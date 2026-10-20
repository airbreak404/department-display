# MAE News: reviewed implementation specification

Reviewed October 20, 2026 against repository baseline `aa5aa01`. This specification supersedes the original Desktop plan. Implementation details and operational commands are in [operations](mae-news-operations.md); actual results and remaining gates are in [validation](mae-news-validation.md).

Expanded automation: see [remaining work](mae-news-remaining-work.md). The user selected MAE stories plus engineering opportunities available to MAE students, no paid services, and no routine manual curation. Official CEAS social accounts are confirmed but direct social ingestion requires access the user does not currently have. That gap must remain visible. The collector now includes official events, persistent inventory, offline relevance rules, optional Gemini classification, and independent health checks.

## Goal and selected defaults

Add up to eight verified MAE stories and engineering opportunities to the existing dual-display hallway kiosk using official WMU sources, four daily GitHub Actions collections, committed JSON, and explicit GitHub Pages deployment. Automatically publish strictly validated, relevant items. Skip uncertain candidates and retry later; no routine human approval queue. Social coverage is an explicit access-dependent gap. Keep the existing base deck and kiosk operating configuration reliable through news failures.

No architecture can guarantee that external websites, AI models, network service, or hardware will never fail. The implementation must instead enforce bounded failures, predictable retention, visible diagnostics, and recoverable deployments. A successful job or commit is not successful visible publication.

## Critical changes from the original

- Replace nonexistent `wmich.edu/engineering/news` with verified `wmich.edu/engineer/news`; also discover articles from the MAE homepage.
- Exclude archival ScholarWorks newsletters from live ingestion. The reviewed collection lists newsletters through 2020, not current news.
- Replace retired `gemini-2.0-flash-lite` and deprecated `google-generativeai` with maintained `google-genai` and a configurable supported model, initially `gemini-3.5-flash-lite`.
- Eliminate broad keyword-only approval. Narrow offline rules require local MAE affiliation, a named WMU engineering team, or an inclusive CEAS opportunity. Ambiguous candidates may use Gemini. Generic WMU/CEAS/engineering terms never establish MAE relevance.
- Replace assumed branch-based auto-publication with explicit Actions deployment. GitHub documents that `GITHUB_TOKEN` commits do not trigger legacy Pages builds; this repository was using legacy `master` root publishing.
- Separate source publication dates, content-change dates, operational attempt reports, and expiry. Old stories must never become new because a fetch succeeded.
- Clone base/fallback data and build generated news slides idempotently. Existing strings are escaped by the renderer: new templates must not escape them twice.
- Add meaningful automated failure tests, real Chromium rendering checks, live-display evidence, rollback, and a 24-hour soak gate.

## Sources and article handling

Use the official CEAS news listing and MAE homepage for discovery. Fetch article pages to verify the headline, date, excerpt, and department relevance. Parse only article body content; exclude navigation, notices, contact sections, related content, and footers. Prefer article-specific structured publication metadata, then verified article selectors. Never infer a publication day from a month-only URL or use fetch time as publication time. Reject future or unverified dates.

Maintain up to 1,200 canonical candidate URLs across restarts; fetch at most 80 due pages per run. Prioritize displayed stories and event pages, then unattempted/newer material and oldest attempts. Consider every dated monthly-archive link, so headlines without MAE keywords are not silently excluded. Follow at most three pages per listing and 30 listing pages total; expose pagination caps, inventory truncation, and deferrals. Recheck displayed items daily and ordinary candidates after six hours; errors receive bounded two-hour to seven-day backoff. Classify bounded article text rather than unrestricted HTML. Publication requires identifiable WMU MAE people/programs/teams or opportunities applicable to those students.

Use a shared HTTPS HTTP client with exact publisher host allowlists, public-address resolution checks, TLS verification, 5-second connect and 20-second read timeouts, at most three validated redirects, and a 2 MiB decompressed body limit. Retry transient errors at most twice with bounded backoff/Retry-After. Respect robots restrictions and crawl delays; do not bypass authentication, challenges, or blocks. Keep total run time bounded below the workflow timeout.

