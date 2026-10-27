# M10: Original-source cross-period ALPR accountability

**October 27 completion update:** The original **21** exact-agency historical review candidates are now all independently examined: **20** are included in the 42-entry page-checked external audit manifest and the remaining Hennepin County 2017 internal report is separately source-verified as an **agency-internal**, not external-independent, publication. The California and Wisconsin expansion is now included in the [current national original-audit methodology](./m10-national-original-audit-acquisition-2026-10-27.md). Earlier numbers below document previous dated engineering checkpoints, not the current review backlog.

**Reviewed October 27, 2026**. Published public agency histories are source-specific and historical. These findings do not establish live devices, a camera map, private vehicle records, or statutory wrongdoing.

## Original-source findings

| Exact agency | Earlier original auditor report | Later original auditor report | Eligible comparison |
|---|---|---|---|
| Woodbury Public Safety | [February 16, 2024, PDF p.2](https://www.lrl.mn.gov/docs/2024/mandated/240350.pdf#page=2), January 2022–December 2023 period, 15 active stationary units in a Flock-system audit | [February 5, 2026, PDF p.2](https://www.lrl.mn.gov/docs/2026/mandated/260248.pdf#page=2), January 2024–December 2025 period, 17 active stationary Flock ALPR units | **+2 difference in separately audited historical stationary device counts.** Not necessarily two new physical cameras, not a present-day deployment count. |
| Shakopee Police Department | [May 2, 2024, PDF p.1](https://www.lrl.mn.gov/docs/2024/mandated/240981.pdf#page=1), March 2022–February 2024 period, Elsag Plate Hunter in three patrol vehicles and no stationary readers | [June 15, 2026, PDF p.1](https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf#page=1), March 2024–April 2026 period, six permanent Flock ALPR locations and Axon squad readers | **Documented technology transition.** Different vendors, units and mobility categories make a combined numeric increase invalid. |

The Shakopee 2026 independent report identifies Elsag termination on January 8, 2025, Axon squad implementation in January 2025 and Flock implementation in June 2025; this detail comes from the later auditor and does not imply continuity across the older and newer audit.

Woodbury's 2024 auditor described a **configured** 30-day Flock data retention period and sampled older reads. The 2026 auditor described a manufacturer-default 30-day setting corroborated by a Flock Vehicle Reads report. These have different verification methods; Katoptron deliberately does not infer an unchanged operational retention policy from the repeated number alone. Later audit titles and report dates are not treated as the observation instant for every device, and neither report proves which named streets currently have cameras.

## Original byte receipts

- Woodbury 2024 official archive: `b2901b1953aad9ae23dbaee126ee5e36df055407ea8724c017ae30c6974d456e`, five pages.
- Shakopee 2024 official archive: `ef940332a5aea9c12614efa16a5f3d694f7f477e815985942cd95ccc3703a5e4`, five pages.

Both SHA-256 receipts were calculated from exact bounded original PDF bytes in [read-only public-source GitHub Action #40524062091](https://github.com/ayeemecee0/Katoptron/actions/runs/40524062091). The curated manifest pins these hashes, exact original URL and reviewed pages; the weekly independent source verifier checks that the original bytes and critical page text remain identical. If a source changes or becomes unavailable, the verifier fails closed. A review queue should re-evaluate the changed original and affected public comparisons.

## Publication rules

The deterministic [cross-period comparison engine](../audit-history.js) requires two distinct reports from the exact same `jurisdiction_key` **and** curated `cross_period.agency_id`, with matching agency names, original HTTPS Minnesota state archive URLs, original reviewed-page evidence and pinned SHA-256 digests. It excludes comparisons when publication dates are invalid or periods overlap; count deltas require the same explicitly typed manufacturer, equipment modality, unit and snapshot measurement definition. Vendor changes produce qualitative events, not math.

Unknown or single-period evidence displays **no comparable pair**, not no policy change. These events do not become a new camera pin, public data-sharing edge, criminal allegation or legal compliance score. All reports link to exact source PDF pages.

## Tests

- `python -m unittest discover -s scripts -p 'test_verify_independent_audit_source.py' -v`
- `node scripts/test_agency_audit_engine.cjs`
- `node scripts/test_audit_history.cjs`
- `node scripts/smoke_agency_audit.cjs`
- `python scripts/verify_independent_audit_source.py` (network/source freshness; original archive only)

The [accountability CI workflow](../.github/workflows/audit_accountability_acceptance.yml) runs engine tests and actual browser cases; the main release smoke remains separate.

## Second original-source expansion: three earlier audit periods, October 27, 2026

Five independently reviewed, original Minnesota auditor PDF reports were added to the page-pinned catalog. Three extend histories already present in Katoptron:

| Agency | Earlier independently reviewed original | Later original | Legitimate finding |
|---|---|---|---|
| Woodbury Public Safety | [Nov. 10, 2021 report, p.2–3](https://www.lrl.mn.gov/docs/2021/mandated/211119.pdf#page=2), described up to **two squad-car ALPR systems** and no stationary readers during **December 2019–June 2021**, with BOSS backend software; the auditor records that the mobile program terminated June 2021 | [Feb. 16, 2024 Flock report](https://www.lrl.mn.gov/docs/2024/mandated/240350.pdf#page=2) reported **15 stationary Flock units** in an audit of January 2022–December 2023 | **Qualitative transition only.** BOSS is software, **not verification of an older hardware manufacturer**. This is distinct from the comparable **15 → 17** stationary Flock observation from Woodbury's two later original reports. |
| Edina Police Department | [Oct. 7, 2021 report, p.2](https://www.lrl.mn.gov/docs/2021/mandated/210885.pdf#page=2), reported **nine squad-car ALPR systems** and **no stationary ALPR units** during the audit, administered through BOSS/PAGIS | [Oct. 15, 2025 Flock report, p.2](https://www.lrl.mn.gov/docs/2025/mandated/251619.pdf#page=2) reported **18 stationary Flock units** | **Qualitative transition only.** The earlier manufacturer is not established, so a numeric cross-manufacturer difference would be invalid. The 2021 report does not state bounded coverage dates: the timeline labels it an **audit snapshot** rather than inventing a full-period range. |
| Shakopee Police Department | [May 8, 2022 report, p.1–3](https://www.lrl.mn.gov/docs/2022/mandated/220708.pdf#page=1), **three Elsag-equipped patrol vehicles** and no stationary readers during February 2020–March 2022 | [May 2, 2024 report](https://www.lrl.mn.gov/docs/2024/mandated/240981.pdf#page=1) separately confirmed the Elsag patrol-reader setup; [2026 report](https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf#page=1) later documents Axon squad and Flock fixed systems | **Independent continuity corroboration** for the earlier Elsag period and a later documented technology transition. No fictitious 2022–2024 change is inserted simply because two audit dates exist. |

The source hash receipts for these newly inspected originals are **Woodbury 2021** `ae0b99580511d52cd46165c10dc3fd5f5582eb4291d47c924fbd4db1f510f986` (4 pages), **Edina 2021** `9eb8d2acd5b3e3e249b1273278d98620671edcb76e6d7b2407b6ed67389e7795` (5 pages), and **Shakopee 2022** `764dd886027d8eb572ab67f828fca3bd2965b3d2e8523c54620d75c9b19dac64` (5 pages). Each matches exact original archive PDF bytes from the [source-inspection GitHub Action](https://github.com/ayeemecee0/Katoptron/actions/runs/40545754341); the independent source verifier separately checks reviewed page text and full SHA-256 before publishing.

## Last two Flock-titled source reviews

The following original Minnesota ALPR reports had previously been private **machine-fingerprint-only** receipts. They are now individually inspected, associated with exact agency dossier keys and pinned to checked source-page statements:

| Agency | Original audit and source period | Independently reported historical observation |
|---|---|---|
| [West Saint Paul Police Department](https://www.lrl.mn.gov/docs/2026/mandated/261167.pdf#page=2) | July 30, 2026; September 2025–June 2026 | **10 stationary Flock ALPR units** and no Flock mobile units at auditor's visit (p.2), default **30-day** retention in the examined Flock system (p.2), May 2026 sharing-request sampling documented by agency and justification (p.3). This does **not** establish active cameras after June–July 2026 or current permissions. |
| [Wyoming Police Department](https://www.lrl.mn.gov/docs/2026/mandated/261268.pdf#page=2) | August 30, 2026; August 2025–July 2026 | **4 stationary Flock ALPR units** and no Flock mobile units at the time of the audit (p.2), auditor-observed default **30-day** retention (p.2), and an auditor statement that **three other agencies had written sharing agreements** during the audited period (p.3). The reviewed passage does **not** identify those three agencies and does not confirm current data-sharing edges. |

Their direct original PDF SHA-256 digests are **West Saint Paul** `5f1b4804cc505436d4cb297f76a8767052f73eb6643210c3c36a4d116d09ba9e` and **Wyoming** `19f39c1f82e656aed2a7c2a8ee7e69a425fef30e43043b4d86473caee8152f6f`, both five pages. Exact original PDFs and page-specific passages were checked by the [October 27 inspection action](https://github.com/ayeemecee0/Katoptron/actions/runs/40545754341), followed by [source freshness verifier CI](https://github.com/ayeemecee0/Katoptron/actions/runs/40547029109).

**Reviewed coverage after this pass:** **22** page-reviewed original audit reports across **17** exact reviewed agency dossiers; **16/16** state-index titles explicitly naming Flock are now independently page-reviewed, with **6** additional vendor-unspecified historical titles/periods (some independently identifying Flock inside the report). Counts are *historical source documents*, not a count of government camera locations, device installations, violations or current operators.

## Expansion path

Before claiming broader same-agency historical trends, independently review prior original reports and verify that each count measures identical vendor/deployment classes. Additional Minnesota archive reports for Woodbury and Shakopee from 2017–2022 are visible as **registry metadata**, not automatically admissible Flock-specific comparisons. Next consider both additional repeated-audit agencies and historical published changes to written ALPR policy, with page-cited policy revisions. Do not infer that all historical vendor types were Flock.
