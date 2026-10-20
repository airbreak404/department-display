"""Bounded live key/model check against a positive and negative official article."""
from datetime import datetime, timezone
import json

from classifier import Classifier
from main import ROOT, atomic
from network import Client
from news import extract


def check():
    judge, http = Classifier(), Client()
    cases = [
        ("https://wmich.edu/engineer/news/2026/06/kristina-lemmer-hallquist-endowed-professor", True),
        ("https://wmich.edu/engineer/news/2026/10/hoveida-family-foundation-gift-power-systems", False),
    ]
    results = []
    for url, expected in cases:
        item, content, _ = extract(http.get(url), url, datetime.now(timezone.utc))
        decision = judge.classify(item, content)
        results.append({"url": url, "expectedRelevant": expected, "decision": decision,
                        "passed": decision is not None and decision["relevant"] == expected})
    report = {"mode": "classifier_check", "requests": judge.calls, "classifierStatus": judge.error or "available",
              "classificationFailures": judge.failures, "cases": results,
              "passed": all(r["passed"] for r in results)}
    atomic(ROOT / "scratch/news/report.json", report)
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == '__main__':
    try:
        raise SystemExit(check())
    except Exception:
        print("Classifier check failed; inspect sanitized diagnostics. Public content unchanged.")
        raise SystemExit(1)
