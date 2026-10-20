"""Run from any working directory. Dry runs write only ignored diagnostics."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime, timezone

from classifier import Classifier, MODEL, PROMPT_VERSION
from network import Client, FetchError
from news import SOURCES, discovery, extract, identity, merge, stamp, validate_feed, validate_item

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
    state_path = root / "scripts/news-scraper/state.json"
    state = read(state_path, {"version": 1, "decisions": {}})
    if state.get("version") != 1 or not isinstance(state.get("decisions"), dict):
        raise ValueError("state_schema")
    http = client or Client()
    urls = set(item["url"] for item in old["items"])
    successes = 0
    for source in SOURCES:
        try:
            found = discovery(http.get(source), source)
            urls.update(found)
            report["sources"].append({"source": source, "status": "ok", "links": len(found)})
            successes += 1
        except (FetchError, ValueError) as exc:
            report["sources"].append({"source": source, "status": str(exc)})
    if not successes:
        report["status"] = "failed_all_sources"
        atomic(root / "scratch/news/report.json", report)
        return report, 1
    judge = classifier or Classifier()
    report["model"] = MODEL
    approved = []
    removed = set()
    # Recheck displayed stories first, then newest paths. All requests stay bounded.
    existing_urls = {item["url"] for item in old["items"]}
    selected = sorted(urls, key=lambda u: (u not in existing_urls, tuple(-ord(c) for c in u)))[:100]
    for url in selected:
        if time.monotonic() >= deadline:
            report["budgetExceeded"] = True
            break
        candidate_id = identity(url)
        if candidate_id in blocked or url in blocked:
            continue
        try:
            item, body, event = extract(http.get(url), url, now)
            validate_item(item, now)
        except (FetchError, ValueError) as exc:
            if isinstance(exc, FetchError) and exc.kind == "not_found":
                blocked.add(candidate_id)
                removed.add(candidate_id)
            report["candidates"].append({"id": candidate_id, "status": str(exc)})
            continue
        fingerprint = hashlib.sha256(json.dumps([item, body, MODEL, PROMPT_VERSION], sort_keys=True).encode()).hexdigest()
        cached = state["decisions"].get(candidate_id, {})
        decision = cached.get("decision") if cached.get("hash") == fingerprint else None
        if event:
            # Event dates cannot safely be inferred by relevance AI. Use explicit manual metadata.
            report["held"] += 1
            blocked.add(candidate_id)
            report["candidates"].append({"id": candidate_id, "title": item["title"], "status": "event_needs_review"})
            continue
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
            status = "approved"
        else:
            blocked.add(candidate_id)
            report["rejected"] += 1
            status = "rejected"
        report["candidates"].append({"id": candidate_id, "title": item["title"], "status": status})
    items = merge(old["items"], approved, blocked, now)
    # Manual approval can supply verified event expiry, but cannot override explicit blocks.
    items = merge(items, manual, set(overrides["blocked"]) | removed, now)
    output = {"schemaVersion": 1, "contentUpdatedAt": old["contentUpdatedAt"] if items == old["items"] else stamp(now),
              "items": items}
    validate_feed(output, now)
    report.update({"status": "ok" if all(s["status"] == "ok" for s in report["sources"]) else "partial",
                   "classifierStatus": judge.error or "available", "items": len(items),
                   "contentChanged": output != old, "requests": judge.calls})
    if not dry_run:
        atomic(feed_path, output)
        state["decisions"] = {k: v for k, v in state["decisions"].items()
                              if v.get("expiresAt", "") > stamp(now)}
        atomic(state_path, state)
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
