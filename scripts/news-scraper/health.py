"""Public, credential-free collector health and an independent freshness gate."""
from datetime import datetime, timedelta, timezone
import json
import hashlib
import re
import time
from urllib.request import urlopen

from network import safe_url
from news import instant


def validate(value):
    fields = {"schemaVersion", "checkedAt", "status", "items", "classifierStatus", "automaticRules", "sources", "inventory", "deferred", "socialCoverage"}
    if (not isinstance(value, dict) or not fields <= set(value) or
            set(value) - fields - {"feedSha256", "attempted", "parsed", "articleFailures"} or
            value["schemaVersion"] != 1 or value["status"] not in {"ok", "partial", "degraded"} or
            type(value["items"]) is not int or not 0 <= value["items"] <= 8 or
            any(type(value[k]) is not int or not 0 <= value[k] <= 1200 for k in ("inventory", "deferred")) or
            not isinstance(value["sources"], list) or len(value["sources"]) > 30):
        raise ValueError("health_schema")
    instant(value["checkedAt"])
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


if __name__ == "__main__":
    try:
        # Raw repository health is current even when unchanged display content
        # intentionally skips Pages deployment and its pre-existing reload signal.
        with urlopen("https://raw.githubusercontent.com/airbreak404/department-display/master/data/news-health.json?t=" + str(time.time_ns()), timeout=20) as response:
            raw = response.read(32769)
        if len(raw) > 32768:
            raise ValueError("health_size")
        value = check(json.loads(raw), datetime.now(timezone.utc))
        for attempt in range(3):
            try:
                with urlopen("https://airbreak404.github.io/department-display/data/news.json?t=" + str(time.time_ns()), timeout=20) as response:
                    verify_deployment(value, response.read(65537))
                break
            except (OSError, ValueError):
                if attempt == 2:
                    raise
                time.sleep(10)
        if value["status"] != "ok" or value["items"] < 3:
            print("::warning title=News coverage needs attention::Collector ran, but coverage is reduced. Inspect news diagnostics.")
        print("Collector freshness and public feed hash verified; " + str(value["items"]) + " feed items.")
    except Exception:
        print("::error title=News health failed::Collector health is unavailable, stale, invalid, or its public feed was not deployed. Inspect the MAE News Scraper workflow.")
        raise SystemExit(1)
