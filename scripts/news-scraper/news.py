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
SOURCES = ("https://wmich.edu/engineer/news", "https://wmich.edu/mechanical-aerospace",
           "https://wmich.edu/engineer", "https://wmich.edu/engineer/events",
           "https://wmich.edu/engineer/custerseries")
EVENT_PATH = re.compile(r"^/engineer/events/[a-z0-9-]+/?$")
EVENT_PAGES = frozenset({"https://wmich.edu/engineer/custerseries",
    "https://wmich.edu/engineering-senior-design", "https://wmich.edu/ieeem/innovationexpo",
    "https://wmich.edu/engineer/resources/career-accelerator"})
ARTICLE_PATH = re.compile(r"^/(?:[a-z][a-z0-9-]*/)?news/\d{4}/\d{2}/[^/]+/?$")
# Generic words such as 'welcomes' and 'registration' also occur in ordinary
# reporting. Only explicit invitations/future hosting make news date-sensitive.
EVENT = re.compile(r"\b(?:will (?:host|hold|honor)|join us|invites? (?:you|students|the public|the community)|to host)\b", re.I)
EVENT_TITLE = re.compile(r"\b(?:events?|speaker series|seminar|workshop|ceremony|career fair|conference)\b", re.I)
ANNOUNCEMENT = re.compile(r"\b(?:upcoming|announced|announces|register now|registration opens|scheduled for)\b", re.I)
DISCOVERY_HINT = re.compile(r"\b(?:engineer\w*|mechanical|aerospace|propulsion|robot\w*|sunseeker|ecocar|bronco racing|baja|aiaa|wali|lemmer|gustafson|fajardo|scholarship\w*|career fair\w*|research opportunit\w*)\b", re.I)


def source_urls(now):
    """Bounded backfill covering the entire 180-day retention window."""
    today = now.astimezone(ZoneInfo("America/New_York")).date()
    earliest = today - timedelta(days=180)
    months = []
    year, month = today.year, today.month
    while (year, month) >= (earliest.year, earliest.month):
        months.append(f"https://wmich.edu/news/{year}/{month:02d}")
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    return list(SOURCES) + ["https://wmich.edu/news/latest"] + months


def next_listing(document, base):
    """Follow only a publisher's explicit same-listing next link, max 3 pages."""
    soup = BeautifulSoup(document, "html.parser")
    link = soup.select_one('.pager a[rel="next"][href]')
    if not link:
        return None
    target = canonical(urljoin(base, link["href"]))
    original, result = urlsplit(base), urlsplit(target)
    query = dict(parse_qsl(result.query))
    if (original.path != result.path or set(query) != {"page"} or query["page"] not in {"1", "2"}):
        return None
    return target


def text(value, limit=None):
    value = BeautifulSoup(str(value), "html.parser").get_text(" ", strip=True)
    value = re.sub(r"[\x00-\x1f\x7f]", " ", html.unescape(value))
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    if limit and len(value) > limit:
        value = value[:limit - 1].rsplit(" ", 1)[0] + "…"
    return value


def excerpt(value, limit=300):
    """Prefer complete source sentences, without rewriting or splitting a word."""
    value = text(value)
    if len(value) <= limit:
        return value
    ends = []
    for match in re.finditer(r'''[.!?][\u201d\u2019"']?(?=\s|$)''', value):
        prefix = value[:match.end()]
        if re.search(r"\b(?:Dr|Mr|Mrs|Ms|Prof|St|Mich|[A-Z])\.$", prefix) or re.search(r"(?:\b[A-Z]\.){2,}$", prefix):
            continue
        if match.end() <= limit:
            ends.append(match.end())
    return value[:ends[-1]].strip() if ends else text(value, limit)


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
    recognized = 0
    if base == "https://wmich.edu/engineer/events":
        targets = set()
        for anchor in area.select('a[href]'):
            try:
                target = canonical(urljoin(base, anchor['href']))
                if target in EVENT_PAGES or EVENT_PATH.fullmatch(urlsplit(target).path):
                    targets.add(target)
            except (FetchError, ValueError):
                continue
        if not targets:
            raise ValueError("event_listing_parser_failure")
        return sorted(targets)
    if base == "https://wmich.edu/engineer/custerseries":
        if not area.select_one('.accordion-item h4'):
            raise ValueError("series_parser_failure")
        return [base]
    for anchor in area.select("a[href]"):
        try:
            url = canonical(urljoin(base, anchor["href"]))
            if ARTICLE_PATH.fullmatch(urlsplit(url).path) or EVENT_PATH.fullmatch(urlsplit(url).path) or url in EVENT_PAGES:
                recognized += 1
                # Monthly archives are the coverage backstop. Keep every article;
                # bounded persistent inventory prevents headline-keyword blind spots.
                links.add(url)
        except (ValueError, FetchError):
            continue
    if not recognized:
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
    # Prefer a self-contained source paragraph that explains the MAE connection,
    # rather than a one-line scene-setting opener in a profile or roundup.
    from relevance import DIRECT, TEAMS
    focus = next((p for p in paragraphs if DIRECT.search(p) or TEAMS.search(p)), paragraphs[0])
    summary = excerpt(focus)
    content = "\n".join(paragraphs)[:12000]
    expiry = datetime.combine(published + timedelta(days=180), time.min, UTC)
    result = {"id": identity(url), "title": title, "url": canonical(url),
              "publishedDate": published.isoformat(), "summary": summary,
              "source": "WMU College of Engineering and Applied Sciences" if urlsplit(url).path.startswith("/engineer/") else
                        "WMU News", "expiresAt": stamp(expiry)}
    # Structured event metadata is authoritative even without invitation copy.
    from events import structured
    invitation = bool(list(structured(soup)) or EVENT.search(title + "\n" + "\n".join(paragraphs[:3])) or
                      EVENT_TITLE.search(title) and ANNOUNCEMENT.search(title + "\n" + paragraphs[0]))
    return result, content, invitation


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
    event = "eventStartsAt" in item
    if event:
        bounds["eventStartsAt"] = 30
    if set(item) != set(bounds):
        raise ValueError("item_fields")
    for field, limit in bounds.items():
        value = item[field]
        if event and field == "publishedDate" and value is None:
            continue
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError("item_bounds")
        if re.search(r"[\x00-\x1f\x7f<>]", value):
            raise ValueError("item_markup")
    if not re.fullmatch(r"[a-f0-9]{24}", item["id"]) or item["id"] != identity(item["url"]):
        raise ValueError("item_identity")
    expiry = instant(item["expiresAt"])
    if event:
        start = instant(item["eventStartsAt"])
        if item["publishedDate"] is not None or expiry != start or start > now + timedelta(days=60):
            raise ValueError("event_dates")
    else:
        published = date.fromisoformat(item["publishedDate"])
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
    def order(value):
        return (0, value["eventStartsAt"], value["id"]) if "eventStartsAt" in value else (1, -date.fromisoformat(value["publishedDate"]).toordinal(), value["id"])
    events = 0
    for item in sorted(by_id.values(), key=order):
        key = (urlsplit(item["url"]).hostname, re.sub(r"\W+", " ", item["title"].casefold()).strip())
        if key not in headlines and ("eventStartsAt" not in item or events < 2):
            chosen.append(item)
            headlines.add(key)
            events += int("eventStartsAt" in item)
    return chosen[:8]
