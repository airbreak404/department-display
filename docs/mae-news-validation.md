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
