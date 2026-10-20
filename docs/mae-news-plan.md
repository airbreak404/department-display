# MAE News: reviewed implementation specification

Reviewed October 20, 2026 against repository baseline `aa5aa01`. This specification supersedes the original Desktop plan. Implementation details and operational commands are in [operations](mae-news-operations.md); actual results and remaining gates are in [validation](mae-news-validation.md).

## Goal and selected defaults

Add up to eight verified MAE news stories to the existing dual-display hallway kiosk using official WMU sources, weekly GitHub Actions ingestion, committed JSON, and explicit GitHub Pages deployment. Automatically publish only strictly validated, relevant stories. Hold uncertain candidates. Social sources are optional additions, not launch dependencies. Keep the existing base deck and kiosk operating configuration reliable through news failures.

No architecture can guarantee that external websites, AI models, network service, or hardware will never fail. The implementation must instead enforce bounded failures, predictable retention, visible diagnostics, and recoverable deployments. A successful job or commit is not successful visible publication.

## Critical changes from the original

- Replace nonexistent `wmich.edu/engineering/news` with verified `wmich.edu/engineer/news`; also discover articles from the MAE homepage.
- Exclude archival ScholarWorks newsletters from live ingestion. The reviewed collection lists newsletters through 2020, not current news.
- Replace retired `gemini-2.0-flash-lite` and deprecated `google-generativeai` with maintained `google-genai` and a configurable supported model, initially `gemini-3.5-flash-lite`.
- Eliminate keyword-only approval when AI fails. Generic WMU/CEAS/engineering terms never establish MAE relevance.
- Replace assumed branch-based auto-publication with explicit Actions deployment. GitHub documents that `GITHUB_TOKEN` commits do not trigger legacy Pages builds; this repository was using legacy `master` root publishing.
- Separate source publication dates, content-change dates, operational attempt reports, and expiry. Old stories must never become new because a fetch succeeded.
- Clone base/fallback data and build generated news slides idempotently. Existing strings are escaped by the renderer: new templates must not escape them twice.
- Add meaningful automated failure tests, real Chromium rendering checks, live-display evidence, rollback, and a 24-hour soak gate.

## Sources and article handling

Use the official CEAS news listing and MAE homepage for discovery. Fetch article pages to verify the headline, date, excerpt, and department relevance. Parse only article body content; exclude navigation, notices, contact sections, related content, and footers. Prefer article-specific structured publication metadata, then verified article selectors. Never infer a publication day from a month-only URL or use fetch time as publication time. Reject future or unverified dates.

Limit discovery/fetch/classification to 100 distinct article candidates per run, prioritizing currently displayed stories and then newly discovered articles. Classify bounded article text rather than unrestricted HTML. Broad terms aid discovery only; publication requires identifiable MAE members, labs, programs, teams, research, or opportunities explicitly applicable to MAE.

Use a shared HTTPS HTTP client with exact publisher host allowlists, public-address resolution checks, TLS verification, 5-second connect and 20-second read timeouts, at most three validated redirects, and a 2 MiB decompressed body limit. Retry transient errors at most twice with bounded backoff/Retry-After. Respect robots restrictions and crawl delays; do not bypass authentication, challenges, or blocks. Keep total run time bounded below the workflow timeout.

Anonymous Instagram/Facebook scraping is disabled. LinkedIn and other social coverage can be added only after verifying a supported or explicitly approved feed, ownership, access terms, dates, maintenance needs, and actual price. No assumed free RSS bridge or unapproved paid infrastructure is required.

Gemini classifies relevance only; source-derived text is displayed. Treat article instructions as untrusted input, use no model tools/URL fetching, and require a strict response with the exact candidate ID, Boolean relevance, and a bounded reason. Invalid output, refusal, model unavailability, auth failure, quota exhaustion, or missing credentials holds new candidates. Previously approved unexpired records may remain. Cache approvals and rejections by content hash, model, and prompt version; changed content is reclassified. Limit generation to 120 requests including retries, and do not automatically enable paid billing.

General stories expire after 180 days. Event announcements are conservatively held until manual review supplies a verified event end date converted from America/New_York to UTC. Do not allow event expiry to exceed general retention. Retain a maximum of eight items, sorted by publication date descending and stable ID. Deduplicate canonical URLs and identical normalized headlines from the same publisher. Strip tracking parameters while preserving meaningful queries.

Manual approvals/corrections and blocked IDs/URLs live in a separate file never overwritten by ingestion. Explicit blocks take precedence. A verified 404 removes an existing story; transient failures do not. Manual event metadata can override an automatic event hold, but never an explicit block or verified removal.

## Public interface and pipeline writes

The public `data/news.json` envelope contains `schemaVersion: 1`, UTC `contentUpdatedAt` or null, and `items`. Each item has exactly `id`, `title`, `url`, `publishedDate`, `summary`, `source`, and UTC `expiresAt`.

Bounds: ID 24 lowercase hexadecimal characters from SHA-256 of canonical URL; title 180 characters; URL 2048; publication date YYYY-MM-DD; excerpt 300; source 80; feed 64 KiB. Strip markup/control characters and reject invalid types. Enforce dates and expiry in Python and browser code. Operational attempt timestamps and model reasons belong in diagnostics/state, not a display update timestamp.

Validate the entire candidate feed before atomic replacement. Preserve byte-identical files and timestamps on no-change runs. Dry runs write only ignored diagnostics. Resolve all repository paths from script location regardless of current working directory. Only feed and classification state may cross into the privileged publishing job. Review/override files and state are excluded from public Pages assets.