Anonymous Instagram/Facebook scraping is disabled. LinkedIn and other social coverage can be added only after verifying a supported or explicitly approved feed, ownership, access terms, dates, maintenance needs, and actual price. No assumed free RSS bridge or unapproved paid infrastructure is required.

Gemini classifies relevance only; source-derived text is displayed. Treat article instructions as untrusted input, use no model tools/URL fetching, and require a strict response with the exact candidate ID, Boolean relevance, and a bounded reason. Invalid output, refusal, model unavailability, auth failure, quota exhaustion, or missing credentials skips uncertain candidates; explicit offline rules remain automatic. Previously approved unexpired records may remain. Cache approvals and rejections by content, model, prompt and rules version. Allow only explicitly listed free-tier text models, at most 20 generation calls including retries, paced at least 6.1 seconds apart. Stop on quota/auth/model failures; never enable grounding or switch to a paid model. The owner must use a project with billing disabled: a key alone does not establish billing status.

General stories expire after 180 days. Events require one matching structured Event with explicit zoned start time, or the tested official Custer adapter with explicit semester/year, matching weekday/date, and Eastern time. Never ask AI to infer dates. Skip cancelled/rescheduled, ambiguous, past or more-than-60-day-away events. Expire at the verified start, conservatively even when an end exists. Advance the Custer URL to its next verified talk. Retain at most eight items: at most two events first by start, then news by publication date descending and stable ID. Deduplicate canonical URLs and identical normalized headlines from the same publisher. Strip tracking parameters while preserving meaningful queries.

Optional emergency approvals/corrections and blocked IDs/URLs live in a separate file never overwritten by ingestion. Explicit blocks take precedence. A verified 404 removes an existing story; transient failures do not. Normal operation must work with empty approvals. Corrections cannot override an explicit block or verified removal.

## Public interface and pipeline writes

The public `data/news.json` envelope contains `schemaVersion: 1`, UTC `contentUpdatedAt` or null, and `items`. General news items have exactly `id`, `title`, `url`, `publishedDate`, `summary`, `source`, and UTC `expiresAt`. The additive event variant also has UTC `eventStartsAt`, sets `publishedDate` to null, and requires expiry equal to that verified start. Older browser code safely drops event records until the application refreshes. Never substitute retrieval time for a missing publication date.

Bounds: ID 24 lowercase hexadecimal characters from SHA-256 of canonical URL; title 180 characters; URL 2048; publication date YYYY-MM-DD; excerpt 300; source 80; feed 64 KiB. Strip markup/control characters and reject invalid types. Enforce dates and expiry in Python and browser code. Operational attempt timestamps and model reasons belong in diagnostics/state, not a display update timestamp.

Validate the entire candidate feed before atomic replacement. Preserve byte-identical files and timestamps on no-change runs. Dry runs write only ignored diagnostics. Resolve all repository paths from script location regardless of current working directory. Only the validated feed, private decision/inventory state, and credential-free public health record may cross into the privileged publishing job. Validate all outputs before writing. Review/override files and state are excluded from public Pages assets.

Listing failures, parser drift, recognized successful listings, and article failures must be distinguishable. A listing with no recognized links is a parser failure unless there is a source-specific tested empty state. Total primary-source failure fails ingestion and preserves the feed. Partial success may publish verified candidates with explicit warnings. Diagnostics include source status, candidate outcomes, held/rejected/approved counts, model availability, content changes, commit, and deployment results. Retain artifacts for 30 days and redact secrets/raw API exceptions.

## Browser data flow and slide behavior

Fetch base slides and news independently with 10-second abort limits and bounded bodies. Keep the last valid in-memory news on missing, malformed, timed-out, or unsupported feeds, but enforce expiry. A valid empty feed intentionally removes news. Cold offline startup displays the bundled base deck without news. Keep base/fallback objects immutable; repeated polls must not accumulate generated slides.

Prevent overlapping polling. Compare effective deck content, not operational attempt timestamps. Apply running updates at a slide boundary, retain pause state for paused updates, preserve current slide by stable ID when possible, and otherwise choose the next surviving old slide. Maintain one animation/progress loop and countdown interval. Recheck expiry on polls, transitions, and visibility restoration. Never allow a removed/empty news page to cause modulo-zero or out-of-range navigation.

