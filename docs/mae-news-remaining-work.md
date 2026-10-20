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

1. **Enable and verify Gemini classification.** Add repository Actions secret `GEMINI_API_KEY`, verify model/free-tier access, then prove an actual model-approved/rejected run. Until then, new uncertain candidates remain held and the visible feed relies on reviewed approvals.
2. **Review newly discovered candidates.** Broader discovery can find more applicable stories and more unrelated campus news. Review held results; do not assume every match belongs on an MAE display. Event invitations need verified dates and conservative expiry.
3. **Integrate optional social sources if desired.** Instagram, LinkedIn, and Facebook adapters/feeds were deferred and are not integrated. They require approved, reliable access; they were not quietly scraped.
4. **Resolve departmental bulletin access before claiming coverage.** The tested MAE bulletin listing and old launch-event URL returned HTTP 404 during this audit. Search-indexed copies are not sufficient for automated live publication. No working bulletin adapter is claimed.
5. **Finish performance acceptance.** The collector is running, but the 24-hour trend and human-visible smoothness still need review. Content expansion must be included in that assessment.

## Acceptance evidence

Local checks after coverage fixes: 24 Python regressions passed and real Chromium regression checks passed. The four-item intermediate feed was rendered locally and its deployment passed Linux CI. The expanded feed contains six different stories across two three-card pages. Deployment and final live display results are recorded in `mae-news-validation.md`.

The live archive audit successfully parsed 13 listing pages, including pagination. Before the additional manual reviews, it found 23 held candidates rather than the original six; many were unrelated scholarships, other departments, or expired invitations. This demonstrates the coverage gap; it is not a claim that 23 stories should be published.

Official reviewed sources:

- [EcoCAR program, June 22](https://wmich.edu/engineer/news/2026/06/ecocar-innovation-challenge-gm)
- [Aerospace alumnus profile, August 17](https://wmich.edu/international/news/2026/08/aerospace-alumni-arshad)
- [Custer fall series, September 22](https://wmich.edu/engineer/news/2026/09/custer-series-fall-2026)
- [Custer current speaker details](https://wmich.edu/engineer/custerseries)
- [Lemmer appointment, June 15](https://wmich.edu/engineer/news/2026/06/kristina-lemmer-hallquist-endowed-professor)
- [WALI satellite, May 5](https://wmich.edu/news/news/2026/05/aerospace-engineering-spacex-payload-launch-tom-scott)
- [Kelly Burris aerospace alumna profile, June 26](https://wmich.edu/magazine/news/2026/06/alumna-trustee-kelly-burris-profile)
