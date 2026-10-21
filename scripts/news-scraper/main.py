"""Run from any working directory. Dry runs write only ignored diagnostics."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime, timedelta, timezone

from classifier import Classifier, MAX_CALLS, MODEL, PROMPT_VERSION
from network import Client, FetchError
from news import ARTICLE_PATH, EVENT_PATH, EVENT_PAGES, source_urls, next_listing, discovery, extract, identity, instant, merge, stamp, validate_feed, validate_item
from events import extract_event
import relevance
import state as cache

ROOT = Path(__file__).resolve().parents[2]


def read(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == payload:
        return False
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                         delete=False) as stream:
            name = stream.name
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)
    return True


def run(root=ROOT, dry_run=False, client=None, classifier=None, now=None):
    now = now or datetime.now(timezone.utc)
    deadline = time.monotonic() + 11 * 60
    report = {"startedAt": stamp(now), "sources": [], "held": 0, "rejected": 0, "approved": 0,
              "candidates": [], "dryRun": dry_run}
    feed_path = root / "data/news.json"
    old = validate_feed(read(feed_path, {"schemaVersion": 1, "contentUpdatedAt": None, "items": []}), now)
    overrides = read(root / "data/news-overrides.json", {"approved": [], "blocked": []})
    if set(overrides) != {"approved", "blocked"} or not all(isinstance(overrides[k], list) for k in overrides):
        raise ValueError("override_schema")
    blocked = set(overrides["blocked"])
    if any(not isinstance(value, str) for value in blocked):
        raise ValueError("override_block_type")
    manual = [validate_item(item, now, allow_expired=True) for item in overrides["approved"]]
    manual_ids = {item["id"] for item in manual}
    state_path = root / "scripts/news-scraper/state.json"
    try:
        state = cache.validate(read(state_path, cache.empty()))
    except (ValueError, TypeError, KeyError):
        state = cache.empty()
        report["cacheRecovered"] = True
    http = client or Client()
    urls = set(state["inventory"]) | {item["url"] for item in old["items"] + manual}
    successes = 0
    sources = source_urls(now)
    for source in sources:
        if time.monotonic() >= deadline:
            report["budgetExceeded"] = True
            break
        try:
            document = http.get(source)
            found = discovery(document, source)
            urls.update(found)
            report["sources"].append({"source": source, "status": "ok", "links": len(found)})
            following = next_listing(document, source)
            from bs4 import BeautifulSoup
            if (BeautifulSoup(document, "html.parser").select_one('.pager a[rel="next"][href]') and
                    (following is None or following not in sources and len(sources) >= 30)):
                report["sources"][-1]["status"] = "pagination_cap"
            if following and following not in sources and len(sources) < 30:
                sources.append(following)
            successes += 1
        except (FetchError, ValueError) as exc:
            report["sources"].append({"source": source, "status": str(exc)})
    if not successes:
        report["status"] = "failed_all_sources"
        atomic(root / "scratch/news/report.json", report)
        return report, 1
    judge = classifier or Classifier()
    report["model"] = MODEL
    policy = hashlib.sha256(json.dumps([MODEL, PROMPT_VERSION, relevance.VERSION]).encode()).hexdigest()
    approved = []
    removed = set()
    # Restartable work: new candidates first, then oldest attempts; displayed stories
    # rechecked daily. Persisted retry backoff prevents a dead URL starving others.
    existing_urls = {item["url"] for item in old["items"]}
    import re
    from urllib.parse import urlsplit
    def priority(url):
        match = re.search(r"/(\d{4})/(\d{2})/", url)
        month = int(match[1]) * 12 + int(match[2]) if match else 0
        entry = state["inventory"].get(url, {})
        previous = entry.get("lastAttempt", "")
        needs_review = entry.get("outcome") == "held" or entry.get("policy") != policy
        important = url in existing_urls or EVENT_PATH.fullmatch(urlsplit(url).path) or url in EVENT_PAGES
        return (not important, bool(previous), not needs_review, previous, -month, url)
    def due(url):
        previous = state["inventory"].get(url)
        return (previous is None or instant(previous["retryAfter"]) <= now or
                previous.get("policy") != policy and previous.get("failures", 0) == 0)
    urls = {u for u in urls if not (m := re.search(r"/(\d{4})/(\d{2})/", u)) or
            (int(m[1]), int(m[2])) >= ((now - timedelta(days=180)).year, (now - timedelta(days=180)).month)}
    report["inventoryTruncated"] = max(0, len(urls) - 1200)
    urls = set(sorted(urls, key=priority)[:1200])
    selected = sorted((u for u in urls if due(u)), key=priority)[:80]
    report["inventory"] = len(urls)
    report["deferred"] = sum(due(u) for u in urls) - len(selected)
    report["rulesApproved"] = 0
    report.update({"attempted": 0, "parsed": 0, "articleFailures": 0})
    for url in selected:
        if time.monotonic() >= deadline:
            report["budgetExceeded"] = True
            break
        candidate_id = identity(url)
        if candidate_id in blocked or url in blocked:
            continue
        report["attempted"] += 1
        previous = state["inventory"].get(url, {})
        entry = state["inventory"][url] = {"lastAttempt": stamp(now), "retryAfter": stamp(now + timedelta(hours=24 if url in existing_urls else 6)), "failures": 0, "policy": policy}
        try:
            document = http.get(url)
            if ARTICLE_PATH.fullmatch(urlsplit(url).path):
                item, body, event = extract(document, url, now)
                if event:
                    item, body = extract_event(document, url, now)
            else:
                item, body = extract_event(document, url, now)
            validate_item(item, now)
        except (FetchError, ValueError) as exc:
            expected_skip = str(exc) in {"expired", "single_structured_event_required", "event_outside_upcoming_window", "no_upcoming_verified_events", "event_cancelled_or_rescheduled"}
            if url in existing_urls and str(exc) == "single_structured_event_required":
                expected_skip = False
            if isinstance(exc, FetchError) or not expected_skip:
                report["articleFailures"] += 1
            failures = min(previous.get("failures", 0) + 1, 10)
            state["inventory"][url].update({"failures": failures,
                "retryAfter": stamp(now + timedelta(hours=min(2 ** failures, 168))),
                "outcome": "skipped" if expected_skip else "failed"})
            if isinstance(exc, FetchError) and exc.kind == "not_found":
                blocked.add(candidate_id)
                removed.add(candidate_id)
            if str(exc) in {"event_outside_upcoming_window", "no_upcoming_verified_events", "event_cancelled_or_rescheduled", "expired"}:
                blocked.add(candidate_id)
                removed.add(candidate_id)  # Verified removal also dominates manual approval.
            report["candidates"].append({"id": candidate_id, "url": url, "status": str(exc)})
            continue
        report["parsed"] += 1
        if candidate_id in manual_ids:
            entry["outcome"] = "approved"
            report["candidates"].append({"id": candidate_id, "url": url, "title": item["title"],
                                         "publishedDate": item["publishedDate"], "status": "manual_approved"})
            continue
        # Cosmetic excerpt changes must not spend the model budget again.
        fingerprint = hashlib.sha256(json.dumps([item["id"], item["title"], body, policy], sort_keys=True).encode()).hexdigest()
        cached = state["decisions"].get(candidate_id, {})
        decision = cached.get("decision") if cached.get("hash") == fingerprint else None
        if decision is None:
            decision = relevance.classify(item, body)
            if decision is None:
                decision = judge.classify(item, body)
            if decision is not None:
                state["decisions"][candidate_id] = {"hash": fingerprint, "decision": decision,
                                                     "expiresAt": item["expiresAt"]}
        status = "held"
        if decision is None:
            report["held"] += 1
        elif decision["relevant"]:
            approved.append(item)
            report["approved"] += 1
            report["rulesApproved"] += int(decision.get("method") == relevance.VERSION)
            status = "approved"
        else:
            blocked.add(candidate_id)
            report["rejected"] += 1
            status = "rejected"
        entry["outcome"] = status
        report["candidates"].append({"id": candidate_id, "url": url, "title": item["title"],
                                     "publishedDate": item["publishedDate"], "status": status,
                                     "reason": (judge.error or ("call_budget_exhausted" if judge.calls >= MAX_CALLS else "no_decision")) if decision is None else decision["reason"]})
    items = merge(old["items"], approved, blocked, now)
    # Manual approval can supply verified event expiry, but cannot override explicit blocks.
    items = merge(items, manual, set(overrides["blocked"]) | removed, now)
    output = {"schemaVersion": 1, "contentUpdatedAt": old["contentUpdatedAt"] if items == old["items"] else stamp(now),
              "items": items}
    validate_feed(output, now)
    report["deferred"] = sum(due(u) for u in urls if identity(u) not in blocked and u not in blocked)
    work = {"pendingClassification": 0, "pendingRetrieval": 0, "unreviewed": 0}
    for url in urls:
        if identity(url) in blocked or url in blocked:
            continue
        entry = state["inventory"].get(url, {})
        outcome = entry.get("outcome")
        if outcome == "failed":
            work["pendingRetrieval"] += 1
        elif not outcome or outcome != "skipped" and entry.get("policy") != policy:
            work["unreviewed"] += 1
        elif outcome == "held":
            work["pendingClassification"] += 1
    report.update(work)
    automation_ready = not report.get("budgetExceeded", False) and not report["inventoryTruncated"]
    classifier_status = judge.error or ("call_budget_exhausted" if judge.calls >= MAX_CALLS and report["held"] else "available")
    parser_degraded = report["articleFailures"] >= 3 and report["articleFailures"] * 4 >= report["attempted"]
    report.update({"status": "degraded" if not automation_ready else
                            "degraded" if judge.error else
                            "partial" if parser_degraded or classifier_status == "call_budget_exhausted" or report["deferred"] or any(work.values()) or len(items) < 3 else
                            "ok" if all(s["status"] == "ok" for s in report["sources"]) else "partial",
                   "classifierStatus": classifier_status, "items": len(items),
                   "automationReady": automation_ready,
                   "manualApproved": sum(item["id"] in manual_ids for item in items),
                   "contentChanged": output != old, "requests": judge.calls})
    report["classificationFailures"] = getattr(judge, "failures", {})
    if judge.error:
        print("::warning title=MAE news coverage reduced::Gemini unavailable; explicit relevance rules remain automatic. Uncertain stories are skipped; inspect diagnostics.")
    if parser_degraded:
        print("::warning title=MAE article intake degraded::At least a quarter of attempted article/event pages failed retrieval or parsing. Retained valid content; inspect candidate diagnostics.")
    if len(items) < 3:
        report["coverageWarning"] = "Fewer than three eligible stories; inspect source health and skipped candidates."
    report["socialCoverage"] = "not_connected: no authorized account access"
    health = {"schemaVersion": 1, "checkedAt": stamp(now), "status": report["status"],
              "items": len(items), "classifierStatus": report["classifierStatus"],
              "automaticRules": relevance.VERSION, "sources": report["sources"],
              "inventory": len(urls), "deferred": report["deferred"],
              **work,
              "attempted": report["attempted"], "parsed": report["parsed"], "articleFailures": report["articleFailures"],
              "feedSha256": hashlib.sha256((json.dumps(output, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest(),
              "socialCoverage": report["socialCoverage"]}
    if not dry_run:
        state["decisions"] = {k: v for k, v in state["decisions"].items()
                              if v.get("expiresAt", "") > stamp(now)}
        state["inventory"] = {u: state["inventory"].get(u, {"lastAttempt": "1970-01-01T00:00:00Z", "retryAfter": "1970-01-01T00:00:00Z", "failures": 0}) for u in sorted(urls)}
        # Validate every output before the first mutation. Publication is isolated
        # in a subsequent job, so an interrupted local write is never deployed.
        cache.validate(state)
        from health import validate as validate_health
        validate_health(health)
        atomic(feed_path, output)
        atomic(state_path, state)
        atomic(root / "data/news-health.json", health)
    atomic(root / "scratch/news/candidate-feed.json", output)
    atomic(root / "scratch/news/report.json", report)
    return report, 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result, status = run(dry_run=args.dry_run)
        print(json.dumps({k: v for k, v in result.items() if k != "candidates"}, indent=2))
        raise SystemExit(status)
    except (ValueError, OSError, KeyError, TypeError):
        print("News ingestion failed validation; public feed was not intentionally replaced.")
        raise SystemExit(1)
