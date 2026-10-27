# M10: Original-source cross-period ALPR accountability

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

## Expansion path

Before claiming broader same-agency historical trends, independently review prior original reports and verify that each count measures identical vendor/deployment classes. Additional Minnesota archive reports for Woodbury and Shakopee from 2017–2022 are visible as **registry metadata**, not automatically admissible Flock-specific comparisons. Next consider both additional repeated-audit agencies and historical published changes to written ALPR policy, with page-cited policy revisions. Do not infer that all historical vendor types were Flock.