Insert news before the first wayfinding slide. Show three stories per page, at most three pages, for 25 seconds each. Provide deliberate layouts for one, two, and three stories. Use existing brand colors and 2048×1152 reference canvas, source attribution, verified publication dates, constrained excerpts, and text encoded exactly once. Validate URLs separately from text escaping. Avoid UTC date-only parsing shifting displayed calendar days.

Use flat editorial rows, thin separators and one News & Opportunities heading. Remove redundant department badges and rounded cards. Display source headlines and excerpts without generated promotional copy. Deterministic presentation cleanup removes Kalamazoo datelines and replaces em/en dashes with commas, preserving original feed text. Event metadata shows Eastern start date/time and zone. Prefer a source paragraph that explains the MAE connection over a short scene-setting opener.

Do not add new continuous animation, blur effects, GPU/browser flags, or host configuration changes. Each news/event row must include a QR code for that exact item URL, as requested by the user. Future connected social items must link to the original post, not an account homepage. Generate codes locally with the pinned MIT-licensed Nayuki encoder, black on white, medium error correction and a four-module quiet border. Use 224px codes at the reference canvas, with Read full story or View event labels. Independently decode rendered screenshots at both target screen sizes and compare decoded destinations with the original unescaped URLs, including query strings. Cache a bounded number of generated SVGs and never run QR encoding on animation frames. The department gateway also uses local generation; no external QR API is required. Emergency `config.newsEnabled=false` suppresses news while retaining the base deck; mirror this setting in bundled fallback data.

## GitHub automation and deployment

Collect daily at 02:17, 08:17, 14:17 and 20:17 UTC, plus manual dispatch with dry-run default. A separate freshness workflow runs at 03:47, 09:47, 15:47 and 21:47 UTC; it fails when public collector health is missing, invalid, future-dated or over 18 hours old. Content age and collector age are independent. Use Python 3.12, hash-locked dependencies and pinned actions. Fetch/classification has contents-read and no stored write credentials. Only the validated publisher gets contents-write. Commit explicit generated paths using normal fast-forward pushes.

Publish collector health at the raw repository URL, independently of Pages. Include the expected news-feed SHA-256; the monitor verifies public Pages bytes as well as collector age. State/health-only bot commits must skip Pages deployment to avoid triggering the kiosk's existing browser restart mechanism when display content has not changed. Ordinary application updates still deploy through CI. The repository is public: excluding ingestion state from Pages is packaging isolation, not confidential storage. No sensitive content belongs in that state.

Every non-dry collection must pass a separate read-only validation job before the contents-write job can run. Check out the exact collection revision, apply the immutable run artifact locally, validate all three output schemas, run regressions and independently decode the candidate feed's rendered QR codes at both screen sizes. This job has no Gemini secret or write credentials. A decoding or layout failure blocks publication and retains evidence. Record attempted, parsed and failed article counts separately from listing health; repeated article failures degrade health, and a total article-parser outage makes the freshness check fail even if index pages remain healthy.

Serialize scraper writes without cancelling active writes. If branch state changes during ingestion, fail publication and require a fresh run rather than rebasing stale data or exposing an API key to a privileged write job. This is a deliberate conservative adjustment from the proposed automatic recomputation attempt. Never force push.

Migrate Pages publishing to GitHub Actions. Use one reusable Pages workflow called by both ordinary validated site updates and successful news publication. Pass the exact source revision; reject superseded deployment revisions, serialize deployment jobs, and scope pages-write/id-token-write permissions to deployment only. Package explicit public assets. Verify the deployed public news bytes by SHA-256 with bounded CDN retries. Never rely on bot pushes starting a second workflow.

Routine story collection and publication require no manual input. The repository owner handles exceptional credential/platform changes and Actions failures. Enable Actions failure notifications and check schedule health monthly. GitHub scheduling has no exact-time guarantee and can disable after inactivity. Both health and collection workflows share GitHub availability, so this is not an independent external uptime service. Browser expiry remains active even if ingestion stops.

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
