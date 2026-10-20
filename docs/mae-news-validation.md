# MAE news validation ledger

## 2026-10-20 implementation checks

- Source repository started clean at `aa5aa01`; default branch `master`.
- Verified existing Pages mode was legacy publishing from `master` root. Implementation replaces it with explicit Actions deployment.
- Both official source listing endpoints parsed successfully in a live dry run: CEAS news returned 32 links; MAE homepage returned 3.
- Reviewed 10+ discovery outcomes: Lemmer directly identifies MAE; power-systems and chemical-engineering stories require classification rather than generic CEAS approval; alumni ceremony, speaker series, and EcoCAR announcements are conservatively held for event review; old presidential scholars and archived stories expire instead of being made fresh by fetch time.
- First dry run: six eligible candidates held, zero AI approvals, `classifierStatus=missing_key`, no feed mutation and no API calls.
- Manually verified seed: [Lemmer appointment](https://wmich.edu/engineer/news/2026/06/kristina-lemmer-hallquist-endowed-professor), publication June 15, 2026, expiry December 12, 2026. Source headline and excerpt retained. This is a manual approval, not an AI result.
- 16 deterministic Python tests passed, including actual-source extraction, rejection caching, strict model output, expiry, total/partial source failure, network limits, and no-change writes.
- Real Chromium checks passed for item counts 0–8, page grouping, idempotence, encoding, date stability, pause/update behavior, empty feeds, malformed data, fetch failures, and expiry validation.
- Screenshots generated at 2048×1152 and 2560×1440 for one-, two-, three-, and eight-story scenarios; three-card layout inspected visually. Local evidence is in ignored `test-results/`.
- Runtime dependency audit: no known vulnerabilities reported by pip-audit. Hash-locked install resolution checked locally; Linux CI remains a deployment gate.
- Live kiosk address recovered with existing encrypted beacon resolver, SSH host verified. No host launcher/GPU/service configuration changed.
- Pre-deployment baseline at 11:48 EDT: kiosk service active since 05:41 EDT, NRestarts=0, shared Chrome PID 1888, RSS 250344 KiB. Both expected display modes/windows present.
- Baseline physical-window captures: remote `/home/mae-student/.local/state/kiosk/screenshots/tv_20261020_114835.png` and `mac_20261020_114835.png`.

## Gates still outstanding at this checkpoint

- Linux Actions validation and public-feed hash verification.
- Deployment with news disabled, followed by enabled verified seed.
- Real-display screenshots after rollout, news-only refresh, and retained human-work behavior.
- Gemini secret setup, model access/free-tier verification, and a successful live AI classification.
- 24-hour performance/recovery soak. A short smoke test cannot establish this.

See later entries below for evidence gathered after this checkpoint. Do not infer completion from this preliminary ledger.

## Disabled rollout verified

- [Linux CI and first explicit deployment](https://github.com/airbreak404/department-display/actions/runs/39452227838) passed all regression checks and public-feed hash verification.
- Pages mode verified changed from `legacy` to `workflow`.
- Both live browser pages loaded `MaeNews`, retained the original 20 slides, showed `newsEnabled=false`, and continued cycling unpaused. Browser viewport sizes remained 2560×1440 and 2048×1152.
- Existing sync requested a soft reload but the first immediate probe still observed old code. The explicit supported `mae-display reload` command loaded new code on both pages; host services and browser flags were unchanged.
- Pre-change frame median/p95 was approximately 83.3/83.5 ms; with news disabled after implementation, median was approximately 66.7 ms and p95 83.5 ms on the sampled slides. These are short samples, not proof of sustained smoothness.
- Local live ingestion validated both primary sources, held six new AI/event candidates, and produced one manually verified unexpired seed with zero Gemini requests.
- Additional checks cover missing-key fail-closed behavior, strict UTC timestamps, and offline cold startup.

## Enabled release and GitHub ingestion verified

- [Enabled-release Linux checks and deployment](https://github.com/airbreak404/department-display/actions/runs/39452983356) succeeded.
- [First GitHub-hosted ingestion, publication, and explicit deployment](https://github.com/airbreak404/department-display/actions/runs/39453032780) succeeded. Both listings parsed; six candidates held; zero AI approvals and zero API calls; one manually approved story retained. Identical content produced `contentChanged=false` and no new data commit.
- Public feed returned the verified seed; manual override and classification-state paths returned HTTP 404. They were not packaged into Pages.
- Real kiosk pages at both display sizes reported 21 slides, `newsEnabled=true`, one news page, and unpaused cycling. Captured and visually inspected the real rendered news page on each browser. Both layouts contained the correct headline, June 15 publication date, source excerpt, and attribution without overflow.
- Remote physical-window screenshots were captured at 11:59:31/32 EDT. CDP screenshots are also retained under local `scratch/kiosk/`.
- News-page short samples: median ~66.7 ms and p95 ~83.5 ms; no material degradation relative to the short disabled sample. This does not establish sustained smoothness.
- Service remained active with `NRestarts=0`. The existing sync timer's SIGHUP restarted Chrome groups during rollout (PID 65345 afterward); service uptime alone does not prove the browser did not restart. This pre-existing deployment behavior was left unchanged.
- 18 Python tests and real Chromium regressions passed locally and in Linux CI.
- A hidden 24-hour collector started at 11:59:40 EDT (local PID 14080), sampling every five minutes. First enabled sample succeeded with zero collection failures. Evidence: local `scratch/soak/status.json` and `samples.jsonl`. Soak acceptance remains pending.
- A genuine live news-only refresh without document/browser reload is being checked separately; Chromium regression coverage already passes. Do not infer this gate from the initial deployment reload.
