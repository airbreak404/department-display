# MAE news validation ledger

Current result (October22 continuation): scheduled collection/publication is operational, with8 items,0 pending classifications,8 pending retrieval/parser outcomes and0 unreviewed entries at run39790659194. Coverage remains partial. The source parser and offline observation repairs below pass55 Python tests; Chromium/QR and public feed verification pass. Physical and sustained acceptance remain open. Earlier entries below are historical, including key/collector setup statements.

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

## Final live content-refresh proof

- [Second ingestion and explicit deployment](https://github.com/airbreak404/department-display/actions/runs/39453684523) applied a manually reviewed correction: the source excerpt now ends at a complete sentence and removes an inline-link spacing artifact. Bot commit `61af9ae` changed only generated `data/news.json`.
- Both real browsers picked up that deployed correction by the 12:09:40 EDT probe through their normal 10-minute content poll and slide-boundary update. No reload, visibility event, fake feed, accelerated clock, or manual refresh was used for this proof.
- Before and after document time origins remained **1792511940193.1** (2560×1440) and **1792511935332.8** (2048×1152). Chrome PID remained **65345**. The service still reported `NRestarts=0`; both displays retained 21 slides and unpaused cycling.
- The exact corrected excerpt was observed in each live deck. DOM count remained 959 per page. Short heap samples varied within the same range; the 24-hour trend remains pending.
- [Final Linux regression/deployment run](https://github.com/airbreak404/department-display/actions/runs/39454169198) passed after correcting publisher attribution and inline punctuation. All 19 Python tests and real Chromium checks passed. Both runtime and test dependency audits found no known vulnerabilities.
- Source change revision is `9858443`. Documentation-only pushes now skip site deployment to avoid unnecessary kiosk update notifications.
- Live screenshots of the news page were visually checked on each display; synthetic one-, two-, and three-card layouts were also visually checked at both target sizes. Evidence and the final read-only probe are retained locally under `scratch/kiosk/` and `test-results/`.
- Repository secrets were checked and `GEMINI_API_KEY` remains absent. Live AI classification is intentionally unverified and held fail-closed. The functioning visible seed is a source-verified manual approval, not an AI approval.
- The 24-hour collector continues in the background under PID 14080. It started October 20 at 11:59:40 EDT and should finish around October 21 noon EDT. Inspect `scratch/soak/status.json` and `samples.jsonl` afterward; collection success alone does not establish visual smoothness. Do not mark soak acceptance complete until reviewed.

## Coverage follow-up prompted by the one-story result

- Confirmed the user's observation: the feed contained exactly one manually approved story; Gemini had never classified a live candidate. Repository key still absent.
- Found two independent coverage defects: discovery read only two landing pages and excluded official non-CEAS departmental URL patterns; event detection treated a multiyear project's future technical presentations as a dated invitation.
- Expanded discovery and pagination, corrected that event false positive, and added degraded automation status, explicit warnings, review URLs/dates/reasons, and separate manual-approval counts.
- A live dry-run parsed 13 listing pages successfully, spanning April–October archives and pagination. It found 23 held candidates before manual review expansion. The run was dry and began with the original single manual approval, so its one-item candidate output was not used to replace the expanded feed.
- Source-reviewed Custer's November 4 invitation, Arshad's aerospace degrees, Burris' aerospace career and WMU aeronautical engineering education, the MAE-led EcoCAR program, and WALI's Thin-Sat payload. Together with Lemmer, these form six unexpired items. Unrelated department-only stories were not added.
- The Custer source supplies a November 4 start but no end; the invitation expires conservatively at the verified start, 18:00 UTC. It does not promote the already-past October talks. WALI's May 5 article retains its actual publication date and expires November 1 under the original age policy.
- 24 Python regressions and Chromium checks passed; the intermediate four-item feed was visually rendered on two pages and [passed Linux CI and deployment](https://github.com/airbreak404/department-display/actions/runs/39459548543).
- Soak collector remains running with zero collection failures at the latest checkpoint. Its initial observations include the one-item feed; the expanded content must be considered in final performance acceptance rather than treating earlier samples as validation of every later change.

## Automatic intake, Gemini and editorial release

- Owner selected MAE stories plus engineering opportunities available to MAE students, no paid services and no routine manual curation. The owner saved the Actions secret directly in GitHub; the key was not pasted into chat or stored in this workspace. Copilot Student was researched as an alternative; no Copilot credits or billing settings were changed. See `mae-news-ai-options.md`.
- First real Gemini run [39461275630](https://github.com/airbreak404/department-display/actions/runs/39461275630) returned valid rejections but exposed latency/transient failures and the run budget. A 15-second trial was too short and failed its focused check. The bounded timeout was corrected to 45 seconds; generation is paced, capped at 20 calls, and protected by a three-candidate failure circuit breaker. Errors are recorded as sanitized categories, never raw API exception bodies.
- Focused live check [39464161173](https://github.com/airbreak404/department-display/actions/runs/39464161173) passed in two calls with zero errors: Lemmer's MAE appointment approved, ECE-only power-systems story rejected.
- [Automatic collection, commit and deployment 39464251490](https://github.com/airbreak404/department-display/actions/runs/39464251490) succeeded with **seven displayed items, zero manual approvals**: five MAE stories and two upcoming opportunities. Six approvals used narrow offline rules; Kelly Burris used Gemini. It recorded 233 inventoried URLs, 80 attempted candidates, 153 deferred, 38 rejections and 13 skips. Twenty generation calls included sanitized HTTP 503/504 failures that did not prevent publication. Status correctly remained partial, not a claim of full backfill.
- Empty-feed, no-key, no-override local passes also demonstrated restartable population. A campus roundup with an incidental later engineering credential exposed an overly broad rule; rules version 2 restricts automatic affiliation approvals to primary story context. Uncertain later mentions go to Gemini.
- [Expanded release CI](https://github.com/airbreak404/department-display/actions/runs/39463719379) and [latency/punctuation correction CI](https://github.com/airbreak404/department-display/actions/runs/39464161519) passed Linux tests, Chromium checks and deployment verification.
- The real kiosk showed the flat editorial layout on both resolutions. Inspected captures `scratch/kiosk/page-2560-1792516660.png` and `page-2048-1792516670.png`. Short news samples remained about 66.7 ms median and 66.8-83.4 ms p95, with both browsers cycling unpaused. These are no-regression samples, not 60-fps or 24-hour acceptance.
- Source dates and source copy remain original in the feed. Display-only cleanup removes datelines and em/en dashes, preserves numeric-range meaning, and uses plain editorial rows instead of rounded cards/badges.

## QR and quiet health deployment follow-up

- User explicitly requested a QR for every news article or social post. News/event rows now encode the exact item URL using a local hash-pinned MIT-licensed Nayuki library, with black/white contrast and four-module quiet borders. The department gateway also uses local generation; the external QR API was removed from application code and CSP.
- Independent ZXing decoding of actual Chromium QR screenshots passed at 2048x1152 and 2560x1440 for all seven real published URLs and a query-string regression. Synthetic 1/2/3/8-story layouts also passed decoding and canvas-bound checks. Visual previews are under `test-results/news-real-*`; the additional query fixture is test data only.
- Local checks now pass **38 Python tests**, including vendor integrity and publication-before-mutation guards, plus Chromium/QR checks. The locked test dependency audit reports no known vulnerabilities. Phone-camera scanning under physical lighting/distance and the 24-hour post-release observation remain pending.
- Health-only deployment was identified as an unnecessary trigger for the pre-existing host sync/restart mechanism. Current collector health is moved to the raw repository URL, includes the expected public-feed hash, and is checked independently of content age. State/health-only commits skip Pages; news-byte changes still explicitly deploy. Final live verification is recorded below after rollout.

## Live QR decoding and quiet publication verified

- [QR release Linux CI and deployment](https://github.com/airbreak404/department-display/actions/runs/39466502052) passed. Application assets were explicitly reloaded on the two existing kiosk pages using CDP; no Chrome flags, host launcher or services were changed.
- Both real pages showed **23 total slides, three news pages and seven items**, cycling unpaused. All seven QR codes decoded to their exact source URLs on each display, fourteen successful real-display decodes total. No em/en dashes remained in visible news text. Evidence: `scratch/kiosk/qr-release/verification.json` and `{2048,2560}-page-{1,2,3}.png`.
- QR-release short samples: 2560 display median/p95 about 83.3/83.5 ms; 2048 display about 66.7/66.8 ms. Results remain within the earlier short-sample range, but do not prove sustained smoothness. Heap samples were about 1.8-2.4 MB; no accumulating trend can be concluded from those samples.
- [Second automatic collection 39466501275](https://github.com/airbreak404/department-display/actions/runs/39466501275) examined another 80 candidates, retained seven items, required zero manual approvals, and left 73 inventory candidates deferred. It rejected 49 and skipped 11. Twenty model calls included transient 503/504 errors. No feed bytes changed; only state/health were committed, and **Pages deployment was skipped** as intended.
- The public collector health age and expected Pages feed hash passed the local check and [independent GitHub health workflow 39468303149](https://github.com/airbreak404/department-display/actions/runs/39468303149). Reduced/backfill coverage produced a warning rather than a false complete-coverage claim.
- The final hardening adds read-only per-update QR validation before the privileged publisher, plus article-level outage detection. Local checks pass **39 Python tests** and Chromium/QR regressions, including valid empty feeds.
- [Scraper run 39468623260](https://github.com/airbreak404/department-display/actions/runs/39468623260) on `d3bf328` completed all four pipeline stages successfully: collection, candidate validation with mandatory Chromium QR decoding, bot commit `5631bdd`, and explicit GitHub Pages deployment with public feed hash verification. It processed all 73 deferred archive candidates, completing the 233-item inventory (0 deferred).
- Content Relevance & False-Positive Hardening:
  - During backfill, an 8th candidate was ingested: *"From Student Involvement to Airline Operations: Kevin Klimas’ Aviation Management Path"* (`https://wmich.edu/aviation/news/2026/04/klimas`, ID `e68f1c27067d6e8828d67e30`).
  - Critical audit confirmed this is a false positive: Klimas is an Aviation Management senior in the College of Aviation (Battle Creek), not an MAE student. He was matched because `relevance.py` rules-2 contained `\bengineering\b` in `PERSON`, creating a tautological match with `DIRECT` on "aeronautical engineering" in a paragraph describing the fraternity Alpha Eta Rho.
  - Candidate `e68f1c27067d6e8828d67e30` was blocked in `data/news-overrides.json`, immediately purging it from the active display deck.
  - `relevance.py` was upgraded to `rules-3`: removed `\bengineering\b` from `PERSON`, rejected non-engineering items early without wasting model budget, and prevented College of Aviation candidates from auto-approving offline.
  - Regression assertions were added to `tests/test_automation.py`. All 39 unit tests and Playwright browser QR decodes pass.
- Current live display status:
  - Both hallway displays (2560×1440 and 2048×1152) are active, cycling unpaused with 23 slides, 3 news pages, and exactly 7 verified, high-quality MAE stories/opportunities.
  - JS heap usage is ~1.2–1.5 MB with 1,045 DOM elements and zero uncaught exceptions.
  - Background 24-hour stability soak continues under PID 14080 (collector PID 28480, tunnel PID 2876) with 25+ consecutive error-free samples; final soak acceptance remains scheduled for Oct 21 ~12:00 EDT.

## October 21 critical-review fixes

- The earlier completion language was too strong: run 39468623260 had four held classifications despite zero due deferrals; later run 39564243995 had 22 held and 148 due deferrals. A fetch attempt is not a completed classification. New persistent inventory outcomes and policy hashes expose `pendingClassification`, `pendingRetrieval` and `unreviewed` across runs. Legacy decisions require revalidation; failed retrievals keep backoff.
- Reproduced and fixed: ordinary news containing "welcomes" was forced through event extraction and removed while status said `ok`. Explicit invitation/structured-event detection replaces generic keyword matching. Parser drift preserves valid unexpired news/events. Verified cancellation/expiry/deletion/rejection still retracts content, including emergency overrides.
- `rules-4` and prompt `mae-3` reject automatic inference from keyword coincidence, a foreign visiting professor, a fraternity's generic careers and negated programs. Narrow affirmative local affiliations remain automatic; ambiguity goes to Gemini. The existing known false-positive block is retained.
- Candidate QR validation now requires an exact count before independent decoding at both resolutions. Encoder failure omits inaccessible news while retaining the base presentation; it cannot silently pass the normal publication gate. Rendered text prefers complete source sentences, recognizes abbreviations/initials and uses measured word boundaries when needed.
- Health retrieval retries transient network failures and reports sanitized stage/reason codes. Historical freshness failure 39519440960 had only a generic message, so its exact cause remains unknown; later health checks passed.
- The original mixed-release monitor has seven collection failures overnight, approximately 20:58-21:29 EDT. The host boot log shows a boot at 21:31; that observation does not establish the cause of the earlier collection gap or attribute it to news changes. No clean final-release 24-hour acceptance is claimed.
- The replacement monitor uses fresh evidence directories, release identity, slide progression/error counters, expected content, browser reloads, boot/service identities and crash evidence. It uses separate loopback port 19223; the original collector remains independent. Physical smoothness always requires human review.
- Owner-supplied AI Studio screenshot reviewed October 21 shows **Free tier** and **Set up billing** for the display project. No key details or account identifiers were copied. This verifies the visible setting at that time; future billing changes remain outside application control.
- Local validation: **52 Python tests pass**, Chromium/QR regressions at both resolutions pass, dependency audit reports no known vulnerabilities, and the defensive workspace scan reports no potential issues. Browser screenshots are in ignored `test-results/`. Deployment/live ingestion and final-release soak evidence will be appended after verification.
- [Linux site validation/deployment 39608939080](https://github.com/airbreak404/department-display/actions/runs/39608939080) passed for `0a3ec07`, including Python tests, Chromium QR tests and public deployment hash verification. Explicit CDP page reloads accelerated the application-asset update; this was not a no-reload news-only update test. Both real browsers loaded `20261021v1`, with 23 slides, seven items across three news pages, unpaused and zero recorded JavaScript errors/rejections.
- Independently decoded all **14 real-browser QR destinations** across six screenshots, then restored the original selected slide. Evidence: ignored `scratch/kiosk/review-release/verification.json` and adjacent screenshots. No visible em/en dashes appeared on the news pages.
- The new monitor's bounded live smoke run in `scratch/soak-smoke-20261021-0938` completed with two samples, zero collection failures and zero observation failures. An additional regression prevents a short final sampling interval from falsely reporting stalled progression; local tests now total **53 passing**. This smoke run is not the 24-hour gate.
- [Live collection/publication 39608954579](https://github.com/airbreak404/department-display/actions/runs/39608954579) passed collection, read-only candidate QR validation, publication and explicit Pages deployment. All seven current items were reapproved, including two source-backed Gemini decisions. It rejected 61 candidates, held nine, used 20 model calls with **zero API failures**, and reported partial coverage rather than completion. Inventory: 234, due deferrals: 151, pending classification: nine, pending retrieval: zero, unreviewed older-policy entries: 154. Automatic scheduled passes continue this migration; not all inventory is classified.
- Public collector freshness and feed SHA-256 passed after publication. Short real-browser frame samples on both displays were approximately 66.7 ms median and 83.4 ms p95, within the earlier measured range; this is not 60 fps or full-day smoothness acceptance.
- Final helper revision `d1b0bab` passed [Linux CI and deployment 39610650061](https://github.com/airbreak404/department-display/actions/runs/39610650061), including all **53 Python tests** and Chromium/QR checks. [Independent freshness run 39610649801](https://github.com/airbreak404/department-display/actions/runs/39610649801) passed; partial coverage remains explicitly warned.
- Fresh 24-hour final-release observation started **October 21 at 09:46:48 EDT**, expected to finish October 22 at approximately the same time. Evidence: ignored `scratch/soak-final-20261021-0947/`, manifest revision `d1b0bab`, clean tree at start, asset version `20261021v1`, five-minute interval, dedicated **127.0.0.1:19223** tunnel. First sample: zero collection/observation failures. Historical process snapshot: launcher 19888, Python collector 12260, SSH listener 20228; reverify command lines before any process operation. The original mixed-release collector/evidence was preserved. This observation continues independently of chat; **24-hour completion and physical smoothness remain pending**. Expected content/deployment reloads must be reviewed separately from unexplained restarts.

## October 22 recovery continuation: retrieval diagnosis and observation repair

The scheduled collector [39790659194](https://github.com/airbreak404/department-display/actions/runs/39790659194) succeeded, including candidate QR validation and publication. Its report has 234 inventory URLs, eight published items, zero pending classifications, eight pending retrievals, zero unreviewed entries, and partial coverage. Freshness run39797731106 also passed. The actual offline kiosk probe now confirms eight items across three news pages on both 2560x1440 and2048x1152 roles,23 total slides, matching indexes, unpaused visible content and zero JavaScript errors/rejections. Query visibility does not establish physical TV visibility.

All eight failed URLs were fetched again using the same bounded publisher client. Five article failures were caused by selecting only the first WMU .text-paragraph block, which could contain just an image; source prose may also be direct text in .dxp-text rather than p elements. The parser now combines the publisher's body blocks, removes ancillary content, and supports direct source text. It still requires a verified date and affirmative relevance. Those five pages parse after the repair; this does not approve them for MAE publication. The parser version participates in the review fingerprint and grants one bounded retry for previously failed extraction after a parser upgrade, then restores normal backoff.

Three publisher-metadata cases remain held: the senior-design landing page has its h1 outside the article and lacks the strict single zoned Event metadata needed for verified event expiry; the Valley Oaks and media-coverage articles lack a verified publication date. Dates are not inferred from URL months, retrieval time or nearby events. Optional social access remains not_connected and is not a release prerequisite.

Current checks:55 Python tests pass; Chromium news/QR regression passes at both resolutions; collector freshness and public feed hash pass. A workstation-only verify_public mismatch was traced to CRLF checkout conversion: parsed JSON was identical and the LF hash exactly matched the public response. Generated public news JSON now has explicit LF attributes, and byte verification passes after normalization. This was a verification-path defect, not evidence of failed public publication.

The old final-release collector is abandoned: its last sample was2026-10-21T15:33:12Z,22 samples,10 collection failures and2 observation failures, despite stale running=true. Its evidence remains unchanged; it did not complete24h. The probe also needed updating for the current fixed offline origin http://127.0.0.1:8765/department-display/; it now accepts only that origin or the exact public kiosk origin and pins CDP to the local SSH tunnel. Collector SSH calls explicitly require StrictHostKeyChecking=yes. A fresh final-configuration observation follows the reliability recovery tests; full24h review and physical smoothness remain mandatory.

Raw publisher HTML, desktop evidence and collector output remain in ignored scratch/ and private reliability evidence, not in public Git. The full display acceptance ledger is in the private mae-reliability repository, issue1.
