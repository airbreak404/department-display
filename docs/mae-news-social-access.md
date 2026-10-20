# CEAS social source investigation

Checked October 20, 2026. The [official CEAS homepage](https://wmich.edu/engineer) and MAE homepage link these college accounts:

- [Facebook WMUCEAS](https://www.facebook.com/WMUCEAS)
- [Instagram wmu_engineers](https://www.instagram.com/wmu_engineers/)
- [College LinkedIn organization](https://www.linkedin.com/edu/school?id=162162), school ID 162162. The university website currently uses a legacy organization link.

The user confirmed no admin access. These are worthwhile content sources, but direct automatic ingestion is not connected and is reported as a coverage gap in public health. No social API token, paid bridge, browser session scraping, or marketing-account access was provisioned. No message was sent to marketing.

The [official LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-06) requires organization read permissions and an appropriate organization role. Its API also requires current version headers; it cannot be treated as an anonymous RSS feed. Meta's documentation endpoints could not be read reliably during this audit, so exact Facebook/Instagram scopes and review requirements are deliberately not represented as verified implementation details.

When marketing can provide authorized read access, verify current official platform documentation, account IDs, scopes, API/app review, cost and token lifetime before implementation. Request only read access. Isolate adapters from the public display and write-enabled publishing job. Bound pagination, response sizes and retries; reject user-supplied next-page hosts and never log tokens. Refresh supported tokens automatically and report expiry/auth failures. Cross-posted WMU links should converge on the official article identity; social-only items need trustworthy platform timestamps and source permission. Apply the same MAE relevance, event-date, age, deduplication, schema and failure gates. Test real access before claiming coverage.

This setup may need periodic reauthorization when platforms revoke access. It must not require manually selecting or copying individual posts. An existing approved university feed could be another free route if marketing already exposes one; no such endpoint has been verified.
