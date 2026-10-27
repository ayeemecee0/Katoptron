# M10: Automatic original Minnesota ALPR historical-review queue

**Created October 27, 2026.** This is an original government archive *metadata and receipt* acquisition workflow, not automated authority to publish findings from original PDFs.

## October 27 verified evidence-conversion update

The original queue's first-run numbers below are retained as a historical scanner baseline. After independent page-level review, the active audited-document catalog contains **22** source-pinned originals, the Flock-titled independent-review backlog is **0 of 16**, and the original registry identifies **21** additional same-agency historical or other-vendor candidates. The new historical scanner's source run [40547015500](https://github.com/ayeemecee0/Katoptron/actions/runs/40547015500) successfully generated **12 of 12** selected machine PDF receipts with **zero** automatic publication of content-derived claims.

The remaining **21** items are opportunities for future individual original-page review, **not 21 proven earlier Flock installations or breaches**. The two previously pending West Saint Paul and Wyoming Flock-title originals, along with older Woodbury, Edina and Shakopee ALPR reports, have moved from metadata-only to separately checked original-content findings. Refer to the [source-by-source audit history](./m10-cross-period-original-audit-history-2026-10-27.md).

## Verified acquisition coverage

The first scheduled-scanner test on the live [Minnesota Legislative Reference Library mandated-report listing](https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735) found:

| Measured acquisition stage | Result |
|---|---:|
| State-index report links (official metadata only) | **137** |
| Reports independently reviewed and page-pinned in Katoptron's curated manifest | **17** |
| Flock-named report titles still awaiting individual PDF page review | **2** |
| Additional earlier or other-vendor ALPR titles with exact matches to an already-reviewed agency | **23** |
| First 12 top-priority original PDFs receiving bounded automated hash/page inspection | **10 successful**, **2 unavailable/unreadable in that pass** |
| New substantive facts automatically promoted from machine readings | **0** |

At this **earlier baseline scan**, the two unmatched Flock-title PDFs were West Saint Paul and Wyoming. Both have since been independently reviewed in the October 27 expansion. The other 23 are candidate historical sources, **not 23 confirmed earlier Flock deployments**. A current-state figure cannot be derived by adding state reports or historical device snapshots.

## Automatic operation

The [agency-title matcher](../mn-audit-candidates.js) consumes the published, source-attributed original state index alongside the SHA-256-pinned, separately page-reviewed [audit manifest](../data/verified-independent-audits.json). It requires:

1. Exact HTTPS `www.lrl.mn.gov` original archive PDF path and report ID agreement, trusted metadata classification and valid publication date;
2. a *literal phrase match* to a curator-identified, exact agency name in the original **report title** (with bounded, known abbreviations such as PD or UMN, not a fuzzy city or shared-publisher join);
3. no previously reviewed source URL in the curated catalog; and
4. a unique agency match. Multi-agency/ambiguous or unrecognized older titles do not acquire an inferred agency identity.

Priority is **P0** for unreviewed titles explicitly naming Flock, **P1** for older/other-period same-agency ALPR titles with *unspecified manufacturer*, and **P2** for exact-agency titles naming a different vendor or multiple vendors. These priorities indicate **research order**, not public risk, statutory compliance or live devices.

The [public audit library](../mn-alpr-audits.html) computes the same priorities from current public index records. Its list is immediately updated as the existing weekly official-index import discovers new source links. If the independently reviewed manifest or original registry is unavailable, it displays no inferred candidates.

The [weekly original-source inspector](../scripts/scan_mn_historical_queue.py) runs each Thursday using the [scheduled GitHub workflow](../.github/workflows/scan_mn_historical_queue.yml). It uses the **same JavaScript candidate engine** through a bounded Node subprocess, then fetches up to **12** prioritised original state-hosted PDF documents. It records their SHA-256 digest, page count and byte size, but **does not extract PDF prose** or retain raw PDFs. A failed PDF is reported as `unavailable_needs_recheck`, never removed or treated as evidence of document withdrawal. It writes the queue and machine receipt data to a short-lived **14-day GitHub Actions artifact**, not to a public evidence fact table or a privileged database. To avoid an undownloadable historical PDF permanently consuming a receipt slot, the inspector prioritizes any outstanding P0 Flock-titled reports on each run and rotates the other receipt slots across the remaining P1/P2 source queue by ISO week. Failure remains a per-source *unknown*; other candidates continue to be inspected. No secrets or paid services are required.

## Exclusions and next step

A report title, even one with Flock in parentheses, does not establish page-specific device counts, camera coordinates, operational retention or findings of misconduct. Two reports can only produce a comparable quantitative timeline when the original pages have both been independently inspected and pinned and the same agency, manufacturer, unit and equipment modality are established.

The next evidence-conversion step is to open the **23** exact-agency original candidates, prioritize source periods that make a useful history, separately check source pages and manufacturers, and add individually reviewed, page-cited facts where appropriate. Reports with different vendors may support *qualitative* transitions but never combined camera-count arithmetic.

Run acceptance:
- `node scripts/test_mn_audit_candidates.cjs`
- `python -m unittest discover -s scripts -p 'test_scan_mn_historical_queue.py' -v`
- `python scripts/scan_mn_historical_queue.py` (uses live government archive; writes only local metadata-only CI artifact)
- `node scripts/smoke_mn_alpr_audit_registry.cjs` (Chromium through the existing accountability suite)

This phase uses the existing free-tier GitHub Actions and static GitHub Pages deployment. It does not import plate records, personal routes, private reports or any agency credentials.
