# MAE news operations

The news feed uses official WMU article text, verified publication dates, explicit expiry, and strict relevance classification. No external API or secret is used by the kiosk. News is optional: the base presentation works without it.

## Setup and schedule

Repository: `airbreak404/department-display`; default branch: `master`. Pages must use **GitHub Actions**, not legacy branch publishing. `site.yml` validates ordinary updates and calls the same deployment workflow used by the scraper. The deployment explicitly packages public assets and checks the public feed's SHA-256 after publishing. Bot commits alone cannot trigger a legacy Pages build.

The scraper collects daily at **02:17, 08:17, 14:17 and 20:17 UTC**, plus manual dispatch. The separate News collector freshness workflow checks at 03:47, 09:47, 15:47 and 21:47 UTC; it fails when public health is unavailable, invalid or over 18 hours old. GitHub schedules are best effort and may disable after inactivity. Both workflows share that platform. Enable Actions failure notifications and check schedule health monthly. No routine story approval is required.

Store a Gemini key as repository secret **GEMINI_API_KEY** using GitHub Settings → Secrets and variables → Actions, or `gh secret set GEMINI_API_KEY -R airbreak404/department-display` (interactive input; never place the key in a command, file, issue, or log). `GEMINI_MODEL` is an optional repository variable, default `gemini-3.5-flash-lite`. Verify access and current free-tier eligibility before enabling it. Do not enable billing automatically. Only public article text is sent; free-tier data may be used by Google's service under its terms. No confidential material is supported.

The owner saved the Actions secret on October 20. To meet the no-paid-services requirement, keep Google project billing disabled; the workflow cannot determine billing status from the key. Only explicitly allowlisted free-tier text models are accepted. At most 20 generation calls run, at least 6.1 seconds apart. Quota/auth/model failures stop API calls. There is no paid-model fallback or search grounding.

On October 21 the owner supplied an AI Studio screenshot showing **Free tier** and **Set up billing** for the display project. This verifies the visible account setting at that time; no key details were copied. Future account changes still require owner verification. The application never enables billing.

Narrow offline rules approve explicit WMU MAE affiliations, identifiable student teams and inclusive official CEAS opportunities automatically. Gemini handles ambiguous relevance. API failures skip uncertain candidates and reduce coverage, while rules continue automatically. Cached approvals/rejections are tied to content, model, prompt and rules version. Invalid private cache data recovers safely. A green workflow does not establish full coverage: inspect `classifierStatus`, source outcomes and deferrals.

Discovery covers CEAS news/homepage/events, MAE homepage, latest WMU news and all archive months intersecting 180 days. Every dated archive link is considered, including headlines without engineering keywords. Follow at most three pages per listing, 30 listing pages total; expose caps. Persistent inventory holds up to 1,200 URLs, with at most 80 due fetches per run. Displayed items/events get priority, then new candidates and oldest attempts. Recheck displayed stories daily, ordinary candidates after six hours; errors back off from two hours to seven days. Deferrals are explicit and resume later.

`deferred` counts remaining immediately due work, not unresolved classifications. Inspect `pendingClassification`, `pendingRetrieval` and `unreviewed` in collector health and reports as well. Pending decisions persist across runs; changed model/prompt/rules policies revalidate successful inventory without waiting a day. Legacy entries remain unreviewed until visited; failed fetches retain their backoff. Cosmetic excerpt changes alone do not invalidate relevance decisions. Low item count and unresolved work keep coverage partial.

Events require matching structured metadata with a zoned start or the tested Custer adapter with explicit year and matching weekday/date. They enter within 60 days and expire at their start. `publishedDate` is null and `eventStartsAt` supplies the displayed Eastern date/time; retrieval time is never used as publication time. At most two events precede general news in the eight-item feed. `data/news-health.json` tracks collector age independently of content age, without private decisions or credentials.

