# MAE news operations

The news feed uses official WMU article text, verified publication dates, explicit expiry, and strict relevance classification. No external API or secret is used by the kiosk. News is optional: the base presentation works without it.

## Setup and schedule

Repository: `airbreak404/department-display`; default branch: `master`. Pages must use **GitHub Actions**, not legacy branch publishing. `site.yml` validates ordinary updates and calls the same deployment workflow used by the scraper. The deployment explicitly packages public assets and checks the public feed's SHA-256 after publishing. Bot commits alone cannot trigger a legacy Pages build.

The scraper runs Mondays at **08:17 UTC** (03:17 EST / 04:17 EDT), plus manual dispatch. GitHub schedules are best effort, can be delayed, and may disable after 60 days of repository inactivity. The repository owner is the operator and must review Actions at least monthly. Enable GitHub Actions failure notifications in your account settings.

Store a Gemini key as repository secret **GEMINI_API_KEY** using GitHub Settings → Secrets and variables → Actions, or `gh secret set GEMINI_API_KEY -R airbreak404/department-display` (interactive input; never place the key in a command, file, issue, or log). `GEMINI_MODEL` is an optional repository variable, default `gemini-3.5-flash-lite`. Verify access and current free-tier eligibility before enabling it. Do not enable billing automatically. Only public article text is sent; free-tier data may be used by Google's service under its terms. No confidential material is supported.

Without a working key, new AI candidates are held. Previously approved unexpired items and manually verified overrides remain eligible. The run summary reports `status=degraded`, `automationReady=false`, and `missing_key` or API failure, and emits an Actions warning. A green publication job does not prove AI ingestion is enabled. Manual approvals are counted separately and do not consume AI requests.

Discovery covers the CEAS listing, MAE homepage, WMU latest news, and each monthly WMU news archive intersecting the 180-day retention window. Explicit same-listing next links are followed for up to three pages per listing, with at most 30 listing pages and 100 article candidates per run. The broad university listings use engineering/team/scholarship/career hints in headlines and teasers for discovery only; they never approve publication. Dated articles from other official WMU departments are supported. Existing stories and newer article months receive priority. These bounded sources improve coverage; they do not guarantee eight publishable stories.

Instagram, LinkedIn, Facebook, and ScholarWorks ingestion are disabled. Add a source only after verifying its current endpoint, access terms, actual cost, and dated article metadata. Never bypass authentication or anti-bot controls. ScholarWorks' reviewed MAE collection lists archival 2016–2020 newsletters and is unsuitable as a live-news source.

## Manual verification and corrections

`data/news-overrides.json` contains `approved` records and `blocked` IDs or canonical URLs. Overrides are reviewed inputs, never overwritten by the scraper, and are excluded from Pages. A verified initial MAE story may be supplied here; this is distinct from AI classification. Every record has exactly:

```json
{
  "id": "24 lowercase hex characters derived from SHA-256 of canonical URL",
  "title": "Source headline, at most 180 characters",
  "url": "https://wmich.edu/engineer/news/YYYY/MM/article",
  "publishedDate": "YYYY-MM-DD",
  "summary": "Source excerpt, at most 300 characters",
  "source": "Publisher name, at most 80 characters",
  "expiresAt": "YYYY-MM-DDTHH:MM:SSZ"
}
```

Use the scraper's `identity(url)` helper to compute the ID. Copy the article headline/excerpt; verify actual publication metadata inside the article. Do not infer an exact day from its URL. General news expires after 180 days. Events are held for manual review: provide a verified event end converted from `America/New_York` to UTC, never later than the retention cap. When only a verified start is supplied, conservatively expire the invitation **at that start**, without inventing an end time. An unverified event date must not be approved. A multiyear program's future technical presentations alone do not make its launch news a dated invitation. Client and pipeline enforce expiry even if Actions stops. Expired overrides may remain as an audit record but will not display.

