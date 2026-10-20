"""Public, credential-free collector health and an independent freshness gate."""
from datetime import datetime, timedelta, timezone
import json
from urllib.request import urlopen

from network import safe_url
from news import instant


def validate(value):
    if (not isinstance(value, dict) or set(value) != {"schemaVersion", "checkedAt", "status", "items",
            "classifierStatus", "automaticRules", "sources", "inventory", "deferred", "socialCoverage"} or
            value["schemaVersion"] != 1 or value["status"] not in {"ok", "partial", "degraded"} or
            type(value["items"]) is not int or not 0 <= value["items"] <= 8 or
            any(type(value[k]) is not int or not 0 <= value[k] <= 1200 for k in ("inventory", "deferred")) or
            not isinstance(value["sources"], list) or len(value["sources"]) > 30):
        raise ValueError("health_schema")
    instant(value["checkedAt"])
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


def check(value, now):
    validate(value)
    checked = instant(value["checkedAt"])
    if checked > now + timedelta(minutes=5) or now - checked > timedelta(hours=18):
        raise ValueError("collector_stale_or_future")
    if not any(s["status"] == "ok" for s in value["sources"]):
        raise ValueError("no_healthy_sources")
    return value


if __name__ == "__main__":
    try:
        with urlopen("https://airbreak404.github.io/department-display/data/news-health.json", timeout=20) as response:
            raw = response.read(32769)
        if len(raw) > 32768:
            raise ValueError("health_size")
        value = check(json.loads(raw), datetime.now(timezone.utc))
        if value["status"] != "ok" or value["items"] < 3:
            print("::warning title=News coverage needs attention::Collector ran, but coverage is reduced. Inspect news diagnostics.")
        print("Collector freshness verified; " + str(value["items"]) + " current feed items.")
    except Exception:
        print("::error title=News collector stale::Public health is unavailable, invalid, or over 18 hours old. Inspect the MAE News Scraper workflow.")
        raise SystemExit(1)