Read current health from [the raw repository record](https://raw.githubusercontent.com/airbreak404/department-display/master/data/news-health.json), rather than a previous Pages deployment. Its expected feed hash is checked against the public display feed. Collector state/health changes alone skip Pages deployment, preventing unnecessary browser restart signals from the existing host sync. Both publication age and actual public feed bytes are monitored. This repository is public; state is excluded from Pages but is not confidential storage.

Every displayed item has its own locally generated QR code opening that exact source URL. Future social posts use their original post URLs when connected. Black/white 224px symbols include quiet borders; generation is cached and has no QR-service request or paid dependency. Department wayfinding uses the same local encoder. The MIT-licensed vendor build is hash-pinned and independently decoded in Chromium screenshot tests at both screen sizes. Phone scanning under actual lighting and distance remains part of physical review.

The collector's immutable output artifact must pass a separate read-only validation/QR job before publication gets write access. It uses the exact source revision, no API key and no persisted checkout credentials. Any malformed output or unreadable/wrong QR stops publication. An article-parser outage is detected independently of successful index pages; partial failure ratios produce warnings and total article intake failure makes the health check fail.

Every real candidate must have exactly one rendered QR at both screen sizes; missing codes cannot silently escape a decoding loop. If the kiosk encoder fails, inaccessible news rows are omitted and the base deck continues. Publisher validation prevents that candidate feed from becoming the normal release. Health retrieval retries transient network failures; failure logs retain bounded categories such as `health_fetch:network_error`, `health_validation:collector_stale_or_future` and `public_feed:public_feed_mismatch`, never raw exception bodies.

Direct Instagram, LinkedIn and Facebook collection is **not connected**. The official accounts are confirmed but the user has no admin access. See [social access](mae-news-social-access.md). Do not bypass controls, purchase RSS bridges or claim unverified social ingestion. ScholarWorks lists archival 2016-2020 newsletters and remains unsuitable for current news.

## Manual verification and corrections

`data/news-overrides.json` contains optional emergency `approved` records and `blocked` IDs or canonical URLs. It is never overwritten by the scraper and is excluded from Pages. Normal operation uses empty approvals. A general news correction has exactly:

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

Use the scraper's `identity(url)` helper to compute the ID. Copy the article headline/excerpt; verify actual publication metadata inside the article. Do not infer an exact day from its URL. General news expires after 180 days. Events publish automatically only with verified metadata; an emergency event override uses `publishedDate: null` and identical verified `eventStartsAt`/`expiresAt` UTC start timestamps. No invented end time is accepted. An unverified event date must not be approved. Ordinary reporting containing words such as "welcomes" or "registration" remains news; explicit invitations and structured events require verified dates. Parser failures retain valid unexpired items; verified cancellation, expiration, deletion and explicit rejection remove them. Client expiry remains active even if Actions stops.

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

`scripts/news-scraper/soak.py --hours 24` creates a new timestamped directory inside ignored `scratch/`, with release/dirty-state manifest, status and samples. `--output scratch/unique-name` selects a new directory; existing evidence is never overwritten. Its dedicated tunnel defaults to loopback port **19223** so the older collector on 19222 can finish independently. `--port` can select another loopback port. No host/browser settings change.

Inspect `collectionFailures` separately from `observationFailures`. Checks include both expected display sizes, unpaused visible playback, slide progression, expected news, JavaScript counters, asset version, browser reloads, boot identity, service restart and crash evidence. `no_issues_observed` means only that the sampled signals passed; physical smoothness is always marked `required`. Deliberate maintenance/reloads require explanation and must not be silently counted as clean uptime. `kiosk_probe.py --port 19223 --frames --capture` reads short frame samples and screenshots through the new tunnel; `--show-news` temporarily selects news without changing pause/fullscreen state. Five-minute observations cannot detect every brief rendering problem.

## Dependency maintenance

Runtime and test requirements are hash-locked; actions are pinned by full commit SHA. Re-resolve on Python 3.12 with pip-tools, then test on Linux CI and audit before committing. Free-tier availability, model support, source layouts, and GitHub policies can change: verify them during maintenance rather than silently swapping models or adding paid services.

References: [Gemini lifecycle](https://ai.google.dev/gemini-api/docs/deprecations), [SDK](https://ai.google.dev/gemini-api/docs/libraries), [pricing](https://ai.google.dev/gemini-api/docs/pricing), [GitHub Pages publishing](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
