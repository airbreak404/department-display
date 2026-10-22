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
2. **Automatic coverage remains partial.** The original 233-URL inventory was fetched over bounded passes, but the final pass still held four classifications. A later run held 22 after reaching the model budget. Zero immediately due deferrals did not mean all decisions were complete. October 21 hardening adds persistent pending-classification, pending-retrieval and unreviewed-policy counts; those counts must be checked before claiming inventory completion. Changed policies recheck prior successful candidates immediately while respecting failure backoff. The known Aviation false positive remains blocked; `rules-4` requires affirmative affiliations and sends ambiguous cases to Gemini.
3. **Physical performance acceptance remains pending.** The original mixed-release monitor recorded seven collection failures overnight, not seven proven application outages. It cannot establish 24 hours of the final release. The replacement monitor records release identity, progression, browser errors, expected news, host boot identity and service restarts in a fresh evidence directory. Collection success never establishes physical smoothness. See the latest validation entry for deployment and observation evidence.

   The final-release run started October 21 at 09:46:48 EDT in `scratch/soak-final-20261021-0947/`, with its own loopback port 19223. It is due to complete October 22 around 09:47 EDT. First sample was clean; full-day acceptance is still pending.
4. **Access-dependent sources (explicit gaps):**
   - Official CEAS Facebook, Instagram, and LinkedIn accounts are documented, but direct ingestion is disconnected due to lack of account administrative credentials. See [access investigation](mae-news-social-access.md).
   - Department bulletin links returned HTTP 404; ScholarWorks newsletters are archival through 2020. No live bulletin adapter is claimed.

## Expanded automatic systems

The scope is MAE stories plus engineering opportunities open to MAE students, with no paid services and no routine manual curation. The previously seeded approvals have been cleared; the overrides file remains an optional emergency correction mechanism.

Collection runs four times daily. Narrow source-backed rules publish explicit MAE affiliations/teams and inclusive CEAS opportunities, while optional Gemini handles ambiguous relevance. Verified structured events and the Custer schedule adapter publish automatically and expire at their start. Unknown dates are skipped. Persistent inventory, decision caching, bounded retries/backoff, all-output validation, isolated publishing, public health and a separate stale-collector check support recovery. GitHub/Google/platform outages remain possible; no failure-proof guarantee is claimed.

The news slide now uses flat editorial rows, visible source/date metadata and source excerpts. Display-only cleanup removes datelines and em/en dashes; original source copy is retained in the feed. There are no generated summaries or decorative news badges.

## Acceptance evidence

Expanded automation passes **53 Python tests** plus Chromium checks at both resolutions, including independent QR decoding, vendor integrity, publication guards, quota/circuit-breaker behavior, offline publication, cache recovery, event cancellation/zones/expiry, retained items on parser drift, affiliation counterexamples, persistent unresolved work, health retry/error categories and monitor failure detection. The real-feed QR gate requires exactly one successfully decoded code for every expected item. Final deployed counts and kiosk evidence are recorded in `mae-news-validation.md`.

Official reviewed sources:

- [EcoCAR program, June 22](https://wmich.edu/engineer/news/2026/06/ecocar-innovation-challenge-gm)
- [Aerospace alumnus profile, August 17](https://wmich.edu/international/news/2026/08/aerospace-alumni-arshad)
- [Custer fall series, September 22](https://wmich.edu/engineer/news/2026/09/custer-series-fall-2026)
- [Custer current speaker details](https://wmich.edu/engineer/custerseries)
- [Lemmer appointment, June 15](https://wmich.edu/engineer/news/2026/06/kristina-lemmer-hallquist-endowed-professor)
- [WALI satellite, May 5](https://wmich.edu/news/news/2026/05/aerospace-engineering-spacex-payload-launch-tom-scott)
- [Kelly Burris aerospace alumna profile, June 26](https://wmich.edu/magazine/news/2026/06/alumna-trustee-kelly-burris-profile)

## October 22 status correction

Automatic collection/publication is running; latest reviewed run39790659194 reports8 items, pendingClassification0, pendingRetrieval8, unreviewed0, status partial. The eight outstanding outcomes were diagnosed: five WMU article body-layout failures are repaired and safely reprocessable; three source-metadata cases stay held. See mae-news-validation.md for precise limits. Optional social access is still blocked by absent authorized account access.

The October21 final-release observation did not finish:22 samples,10 collection failures,2 observation failures and stale running=true. Preserve that evidence; it cannot satisfy24h acceptance. A new observation is required after final recovery/deployment tests, using the updated pinned offline-origin probe. Physical smoothness and elapsed24h/72h/seven-day gates remain open.

Latest October22 publication39826836548 and bot30cfee1 supersede the earlier run39790659194 snapshot:8 items,3 pending retrieval,9 pending classification,113 unreviewed, partial coverage. Publication/QR gates passed; same feed bytes meant deployment skip was expected, with separate source Pages deployment passed. The kiosk ingested the same verified feed. Source metadata uncertainty stays held; optional social access is still unavailable. The new17:51Z observation was invalidated by a host graphics incident and later controlled recovery tests. Its needs_review failures are retained and cannot count as24h acceptance. See the latest checkpoint in mae-news-validation.md.