Listing failures, parser drift, recognized successful listings, and article failures must be distinguishable. A listing with no recognized links is a parser failure unless there is a source-specific tested empty state. Total primary-source failure fails ingestion and preserves the feed. Partial success may publish verified candidates with explicit warnings. Diagnostics include source status, candidate outcomes, held/rejected/approved counts, model availability, content changes, commit, and deployment results. Retain artifacts for 30 days and redact secrets/raw API exceptions.

## Browser data flow and slide behavior

Fetch base slides and news independently with 10-second abort limits and bounded bodies. Keep the last valid in-memory news on missing, malformed, timed-out, or unsupported feeds, but enforce expiry. A valid empty feed intentionally removes news. Cold offline startup displays the bundled base deck without news. Keep base/fallback objects immutable; repeated polls must not accumulate generated slides.

Prevent overlapping polling. Compare effective deck content, not operational attempt timestamps. Apply running updates at a slide boundary, retain pause state for paused updates, preserve current slide by stable ID when possible, and otherwise choose the next surviving old slide. Maintain one animation/progress loop and countdown interval. Recheck expiry on polls, transitions, and visibility restoration. Never allow a removed/empty news page to cause modulo-zero or out-of-range navigation.

Insert news before the first wayfinding slide. Show three stories per page, at most three pages, for 25 seconds each. Provide deliberate layouts for one, two, and three stories. Use existing brand colors and 2048×1152 reference canvas, source attribution, verified publication dates, constrained excerpts, and text encoded exactly once. Validate URLs separately from text escaping. Avoid UTC date-only parsing shifting displayed calendar days.

Do not add new continuous animation, blur effects, GPU/browser flags, or host configuration changes. The first version omits QR codes and scan instructions because no reliable QR workflow was specified. Emergency `config.newsEnabled=false` suppresses news while retaining the base deck; mirror this setting in bundled fallback data.

## GitHub automation and deployment

Run Mondays 08:17 UTC (03:17 EST / 04:17 EDT), plus manual dispatch with dry-run default. Use Python 3.12, hash-locked runtime/test dependencies, and actions pinned by reviewed full commit SHA. Fetch/classification jobs have contents-read permissions and no stored write credentials. Only the validated publisher gets contents-write. Commit explicit generated paths using local Git identity and normal fast-forward pushes.

Serialize scraper writes without cancelling active writes. If branch state changes during ingestion, fail publication and require a fresh run rather than rebasing stale data or exposing an API key to a privileged write job. This is a deliberate conservative adjustment from the proposed automatic recomputation attempt. Never force push.

Migrate Pages publishing to GitHub Actions. Use one reusable Pages workflow called by both ordinary validated site updates and successful news publication. Pass the exact source revision; reject superseded deployment revisions, serialize deployment jobs, and scope pages-write/id-token-write permissions to deployment only. Package explicit public assets. Verify the deployed public news bytes by SHA-256 with bounded CDN retries. Never rely on bot pushes starting a second workflow.

The repository owner maintains the source adapters, credentials, model access, Actions failures, and monthly schedule-health review. GitHub scheduling has no exact-time guarantee and can disable after 60 days of repository inactivity. Browser expiry remains active even if ingestion stops.

## Verification, rollout, and rollback

Automated checks must cover real saved WMU fixtures, parser drift/challenge pages, missing/future dates, network limits and redirects, private destinations, 404/429/timeouts, partial and total failures, missing/retired models and keys, malformed/refused structured responses, prompt-like article text, caching, manual blocks/corrections, deterministic merge, expiry, atomic writes, and no-change/no-commit behavior.

Browser checks cover counts 0–8, idempotent composition, failed/malformed/missing/empty feeds, offline startup, news-only changes, pause state, deck shrinkage, stable navigation, single timer cleanup, encodings, date stability, and emergency disable behavior. Inspect screenshots at 2048×1152 and 2560×1440 with long headlines/excerpts. Validate GitHub workflow syntax, permissions, output allowlists, explicit deployment, and public hash verification.

Capture baseline real-display screenshots and service counters. Deploy news disabled first and verify the existing presentation. Inspect at least ten dry-run outcomes. Enable a verified seed only after those checks pass. Prove ingestion → commit → public deployment → visible kiosk update, with target latency of one 10-minute poll plus a slide boundary after deployment. Check both displays and preserve human-work behavior. Do not claim physical output from code inspection or CI status alone.

Compare the release with baseline over 24 hours. Reject repeatable new freezing/choppiness, timer/memory accumulation, attributable graphical recovery events, or uncaught errors. If this gate cannot finish during the implementation session, explicitly record it as pending instead of declaring it passed.

Rollback controls: disable scraper, suppress news, restore a verified unexpired feed with durable blocks/corrections, or revert the application release and explicitly deploy. Restoring legacy Pages mode requires disabling bot publication or establishing an alternate explicit deployment path. Preserve evidence and the dated original Desktop plan.

## Evidence and references

Verified repository admin/push access, enabled Actions, default branch master, and initial legacy Pages mode. Live sources returned valid listing/article content. No Gemini key was configured at implementation start. See the validation ledger for current run evidence rather than treating historical host facts as current.

- [Official CEAS news](https://wmich.edu/engineer/news)
- [MAE department](https://wmich.edu/mechanical-aerospace)
- [ScholarWorks archive](https://scholarworks.wmich.edu/mechanical-aerospace_news/)
- [Gemini model lifecycle](https://ai.google.dev/gemini-api/docs/deprecations)
- [Maintained SDK](https://ai.google.dev/gemini-api/docs/libraries)
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [GitHub Pages publishing behavior](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
