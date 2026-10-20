"""Validate the private decision cache and bounded, restartable work inventory."""
import re
from network import FetchError
from news import ARTICLE_PATH, EVENT_PATH, EVENT_PAGES, canonical, instant
from urllib.parse import urlsplit


def empty():
    return {"version": 1, "decisions": {}, "inventory": {}}


def validate(value):
    if (not isinstance(value, dict) or value.get("version") != 1 or
            set(value) - {"version", "decisions", "inventory"} or
            not isinstance(value.get("decisions"), dict) or len(value["decisions"]) > 1200 or
            not isinstance(value.get("inventory", {}), dict) or len(value.get("inventory", {})) > 1200):
        raise ValueError("state_schema")
    for key, entry in value["decisions"].items():
        if (not re.fullmatch(r"[a-f0-9]{24}", key) or not isinstance(entry, dict) or
                set(entry) != {"hash", "decision", "expiresAt"} or
                not re.fullmatch(r"[a-f0-9]{64}", entry["hash"])):
            raise ValueError("state_decision")
        instant(entry["expiresAt"])
        d = entry["decision"]
        if (not isinstance(d, dict) or set(d) - {"id", "relevant", "reason", "method"} or
                d.get("id") != key or type(d.get("relevant")) is not bool or
                not isinstance(d.get("reason"), str) or not 1 <= len(d["reason"]) <= 300 or
                not isinstance(d.get("method", "gemini"), str)):
            raise ValueError("state_response")
    for url, entry in value.get("inventory", {}).items():
        try:
            canonical(url)
        except FetchError:
            raise ValueError("state_destination") from None
        if (not (ARTICLE_PATH.fullmatch(urlsplit(url).path) or EVENT_PATH.fullmatch(urlsplit(url).path) or
                 url in EVENT_PAGES) or not isinstance(entry, dict) or
                set(entry) != {"lastAttempt", "retryAfter", "failures"} or
                type(entry["failures"]) is not int or not 0 <= entry["failures"] <= 10):
            raise ValueError("state_inventory")
        instant(entry["lastAttempt"])
        instant(entry["retryAfter"])
    return {**value, "inventory": value.get("inventory", {})}
