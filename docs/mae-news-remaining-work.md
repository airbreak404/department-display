# MAE news: coverage audit and remaining work

The initial release delivered the display, deployment, expiry, and refresh mechanisms but only one manually approved seed. Calling that implemented without emphasizing incomplete content intake was misleading. Source collection was healthy; AI classification had never run successfully because no Gemini key was configured.

## Corrected in the coverage follow-up

- Added WMU latest news and monthly archives covering the full 180-day retention window, plus bounded pagination. The original discovery read only the CEAS listing and MAE homepage.
- Expanded dated article URL recognition to other official WMU departments. The aerospace alumnus story under International Student and Scholar Services was previously excluded by the URL pattern.
- Fixed a false event hold: the EcoCAR article described students presenting vehicles at the end of a multiyear program, not an invitation requiring a short event deadline.
- Added separate manual-approval counts and a degraded automation status/warning when AI credentials are missing. A green deployment is not an operational AI feed.
- Verified items for publication: Custer's upcoming November 4 talk, Senior Engineering Design Conference, aerospace alumnus Talal Arshad, aerospace alumna Kelly Burris, the MAE-led EcoCAR program, the Lemmer appointment, and the WALI/Western Aerospace Thin-Sat story.
- The Custer invitation expires at its verified November 4, 1 p.m. Eastern start (18:00 UTC), because the source does not supply an end. The excerpt names only the upcoming talk, rather than promoting October events that have already happened.
- Preserved the 180-day age policy. Old stories were not relabeled as current merely to fill all eight slots.

## Verification status

1. **Mandatory QR validation & quiet health:** Verified. Run 39468623260 passed the mandatory candidate QR decoding gate in CI before publication. Both real kiosk displays independently decode all 7 active items across resolutions.
2. **Automated archive backfill:** Completed. All 233 inventoried archive candidates were evaluated over bounded passes, leaving 0 deferred. An 8th incidental aviation candidate was audited, blocked in overrides, and offline rules were hardened to `rules-3`.
3. **Physical performance acceptance (in progress):** The 24-hour stability collector continues running in the background (PID 14080) with zero collection errors across 25+ samples. Scheduled for final smoothness review upon completion on Oct 21 ~12:00 EDT.
4. **Access-dependent sources (explicit gaps):**
   - Official CEAS Facebook, Instagram, and LinkedIn accounts are documented, but direct ingestion is disconnected due to lack of account administrative credentials. See [access investigation](mae-news-social-access.md).
   - Department bulletin links returned HTTP 404; ScholarWorks newsletters are archival through 2020. No live bulletin adapter is claimed.

## Expanded automatic systems

The scope is MAE stories plus engineering opportunities open to MAE students, with no paid services and no routine manual curation. The previously seeded approvals have been cleared; the overrides file remains an optional emergency correction mechanism.

Collection runs four times daily. Narrow source-backed rules publish explicit MAE affiliations/teams and inclusive CEAS opportunities, while optional Gemini handles ambiguous relevance. Verified structured events and the Custer schedule adapter publish automatically and expire at their start. Unknown dates are skipped. Persistent inventory, decision caching, bounded retries/backoff, all-output validation, isolated publishing, public health and a separate stale-collector check support recovery. GitHub/Google/platform outages remain possible; no failure-proof guarantee is claimed.

The news slide now uses flat editorial rows, visible source/date metadata and source excerpts. Display-only cleanup removes datelines and em/en dashes; original source copy is retained in the feed. There are no generated summaries or decorative news badges.

## Acceptance evidence

Expanded automation passes **39 Python tests** plus Chromium checks at both resolutions, including independent QR decoding, vendor integrity, publication guards, quota/circuit-breaker behavior, offline publication, cache recovery, event cancellation/zones/expiry and collector/publication health. The dependency audit found no known runtime or test dependency vulnerabilities. Final deployed counts and kiosk evidence are recorded in `mae-news-validation.md`.

Official reviewed sources:

- [EcoCAR program, June 22](https://wmich.edu/engineer/news/2026/06/ecocar-innovation-challenge-gm)
- [Aerospace alumnus profile, August 17](https://wmich.edu/international/news/2026/08/aerospace-alumni-arshad)
- [Custer fall series, September 22](https://wmich.edu/engineer/news/2026/09/custer-series-fall-2026)
- [Custer current speaker details](https://wmich.edu/engineer/custerseries)
- [Lemmer appointment, June 15](https://wmich.edu/engineer/news/2026/06/kristina-lemmer-hallquist-endowed-professor)
- [WALI satellite, May 5](https://wmich.edu/news/news/2026/05/aerospace-engineering-spacex-payload-launch-tom-scott)
- [Kelly Burris aerospace alumna profile, June 26](https://wmich.edu/magazine/news/2026/06/alumna-trustee-kelly-burris-profile)
