# MAE news validation ledger

Current result: initial deployment and news-only refresh verified; coverage follow-up expands the reviewed feed from one item to six. 24 Python regressions and Chromium checks pass. Automatic classification is **not operational** until a Gemini key is configured and verified. Optional social/bulletin integrations and final soak acceptance remain unfinished. See `mae-news-remaining-work.md` for the full inventory.

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
- The final hardening adds read-only per-update QR validation before the privileged publisher, plus article-level outage detection. Local checks now pass **39 Python tests** and Chromium/QR regressions, including valid empty feeds. Final Linux/automatic gate verification follows below.
