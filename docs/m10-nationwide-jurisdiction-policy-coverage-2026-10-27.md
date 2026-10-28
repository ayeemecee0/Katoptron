# M10 · All-state Flock policy evidence coverage and real original acquisition

Implemented October 27, 2026. This is a **source coverage product**, not the false claim that every U.S. municipality or police agency was checked and verified.

## National baseline from already reviewed original ledgers

| Dimension | Authentic source and extent |
|---|---|
| State-level research jurisdictions | 50 states plus Washington, D.C. (51 of 51) |
| Distinct curated government URL sources | 43 newer independently retrieved/held original-publisher URLs + 14 older curated URLs = **57** |
| Newer original URLs retrieved at observation | **31 of 43**; another 12 held (e.g. redirect or inaccessible) |
| State Attorney General ALPR agency registrations | **97** Washington self-certifications; neither Flock status nor current operational agency roster |
| Agency dossiers individually source-page reviewed | **18 agencies**, **25 original documents**, across **7 states**, some only historical/draft/government text |
| Independently completed statewide local agency census | **0 of 51**; no comprehensive statewide policy inventory inferred |
| Verified new camera GPS points or current Flock sharing edges | **0** |

Source and status counts come from current independently verified registry JSON and fail-closed validators, not search popularity. Adding more government links does not create verified Flock operations, current policy, county-wide completeness or nationwide camera locations.

## New product

- `nationwide-policy.html` exposes a **51-state evidence-gap matrix** with all jurisdictions state-listed, direct government source URLs, 97 state registrations clearly labeled self-certified, 18 separate individually page-reviewed dossier agencies, and Apache Junction adoption versus Green Bay unadopted draft.
- `nationwide-policy-coverage.js` combines official-source registry, original retrieval receipts, state AG registration source, originally verified agency ledgers and source-qualified adoption status with strict validation. Unique agency dossiers are not deduced from approximate city names, scraped search result counts or vendor portals.
- Source details and local agency entries can be searched by state and evidence tier. The first-load view intentionally shows summary and all 51 state rows without rendering or implying a complete municipality/department directory.
- Navigation from map, Agency X-Ray, Policy History and Government Watch.
- Independent `nationwide_policy_coverage.yml` CI with unit, adversarial and mobile Chromium tests; existing accountability CI also tests the page.

## Nationwide source acquisition upgrade

`scripts/watch_nationwide_government_originals.py` now extracts up to 12 bounded **same-government-host** ALPR/Flock policy-document links from each successful official government HTML response; it refuses cross-host and sensitive vehicle/plate search-log URLs. All outputs are labeled `government_same_host_link_unverified_individual_document`. It never publishes an adoption, current policy claim, sharing relationship or camera coordinate.

First live all-51-state crawl of that code:

- 43 newer exact first-party source URLs checked; **31 retrieved, 12 held**.
- **Two new same-host policy document links** discovered:
  - Robbinsdale MN Police Policy 427: [official source](https://www.robbinsdalemn.gov/DocumentCenter/View/2520/Robbinsdale-Police-Department-Policy-Manual-Policy-427). New document verification candidate; the department's separately published official page identifies use of Flock Safety, but the policy PDF needs independent page review and cannot be assumed effective from its filename alone.
  - Brookings SD Policy 13D1: [official source](https://cityofbrookings-sd.gov/DocumentCenter/View/20501/Policy-13D1---Automated-License-Plate-Recognition-System). Duplicate of a previously source-page-reviewed agency policy, not a new finding.
- The separately triggered all-51-state public search feed completed 51 searches but generated **zero** usable additional link leads; no negative Flock coverage inference follows from an empty search result.

Both existing nationwide original-monitoring and state-search workflows are triggered on launch and retained on their original periodic schedules. The correct next scalable improvement is to add a **federal jurisdiction/agency research universe** (rather than treating state-level source coverage as an agency census), then prioritize authentic original documents for unreviewed entities. U.S. Census 2026 Gazetteer places and counties and DOJ BJS agency census are potential official baselines with different scope; geography alone is not a law enforcement agency.

This release neither changes the public camera map nor produces legal-compliance rankings or automated policy adoption emails.
