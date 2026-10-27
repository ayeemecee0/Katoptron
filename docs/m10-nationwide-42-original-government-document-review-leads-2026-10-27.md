# M10 · Nationwide discovery of original government document links behind seeded publishers

Inspected October 27, 2026. Based on the nationwide [51-jurisdiction original-government source registry](../data/nationwide-government-jurisdiction-registry.json) and the [43 exact original source receipts](../data/nationwide-original-government-source-receipts.json).

[GitHub Actions #40601673641](https://github.com/ayeemecee0/Katoptron/actions/runs/40601673641) successfully ran the [outbound document link discovery workflow](../.github/workflows/discover_nationwide_original_document_links.yml). The workflow now recurs weekly and stores a 21-day review-queue artifact. Original-page sources must be checked separately before publishing evidence.

## Results measured

| Pipeline measure | Result |
| --- | ---: |
| US state and DC research jurisdictions enrolled | **51** |
| Curated original government URLs used as starting points | **43 new + 14 preexisting** |
| Newly seeded original government HTML pages inspected for embedded document links | **28** |
| Public original government seeds unavailable for link extraction | **6** |
| Other source seeds: direct government PDFs not treated as HTML link indexes | **9** |
| **Additional official-host ALPR/Flock-related document links queued** | **42** |
| States with newly linked review candidates | **11** |
| Claims automatically promoted into verified contracts, policies or installed Flock hardware | **0** |

The initial raw crawler included navigation links for translated language versions and page self-links. These were removed and a subsequent successful workflow found 42 distinct candidate links. Candidate links are **same-government-host anchors**, not yet re-fetched authenticated original document contents; a label/filename does not establish an adopted policy or signed agreement.

## High-value original link-review priorities

The sources below are **review candidates**, not published assertions about their content or present-day operational status.

| Priority | Government-linked original publication | Evidence task |
| --- | --- | --- |
| P0 | [Oklahoma City August 18, 2026 Flock amendment](https://www.okc.gov/files/assets/city/v/1/police/documents/flock/flock-amendment-august-2026.pdf) | Verify actual original PDF bytes, signature/date, amendment terms, earlier agreement relationship and equipment scope |
| P0 | [Oklahoma City August 18, 2026 council memorandum](https://www.okc.gov/files/assets/city/v/1/police/documents/flock/flock-council-memo-august-2026.pdf) | Distinguish staff recommendation, enacted council action and what was actually authorized |
| P0 | [Oklahoma City Flock renewal letter](https://www.okc.gov/files/assets/city/v/1/police/documents/flock/flock-renewal-letter-august-2026.pdf) | Distinguish proposal, approval and current contract renewal |
| P0 | [Nebraska Buffalo County sheriff's 2025 year-end Flock ALPR report](https://ncc.nebraska.gov/sites/default/files/Buffalo%20County%20Sheriff%27s%20Office%20Flock%20ALPR_Data_%20January%201%202025%20-%20December%2031%202025%20Year%20Report.pdf) | Source-page audit of agency-authored aggregate collection/search statistics and dates, without private plate reads |
| P0 | [Nebraska Dakota County 2025 Flock report](https://ncc.nebraska.gov/sites/default/files/Dakota%20County%20FLOCK%20REPORT%202025%20TO%20STATE.pdf) | Original source identity and page-specific aggregate activity record |
| P1 | [Lexington, Kentucky LPR audit index](https://www.lexingtonky.gov/license-plate-reader-audits) | Check source-date independent vs police-authored audits, equipment vendor attribution |
| P1 | [Robbinsdale, Minnesota ALPR Policy 427](https://www.robbinsdalemn.gov/DocumentCenter/View/2520/Robbinsdale-Police-Department-Policy-Manual-Policy-427) | Original PDF content, lifecycle, retention/sharing rules and true policy adoption |
| P1 | [Providence, Rhode Island Police ALPR Policy 350.05](https://ppd.providenceri.gov/wp-content/uploads/2026/04/350.05-Automated-License-Plate-Readers-ALPR.pdf) | Byte/page verification and vendor identity qualification |
| P1 | [Brookings, South Dakota Police ALPR Policy 13D1](https://cityofbrookings-sd.gov/DocumentCenter/View/20501/Policy-13D1---Automated-License-Plate-Recognition-System) | Agency-authored published policy and retention/sharing controls |
| P1 | [Oklahoma City August 18 ALPR presentation](https://www.okc.gov/files/assets/city/v/1/police/documents/flock/okcpd-alpr-presentation-august-2026.pdf) | Separate presentation assertions from adopted terms |
| P1 | [Nebraska state police 2025 ALPR collection report](https://ncc.nebraska.gov/sites/default/files/NSP%202025%20ALPR%20Data%20Collection.pdf) | Aggregate original agency report, not independently audited Flock-only statistics |

**Important:** Nebraska's state reporting page links Flock and non-Flock technologies, and some reports were revised. Treat versions and vendors separately. An original link carrying “Flock” in its title has a stronger research lead than an arbitrary ALPR policy, but it is not confirmation of installed equipment or current live agency access.

## Safeguards

The [original government link collector](../scripts/discover_nationwide_original_document_links.py) follows only links on the **same exact originally seeded government host**, does not download candidate documents, rejects non-government/offsite/private search-log/plate-read URLs, ignores language selector variants and duplicate links, caps both source response size and candidate count, and stores source attribution plus explicitly false flags for installation, policy adoption and content review. Each candidate must enter a separate original-PDF/page/content verification path.

The previous broad 51-state RSS search provider returned **zero qualified leads**, even though the program executed all 51 queries. The new hosted-source extraction is the functional acquisition path and generated 42 usable document *leads*, not 42 independently verified Flock findings. Research efforts are still not complete nationwide: 11 states yielded newly linked candidates on this first pass, and the broader project must continue recruiting authentic government publishers, including jurisdictions with no Flock-specific original.

## Next development priorities

1. Independently verify Oklahoma City's original August 2026 amendment, council memo and renewal papers; publish source-dated outcomes and distinguish any adopted decisions.
2. Verify and import Nebraska's agency-authored ALPR aggregate reports without erroneously counting other-vendor systems or private plate records.
3. Expand per-state government-publisher acquisition in states with only statutes or unadopted bills, then connect genuine independently verified documents to Agency X-Ray and the nationwide accountability timeline.
4. Keep camera-map publication rules separate from documentation and statistical evidence, with verifiable equipment locations or clearly labeled approximate reports only.
