# M10 · Nebraska 2025 state-filed ALPR aggregate, independently reviewed original

Reviewed October 27, 2026. Publisher: Nebraska Commission on Law Enforcement and Criminal Justice, which hosts annual reports submitted by individual police/sheriff agencies.

## Individually visually reviewed original: Dakota County Sheriff's Office

**Original:** [Dakota County FLOCK REPORT 2025 TO STATE](https://ncc.nebraska.gov/sites/default/files/Dakota%20County%20FLOCK%20REPORT%202025%20TO%20STATE.pdf#page=1), one government-hosted PDF page. The official original is SHA-256 `441961503a77e7838717713448426df07cd59aec4146f92af01830d4e3817eae`, 136,060 bytes; a separately rendered source-page image has SHA-256 `02686973bfb2c942e98624048bdee0f9a3d54b241b2af432211c69506495fb27`. [Independent CI inspection #40602190851](https://github.com/ayeemecee0/Katoptron/actions/runs/40602190851) and [original hash/render verifier #40602327164](https://github.com/ayeemecee0/Katoptron/actions/runs/40602327164) passed.

The report identifies **Dakota County Sheriff's Office** and a reporting period of **January 1 through December 31, 2025**. The original page lists these **agency-reported aggregate statistics**:

| Report field | 2025 total |
| --- | ---: |
| NCIC list confirmed matches | 43 |
| NCIC list non-correlated matches | 0 |
| Plate numbers manually entered | 126 |
| Manually entered confirmed matches | 19 |
| Manually entered non-correlated matches | 1 |

**What this does not show:** The report was *authored/submitted by the agency*, not an independently certified audit. These counts are not numbers of crimes solved, arrests, installed cameras or license plates collected. The PDF filename mentions Flock; the actual one-page report does **not independently prove the camera manufacturer, coordinates, current active network, compliance with retention rules, or data sharing**. No individual plate records, dates of vehicle movements or police user logs have been requested or obtained.

## Explicit original held: Buffalo County Sheriff's Office

The public Nebraska government index links to a PDF named [Buffalo County Sheriff's Office Flock ALPR Data January 1–December 31, 2025 Year Report](https://ncc.nebraska.gov/sites/default/files/Buffalo%20County%20Sheriff%27s%20Office%20Flock%20ALPR_Data_%20January%201%202025%20-%20December%2031%202025%20Year%20Report.pdf). Its rendered source page displays an **unfilled reporting form** with blank agency/metric fields. The filename alone is not evidence that Buffalo County reported any particular number. The PDF remains **held** from numeric findings until its original URL and a populated government-authored report are verified.

## Implemented safeguards

- [Nebraska strict original evidence manifest](../data/verified-nebraska-original-aggregate-reports.json) contains one approved Dakota record and a separate Buffalo hold.
- [Original verifier](../scripts/verify_nebraska_dakota_2025_aggregate.py) rechecks the exact public government PDF bytes and separately rendered page hash on every CI run and weekly. Changed original bytes/pages must be re-reviewed before reporting new figures.
- [Public national original-source library](../national-audits.html) has a distinct agency-authored aggregate section, outside independent oversight and contract findings, with direct original page-1 access.
- [Negative data validation](../scripts/test_verify_nebraska_dakota_2025_aggregate.py) and [JS boundary tests](../scripts/test_nebraska_original_aggregate.cjs) reject replaced hashes, changed annual figures, unreviewed manufacturer/equipment counts, invented GPS points, and promotion of the blank Buffalo report.

This adds an **individually verified historic aggregate document**, not nationwide Flock camera coverage. It is a factual advancement in Nebraska evidence depth, not a source-discovery-only addition.
