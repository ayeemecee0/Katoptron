# M10 · Rhode Island and South Dakota original government ALPR policies, 2026 versions

**Original government source-page review:** October 27, 2026.

This release converts **two source-linked government policy PDFs** into independently original-page-verified documents in the national evidence library. It does **not** certify actual Flock system settings, installation coordinates or agency compliance. The published policy version is a legal/administrative record, not operational telemetry.

## Rhode Island · Providence Police Department General Order 350.05

[Police policy directory](https://ppd.providenceri.gov/policies-and-procedures/) identifies publicly listed policies as **in effect** and links to [350.05 Automated License Plate Readers](https://ppd.providenceri.gov/350-05-automated-license-plate-readers-alpr-2/). Its current link **redirects on the same official police host** to an original PDF under `/wp-content/uploads/2026/10/`. Katoptron independently qualified and pinned that final [exact official original PDF URL](https://ppd.providenceri.gov/wp-content/uploads/2026/10/350.05-Automated-License-Plate-Readers-ALPR.pdf). Do not use an older April 2026 upload path still visible in indexed search results; it is stale.

**Document:** Ten pages, General Order 350.05, with displayed issue and **effective date September 4, 2026**, superseding earlier listed issue dates November 25, 2025 and July 27, 2022.

- **Page 1:** identifies General Order number and exact issue/effective date. The department's own public directory describes this as an effective policy, unlike a draft.
- **Page 7:** expressly names **Flock Safety** as an ALPR data-hosting vendor, sets the written routine ALPR retention limit at **30 days**, and describes case-specific evidence retention exceptions. It also prohibits specified use of the system for federal immigration enforcement except where judicial warrant requirements are met. No independent enforcement audit is implied.
- **Page 8:** calls for a transparency portal with reported hotlist sources, data retention, operational-camera **counts**, partner organizations and aggregated 30-day read/search totals; it directs quarterly internal ALPR-search sampling audits. These published duties are not evidence that the portal or every quarterly audit has been completed.
- **Page 9:** describes procedures for written, approved law-enforcement data requests, prohibition of certain sharing for federal immigration enforcement, and reporting to City Council. A written permission rule is not proof of individual external agency access or live sharing connections.

**SHA-256 of original 10-page PDF:** `74b04c3c5b3f7c6fba013ea205e23279213efd20247be9039acb8cd8e7716f46`. **235,578 bytes**. Original pages independently visually reviewed: **1, 7, 8, 9**.

## South Dakota · Brookings Police Department Policy 13D1

[Original Brookings government ALPR program page](https://www.cityofbrookings-sd.gov/941/Automated-License-Plate-Readers-ALPRs) explicitly states the police department has partnered with Flock Safety. It links its [6-page Policy 13D1](https://www.cityofbrookings-sd.gov/DocumentCenter/View/20501/Policy-13D1---Automated-License-Plate-Recognition-System), published as a raster-scanned original. The policy itself is vendor-neutral ALPR language and must not independently be interpreted as a specific equipment manufacturer certification.

- **Page 1:** visibly identifies Policy 13D1 as the department's ALPR policy, with an original **April 24, 2024 effective date** and **September 22, 2026 revision date**.
- **Page 5:** directs ordinary ALPR reads and hits to be maintained for a **maximum of 30 days**, with investigative retention exceptions and limits on release to non-law-enforcement recipients. It directs an **internal review every 30 days** of database searches and hotlist use. A duty to audit does not certify that every audit was completed.
- **Page 6:** carries the visibly signed approval of the police chief on the city-hosted revision. This is evidence of a signed departmental policy, not independent assurance of implementation.

**SHA-256 of original 6-page scanned PDF:** `2c47881c232c5cb46dd110bf687770371982821798bcb47feebbcb5fc3553df2`. **330,030 bytes**. Original pages independently visually reviewed: **1, 5, 6**. All six pages are in the original PDF hash; only listed pages are quoted as reviewed policy findings.

## Verification and publication architecture

- Original [policy evidence manifest](../data/verified-ri-sd-original-alpr-policies.json) pins exact official source URLs, document dates, issuing agencies, four Providence page render hashes, three Brookings page render hashes, precise reviewed page numbers and source-specific findings.
- [Original government PDF inspection](../scripts/inspect_ri_sd_alpr_original_policies.py) holds unqualified redirects and verifies that both original versions are available, without scraping any raw plate-reader events.
- [Scheduled original source verifier](../scripts/verify_ri_sd_original_policies.py) re-checks exact PDF SHA-256, complete page count and visually reviewed image fingerprints. Providence additionally has text-layer anchors; Brookings is an image-only original, so it cannot be silently interpreted from missing text or OCR guesses.
- [Negative test suite](../scripts/test_verify_ri_sd_original_policies.py) and [browser catalog guard](../ri-sd-original-policies.js) reject invented camera counts, changed adoption dates, edited original PDFs and unverified sharing or retention settings.
- [National original-source library](../national-audits.html) displays independently source-page-reviewed RI and SD policy versions, with direct original-page links and explicit source/evidence boundaries.

**Limitation:** The original Providence PDF naming Flock is manufacturer-specific written policy evidence; the Brookings website naming Flock is direct agency self-report. Neither is evidence of exact camera coordinates, actual sharing-network edges, independent compliance testing, or live platform retention configuration. Do not publish new map pins from these records.

Next review targets: dated contract documents or real inventory/source coordinates for these departments, and independently authenticated audit results rather than making audit-compliance claims from department policies.
