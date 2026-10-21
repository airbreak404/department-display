"""Public, credential-free collector health and an independent freshness gate."""
from datetime import datetime, timedelta, timezone
import json
import hashlib
import re
import time
from urllib.request import urlopen
from urllib.error import HTTPError

from network import safe_url
from news import instant


def validate(value):
    fields = {"schemaVersion", "checkedAt", "status", "items", "classifierStatus", "automaticRules", "sources", "inventory", "deferred", "socialCoverage"}
    if (not isinstance(value, dict) or not fields <= set(value) or
            set(value) - fields - {"feedSha256", "attempted", "parsed", "articleFailures", "pendingClassification", "pendingRetrieval", "unreviewed"} or
            value["schemaVersion"] != 1 or value["status"] not in {"ok", "partial", "degraded"} or
            type(value["items"]) is not int or not 0 <= value["items"] <= 8 or
            any(type(value[k]) is not int or not 0 <= value[k] <= 1200 for k in ("inventory", "deferred")) or
            not isinstance(value["sources"], list) or len(value["sources"]) > 30):
        raise ValueError("health_schema")
    instant(value["checkedAt"])
    for key in ("pendingClassification", "pendingRetrieval", "unreviewed"):
        if key in value and (type(value[key]) is not int or not 0 <= value[key] <= value["inventory"]):
            raise ValueError("health_work_counts")
    for key in ("attempted", "parsed", "articleFailures"):
        if key in value and (type(value[key]) is not int or not 0 <= value[key] <= 80):
            raise ValueError("health_intake_counts")
    metrics = {"attempted", "parsed", "articleFailures"} & set(value)
    if metrics and (len(metrics) != 3 or value["parsed"] + value["articleFailures"] > value["attempted"]):
        raise ValueError("health_intake_consistency")
    if "feedSha256" in value and (not isinstance(value["feedSha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", value["feedSha256"])):
        raise ValueError("health_hash")
    for key in ("classifierStatus", "automaticRules", "socialCoverage"):
        if not isinstance(value[key], str) or not 1 <= len(value[key]) <= 100:
            raise ValueError("health_bounds")
    for source in value["sources"]:
        if not isinstance(source, dict) or set(source) not in ({"source", "status"}, {"source", "status", "links"}):
            raise ValueError("health_source")
        safe_url(source["source"], resolve=False)
        if not isinstance(source["status"], str) or len(source["status"]) > 80:
            raise ValueError("health_status")
    return value


def verify_deployment(value, payload):
    if len(payload) > 65536 or hashlib.sha256(payload).hexdigest() != value.get("feedSha256"):
        raise ValueError("public_feed_mismatch")


def check(value, now):
    validate(value)
    checked = instant(value["checkedAt"])
    if checked > now + timedelta(minutes=5) or now - checked > timedelta(hours=18):
        raise ValueError("collector_stale_or_future")
    if not any(s["status"] == "ok" for s in value["sources"]):
        raise ValueError("no_healthy_sources")
    if value.get("attempted", 0) >= 3 and value.get("parsed", 0) == 0 and value.get("articleFailures", 0) >= 3:
        raise ValueError("article_intake_outage")
    return value


class HealthFailure(Exception):
    """Only a bounded category may reach an Actions log, never exception bodies."""


def fetch_bytes(url, limit):
    with urlopen(url + "?t=" + str(time.time_ns()), timeout=20) as response:
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("response_size")
    return raw


def monitor(fetch=fetch_bytes, sleep=time.sleep, now=None):
    stage = "health_fetch"
    try:
        raw = None
        for attempt in range(3):
            try:
                raw = fetch("https://raw.githubusercontent.com/airbreak404/department-display/master/data/news-health.json", 32768)
                break
            except OSError as exc:
                if isinstance(exc, HTTPError) and exc.code not in {429, 500, 502, 503, 504} or attempt == 2:
                    raise
                sleep(2 ** attempt)
        stage = "health_validation"
        value = check(json.loads(raw), now or datetime.now(timezone.utc))
        stage = "public_feed"
        for attempt in range(3):
            try:
                verify_deployment(value, fetch("https://airbreak404.github.io/department-display/data/news.json", 65536))
                return value
            except (OSError, ValueError):
                if attempt == 2:
                    raise
                sleep(10)
    except Exception as exc:
        if isinstance(exc, HTTPError):
            category = "http_" + str(exc.code) if type(exc.code) is int and 100 <= exc.code <= 599 else "http_error"
        elif isinstance(exc, json.JSONDecodeError):
            category = "invalid_json"
        elif isinstance(exc, ValueError):
            known = {"collector_stale_or_future", "no_healthy_sources", "article_intake_outage", "public_feed_mismatch", "response_size"}
            category = str(exc) if str(exc) in known else "invalid_schema"
        elif isinstance(exc, OSError):
            category = "network_error"
        else:
            category = "unexpected_error"
        raise HealthFailure(stage + ":" + category) from None


if __name__ == "__main__":
    try:
        value = monitor()
        if value["status"] != "ok" or value["items"] < 3 or any(value.get(k, 0) for k in ("pendingClassification", "pendingRetrieval", "unreviewed")):
            print("::warning title=News coverage needs attention::Collector ran, but coverage is reduced. Inspect news diagnostics.")
        print("Collector freshness and public feed hash verified; " + str(value["items"]) + " feed items.")
    except HealthFailure as exc:
        print("::error title=News health failed::" + str(exc) + ". Inspect the MAE News Scraper workflow.")
        raise SystemExit(1)
