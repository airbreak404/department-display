"""Pure extraction, validation, expiry and stable feed construction."""
import hashlib
import html
import json
import re
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from network import FetchError, safe_url

UTC = timezone.utc
SOURCES = ("https://wmich.edu/engineer/news", "https://wmich.edu/mechanical-aerospace")
ARTICLE_PATH = re.compile(r"^/(?:engineer/news|news(?:/news)?)/\d{4}/\d{2}/[^/]+/?$")
EVENT = re.compile(r"\b(?:will (?:host|hold|honor|present)|upcoming|register|registration|deadline|join us|takes? place|scheduled|invites?|welcomes?|to host)\b", re.I)


def text(value, limit=None):
    value = BeautifulSoup(str(value), "html.parser").get_text(" ", strip=True)
    value = re.sub(r"[\x00-\x1f\x7f]", " ", html.unescape(value))
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    if limit and len(value) > limit:
        value = value[:limit - 1].rsplit(" ", 1)[0] + "…"
    return value


def canonical(url):
    safe_url(url, resolve=False)
    p = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in ("fbclid", "gclid")]
    return urlunsplit(("https", p.hostname, p.path.rstrip("/") or "/", urlencode(sorted(query)), ""))


def identity(url):
    return hashlib.sha256(canonical(url).encode()).hexdigest()[:24]


def discovery(document, base):
    soup = BeautifulSoup(document, "html.parser")
    area = soup.select_one("main") or soup
    links = set()
    for anchor in area.select("a[href]"):
        try:
            url = canonical(urljoin(base, anchor["href"]))
            if ARTICLE_PATH.fullmatch(urlsplit(url).path):
                links.add(url)
        except (ValueError, FetchError):
            continue
    if not links:
        raise ValueError("listing_parser_failure")
    return sorted(links, reverse=True)


def parse_date(value):
    value = text(value)
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        for fmt in ("%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                pass
    raise ValueError("unverified_date")


def extract(document, url, now):
    soup = BeautifulSoup(document, "html.parser")
    article = soup.select_one("article")
    if not article or not article.select_one("h1"):
        raise ValueError("article_parser_failure")
    title = text(article.select_one("h1").get_text(" ", strip=True), 180)
    date_values = []
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or script.get_text())
            pending = data if isinstance(data, list) else [data]
            while pending:
                obj = pending.pop()
                if isinstance(obj, dict):
                    if obj.get("@type") in ("NewsArticle", "Article", "BlogPosting"):
                        date_values.append(obj.get("datePublished", ""))
                    pending.extend(obj.get("@graph", []))
        except (ValueError, TypeError):
            pass
    for el in soup.select('meta[property="article:published_time"], meta[itemprop="datePublished"]'):
        date_values.append(el.get("content", ""))
    for el in article.select("time, .contact--article .date"):
        date_values.append(el.get("datetime") or el.get_text(" ", strip=True))
    published = None
    for value in date_values:
        try:
            published = parse_date(value)
            break
        except ValueError:
            continue
    if published is None or published > now.astimezone(ZoneInfo("America/New_York")).date():
        raise ValueError("unverified_or_future_date")
    body = article.select_one(".text-paragraph") or article.select_one(".field--name-body")
    if not body:
        raise ValueError("article_body_missing")
    for node in body.select("script, style, nav, aside, figcaption, .contact, .related-content"):
        node.decompose()
    paragraphs = [text(p.get_text(" ", strip=True)) for p in body.select("p")]
    paragraphs = [p for p in paragraphs if p and not p.startswith("For more WMU news")]
    if not paragraphs:
        raise ValueError("article_body_missing")
    summary = text(paragraphs[0], 300)
    content = "\n".join(paragraphs)[:12000]
    expiry = datetime.combine(published + timedelta(days=180), time.min, UTC)
    result = {"id": identity(url), "title": title, "url": canonical(url),
              "publishedDate": published.isoformat(), "summary": summary,
              "source": "WMU News" if urlsplit(url).path.startswith("/news/") else
                        "WMU College of Engineering and Applied Sciences", "expiresAt": stamp(expiry)}
    return result, content, bool(EVENT.search(title + " " + content))


def stamp(value):
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def instant(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise ValueError("utc_timestamp_required")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_item(item, now, allow_expired=False):
    if not isinstance(item, dict):
        raise ValueError("item_type")
    bounds = {"id": 64, "title": 180, "url": 2048, "publishedDate": 10,
              "summary": 300, "source": 80, "expiresAt": 30}
    if set(item) != set(bounds):
        raise ValueError("item_fields")
    for field, limit in bounds.items():
        value = item[field]
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError("item_bounds")
        if re.search(r"[\x00-\x1f\x7f<>]", value):
            raise ValueError("item_markup")
    if not re.fullmatch(r"[a-f0-9]{24}", item["id"]) or item["id"] != identity(item["url"]):
        raise ValueError("item_identity")
    published = date.fromisoformat(item["publishedDate"])
    expiry = instant(item["expiresAt"])
    if (published > now.astimezone(ZoneInfo("America/New_York")).date() or
            expiry <= datetime.combine(published, time.min, UTC) or
            expiry > datetime.combine(published + timedelta(days=181), time.min, UTC)):
        raise ValueError("item_dates")
    if not allow_expired and expiry <= now:
        raise ValueError("expired")
    return dict(item)


def validate_feed(feed, now):
    if (not isinstance(feed, dict) or type(feed.get("schemaVersion")) is not int or
            feed["schemaVersion"] != 1 or not isinstance(feed.get("items"), list) or len(feed["items"]) > 8):
        raise ValueError("feed_schema")
    if feed.get("contentUpdatedAt") is not None:
        instant(feed["contentUpdatedAt"])
    seen = set()
    for item in feed["items"]:
        validate_item(item, now, allow_expired=True)
        if item["id"] in seen:
            raise ValueError("duplicate_id")
        seen.add(item["id"])
    if len(json.dumps(feed, ensure_ascii=False).encode()) > 65536:
        raise ValueError("feed_size")
    return feed


def merge(existing, approved, blocked, now):
    by_id = {}
    for item in existing + approved:
        try:
            value = validate_item(item, now)
            if value["id"] not in blocked and value["url"] not in blocked:
                by_id[value["id"]] = value
        except (ValueError, TypeError, KeyError):
            continue
    chosen, headlines = [], set()
    for item in sorted(by_id.values(), key=lambda x: (-date.fromisoformat(x["publishedDate"]).toordinal(), x["id"])):
        key = (urlsplit(item["url"]).hostname, re.sub(r"\W+", " ", item["title"].casefold()).strip())
        if key not in headlines:
            chosen.append(item)
            headlines.add(key)
    return chosen[:8]
