# MAE news: coverage audit and remaining work

The initial release delivered the display, deployment, expiry, and refresh mechanisms but only one manually approved seed. Calling that implemented without emphasizing incomplete content intake was misleading. Source collection was healthy; AI classification had never run successfully because no Gemini key was configured.

## Corrected in the coverage follow-up

- Added WMU latest news and monthly archives covering the full 180-day retention window, plus bounded pagination. The original discovery read only the CEAS listing and MAE homepage.
- Expanded dated article URL recognition to other official WMU departments. The aerospace alumnus story under International Student and Scholar Services was previously excluded by the URL pattern.
- Fixed a false event hold: the EcoCAR article described students presenting vehicles at the end of a multiyear program, not an invitation requiring a short event deadline.
- Added separate manual-approval counts and a degraded automation status/warning when AI credentials are missing. A green deployment is not an operational AI feed.
- Verified six items for publication: Custer's upcoming November 4 talk, aerospace alumnus Talal Arshad, aerospace alumna Kelly Burris, the MAE-led EcoCAR program, the Lemmer appointment, and the WALI/Western Aerospace Thin-Sat story. These are source-reviewed manual approvals.
- The Custer invitation expires at its verified November 4, 1 p.m. Eastern start (18:00 UTC), because the source does not supply an end. The excerpt names only the upcoming talk, rather than promoting October events that have already happened.
- Preserved the 180-day age policy. Old NASA/team stories were not relabeled as current merely to fill all eight slots.

## Still unfinished

1. **Complete release verification for expanded automation.** The owner saved the GitHub Gemini secret. Live run [39461275630](https://github.com/airbreak404/department-display/actions/runs/39461275630) returned 11 valid rejections but hit classification/time failures. This led to paced calls, explicit minimal thinking, a larger bounded output allowance, bounded request timeouts, a circuit breaker and a separate positive/negative classifier check. See the validation ledger for the final release results.
2. **Finish automated archive backfill.** Discovery now inventories every dated archive link rather than filtering headlines. A live empty-feed/no-override test found 230 candidates and populated events and MAE stories over resumable passes. A broad roundup containing a later engineering credential exposed an overly permissive offline rule; automatic affiliation approvals now require primary story context. Deferred candidates resume without human review. Eight slots are a cap, not an instruction to include weak matches.
3. **Connect social sources when authorized access exists.** Official CEAS Facebook, Instagram and LinkedIn links are confirmed. The user has no admin access, so direct collection remains disconnected and is reported in health. See [access investigation](mae-news-social-access.md). No paid bridge or anonymous login-page scraping is enabled.
4. **Resolve departmental bulletin access before claiming coverage.** The tested MAE bulletin listing and old launch-event URL returned HTTP 404. Search-indexed copies are insufficient for live publication. No working bulletin adapter is claimed.
5. **Finish physical performance acceptance.** The 24-hour trend and human-visible smoothness remain pending. Content expansion and the editorial layout must be included. Green CI does not establish smoothness.

## Expanded automatic systems

The scope is MAE stories plus engineering opportunities open to MAE students, with no paid services and no routine manual curation. The previously seeded approvals have been cleared; the overrides file remains an optional emergency correction mechanism.

Collection runs four times daily. Narrow source-backed rules publish explicit MAE affiliations/teams and inclusive CEAS opportunities, while optional Gemini handles ambiguous relevance. Verified structured events and the Custer schedule adapter publish automatically and expire at their start. Unknown dates are skipped. Persistent inventory, decision caching, bounded retries/backoff, all-output validation, isolated publishing, public health and a separate stale-collector check support recovery. GitHub/Google/platform outages remain possible; no failure-proof guarantee is claimed.

The news slide now uses flat editorial rows, visible source/date metadata and source excerpts. Display-only cleanup removes datelines and em/en dashes; original source copy is retained in the feed. There are no generated summaries or decorative news badges.

## Acceptance evidence

The earlier coverage release passed 24 Python regressions and Chromium checks. Expanded automation now passes 35 Python tests plus Chromium checks at both resolutions, including quota/circuit-breaker behavior, offline publication, cache recovery, event cancellation/zones/expiry and independent collector freshness. The dependency audit found no known runtime vulnerabilities. Final deployed counts and kiosk evidence are recorded in `mae-news-validation.md`.

The live archive audit successfully parsed 13 listing pages, including pagination. Before the additional manual reviews, it found 23 held candidates rather than the original six; many were unrelated scholarships, other departments, or expired invitations. This demonstrates the coverage gap; it is not a claim that 23 stories should be published.

Official reviewed sources:

- [EcoCAR program, June 22](https://wmich.edu/engineer/news/2026/06/ecocar-innovation-challenge-gm)
- [Aerospace alumnus profile, August 17](https://wmich.edu/international/news/2026/08/aerospace-alumni-arshad)
- [Custer fall series, September 22](https://wmich.edu/engineer/news/2026/09/custer-series-fall-2026)
- [Custer current speaker details](https://wmich.edu/engineer/custerseries)
- [Lemmer appointment, June 15](https://wmich.edu/engineer/news/2026/06/kristina-lemmer-hallquist-endowed-professor)
- [WALI satellite, May 5](https://wmich.edu/news/news/2026/05/aerospace-engineering-spacex-payload-launch-tom-scott)
- [Kelly Burris aerospace alumna profile, June 26](https://wmich.edu/magazine/news/2026/06/alumna-trustee-kelly-burris-profile)
