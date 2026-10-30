# Historical original-source recovery: actionable issuer research, 2026-10-30

**Scope:** source-attributed research questions and retrieval provenance. This is **not** an automated source-version finding, a verified hardware inventory, an approved investigation, or a statement that expired URLs were recovered.

## Two independent retrieval observations

- [Main-branch original-source monitor run 41084781918](https://github.com/ayeemecee0/Katoptron/actions/runs/41084781918), at 2026-10-30 15:54 UTC, authenticated **13 of 19** historical originals by successful publisher retrieval and original-byte SHA-256. Six historical IDs remained held: CO, MI, OH, NY, IL (Naperville) and WI (Sheboygan).
- [PR regression run 41086757265](https://github.com/ayeemecee0/Katoptron/actions/runs/41086757265), at 2026-10-30 16:07 UTC, fetched **11 of 19** historical originals. Publisher access fluctuated. The earlier 13 successful receipts remain historical evidence; the later result must not erase them. The PR regression checks passed.
- A 2026-10-30 code improvement preserves immutable SHA-256-addressed previously authenticated versions when source content changes and identifies previously observed hash pairs. GitHub cache remains best-effort, not permanent archival storage.
- **All six unresolved old URL identities remain held.** Modern publisher indexes are separate sources, not interchangeable with the original pages. There is **no newly approved original-version change** or derived email alert from this casebook.

## Documented investigative questions (original issuer, dated)

### Ohio: statewide software access, not documented camera procurement

**Original issuer:** Ohio Controlling Board, [Request DPS0105268](https://controllingboard.obm.ohio.gov/Print/PrintCBRequest?id=511a4ceb-9a1e-420f-b949-2257330dbf4a), approved at its **June 3, 2024** meeting. The public record identifies a waiver for **$90,000 FY2024 and $90,000 FY2025**, requesting a Flock Group license-plate reader network subscription supporting unlimited users. The request's explanation states that the Highway Patrol would continue its existing ELSAG-Leonardo cameras and that the Flock subscription avoided the need to buy/install more cameras to use Flock's network.

**Why this matters:** Claims that Ohio spent $180,000 on **new Flock camera installations** cannot be inferred from this record. It documents approved subscription authority; it does not by itself verify disbursement or ongoing usage.

**Open evidence:** Original Controlling Board HTML could not be read and hashed in the automated 2026-10-30 monitor (network error); the site's indexed page does not provide a machine-authenticated retrieval receipt. Obtain the listed signed contract **DPS020262**, sole-source justification and agency payment/renewal records, then hash exact original files before any publisher-authenticated finding is promoted. Do not infer signed contract terms merely from its attachment filename.

### Colorado: budget defunding versus completed contract termination

**Original issuers:** City of Lafayette [October 20, 2026 statement](https://www.lafayetteco.gov/m/newsflash/home/detail/10277) and [October 20 council meeting recap](https://www.lafayetteco.gov/CivicSend/ViewMessage/message/304072). The city says its 2027 budget removed funding for Flock and that use would end while it began early termination and would cover its **30 city-contracted cameras** pending removal. Its city council recap reports second-reading approval, **6-0**, of **Ordinance 18B** with no 2027 Flock appropriation.

**Why this matters:** Dated budget and city leadership actions are independently visible on separate original city pages. They do **not** prove Flock accepted a termination, that all contracted cameras were removed, or the status of independently contracted cameras.

**Open evidence:** Obtain signed cancellation, vendor acknowledgment, completed camera-removal documentation and a dated aggregate data-access cutoff. The old `/4282/Flock-Safety-ALPR-Program` page redirects to a police transparency index; the replacement is **not** established to contain the same historical text.

### Wisconsin: public termination request, not yet a documented completed termination

**Original issuer:** City of Sheboygan [August 25, 2026 release](https://www.sheboyganwi.gov/m/newsflash/Home/Detail/94). Police leadership announced intent to ask the September 8 Common Council to terminate the city's Flock agreement, and reported **15** city-program Flock cameras.

**Why this matters:** An announced request does not establish the later council vote, contract cancellation, equipment removal or access cutoff.

**Open evidence:** September 8 council minutes/vote, executed cancellation and decommissioning record. The original municipal URL returned HTTP **403** in the automated monitor. A separately readable public webpage is **not** a successful hash-verified automated fetch.

### Illinois: current and prior policy availability without approved clause changes

**Original issuer:** City of Naperville [current ALPR transparency page](https://www.naperville.il.us/589/Automated-License-Plate-Readers). The publisher links current and preceding PDF policy versions and describes a routine 30-day retention period subject to exceptions.

**Why this matters:** A matched and page-cited before/after comparison could establish specific document wording changes, but the availability of two links does not establish when or how those changes took legal effect.

**Open evidence:** Preserve original PDF bytes, effective dates and exact page references, complete independent editorial review for ten pending comparisons, and document what agency practice remains unknown. The old monitored publisher URL still returned **404**. No preapproval of those comparisons is warranted.

## Remaining original-URL blockers

| State / source | Last reported failure | Evidence threshold to resolve |
| --- | --- | --- |
| Colorado / Lafayette | 301 redirect to a different publisher page | Original archived version or explicit issuer-authorized replacement mapping, with version identity |
| Michigan / June 3, 2025 state minutes PDF | 403 | Exact meeting minutes from publisher, byte SHA and document identity |
| Ohio / State Highway Patrol request | network timeout | Actual issuer HTML or attached signed original, HTTP retrieval and byte SHA |
| New York / 2021 MPTC model policy | 404 on watched host/path | Original 2021 model PDF from issuer; 2022 model is **not** the same edition |
| Illinois / Naperville historical transparency | 404 | Issuer-original historical content or verifiable replacement mapping |
| Wisconsin / Sheboygan announcement | 403 | Original publisher HTML bytes through reliable permitted retrieval or official equivalent with distinct source identity |

## Next development thresholds

1. **P0** Recover the six never-signed-off historical originals or document permanent publisher absence with exact official replacement mappings and version evidence; do **not** convert related links into false recovered-original counts.
2. **P0** Obtain signed Ohio attachment **DPS020262** and checksum the official bytes; distinguish approved subscription spend from actual payment and camera purchases.
3. **P0** Move last-good versions and deduplication ledger from best-effort Actions cache to a retained, access-controlled archive; test restoration after a cache eviction.
4. **P1** Advance the Colorado, Ohio, Sheboygan and Naperville questions to independent government records and human-reviewed, dated findings, each with a concrete unresolved question and source/pagination anchors where applicable.
5. **P1** Produce ten page-cited and independently reviewed document-version comparisons; deliver research alerts only for genuinely approved new events with duplicate-safe receipts.