Block a bad story by adding its ID/URL to `blocked`, run ingestion with `dry_run=false`, and verify public deployment. A block overrides approvals. Removing a manual approval alone does not retract a story already in the merged feed: **add a block**. For urgent suppression set `config.newsEnabled` to `false` in both `data/slides.json` and `data/fallback.js`, then deploy. Do not manually edit generated news as the durable correction mechanism.

## Run and inspect

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r scripts/news-scraper/requirements-test.txt
.\.venv\Scripts\python.exe scripts/news-scraper/main.py --dry-run
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
.\.venv\Scripts\python.exe tests/browser_news.py
gh workflow run news-scraper.yml -R airbreak404/department-display -f dry_run=true
```

Linux: use `.venv/bin/python` instead of the Windows executable. Scripts resolve repository paths independently of the shell's working directory. Browser checks require `python -m playwright install chromium`; CI installs Chromium and OS dependencies automatically.

Dry runs write only ignored `scratch/news/` evidence and do not modify feed/cache. Review at least ten discovery outcomes, including unrelated CEAS stories, before the first live ingestion. Enable writes by manually dispatching with `dry_run=false`. Inspect source, classification, commit, deploy, and public verification as separate stages. Diagnostics remain in Actions artifacts for 30 days. Reports contain no keys or raw API exceptions. Classification state is committed for reuse but excluded from public Pages assets.

Total primary-source failure leaves the feed unchanged and fails the run. Partial success publishes valid candidates with explicit warnings. A valid empty feed removes news; a failed browser fetch retains unexpired in-memory news. Cold offline startup uses the bundled base deck with no news. Model failures never approve broad keywords. Undated and ambiguous event stories stay held. Crawl permissions, HTTPS host restrictions, redirects, byte limits, timeouts, and run budgets are enforced.

Concurrent code changes invalidate an ingestion snapshot: publication fails rather than rebasing stale generated results. Rerun the scraper from latest `master`. No force push or write-token exposure to the classifier is needed. Deployments serialize and reject revisions superseded while the artifact was built. If a later commit supersedes a running deployment, its own validated deployment must complete; rerun the site workflow if needed.

## Rollback and acceptance

Disable the scraper workflow to stop ingestion. To roll back UI/code, revert the release commit and explicitly run `site.yml`. To roll back data, restore a known-good **unexpired** feed, apply durable blocks/corrections, and deploy. If migrating Pages back to legacy mode, first disable scraper publishing or supply another explicit deployment path; bot commits will not update legacy Pages.

Before rollout retain baseline screenshots and host status. Deploy with news disabled first, verify the base deck, then enable a verified seed. Check visible news on both real displays and news-only updates without a browser restart; the target is one 10-minute content poll plus a slide boundary after public deployment. Keep existing TV/workstation control behavior, launcher settings, and GPU flags unchanged.

The final release gate is a 24-hour comparison with the pre-change baseline: no repeatable new freezing/choppiness, accumulating timers/memory, attributable graphical recovery events, or uncaught JavaScript errors. Screenshots and green workflows do not establish physical display quality or soak completion. Record outstanding gates in `docs/mae-news-validation.md`.

`scripts/news-scraper/soak.py --hours 24` collects bounded, read-only browser/host evidence every five minutes into ignored `scratch/soak/`. It uses existing SSH credentials and a loopback-only CDP tunnel; it never changes host/browser settings. Inspect `status.json` and `samples.jsonl` after completion. Collection success is not visual-smoothness acceptance. `kiosk_probe.py --frames --capture` provides short frame samples and screenshots over the same tunnel; `--show-news` selects a news slide for rollout inspection without changing pause/fullscreen settings.

## Dependency maintenance

Runtime and test requirements are hash-locked; actions are pinned by full commit SHA. Re-resolve on Python 3.12 with pip-tools, then test on Linux CI and audit before committing. Free-tier availability, model support, source layouts, and GitHub policies can change: verify them during maintenance rather than silently swapping models or adding paid services.

References: [Gemini lifecycle](https://ai.google.dev/gemini-api/docs/deprecations), [SDK](https://ai.google.dev/gemini-api/docs/libraries), [pricing](https://ai.google.dev/gemini-api/docs/pricing), [GitHub Pages publishing](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
