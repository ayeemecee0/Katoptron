# M11 · Distinguish old government-source acquisition holds from authoritative program changes

Date of source-recheck baseline: October 27, 2026. Government original recheck: [Actions run 40634047460](https://github.com/ayeemecee0/Katoptron/actions/runs/40634047460).

The earlier national first-party source crawler accurately logged **12 held original government URLs** as a dated acquisition snapshot. That is NOT 12 agencies without Flock, and does NOT mean all 12 URLs must remain forever actionable. Review historical source records rather than overwriting them.

## Three individually re-evaluated entries

1. **Lafayette, Colorado**: Historical Flock program URL was held for redirect. The City has since published a separate **source-hash-verified** October 22, 2026 announcement of Flock termination and camera-removal plans. This newer municipal publication supersedes the old URL as the relevant current municipality-stated program direction. **The original URL remains uninspected; this is source lifecycle reconciliation, not independent proof the contract was terminated or the hardware removed.** One old stale status lead can be closed as superseded.
2. **Panama City Beach, Florida**: Original September 1, 2026 police chief statement is publicly discoverable on the [official city webpage](https://www.pcbfl.gov/m/NewsFlash/Home/Detail/38), but direct read-only CI fetch still returned HTTP error. The September suspension and prospective removal are *city statements*. Do not upgrade the original original-body review or claim physical camera removal without successful source acquisition, hash and individual fact checking. Still held.
3. **Raleigh, North Carolina**: Original [government Flock FAQ](https://raleighnc.gov/services/how-does-raleigh-use-flock-cameras) is publicly discoverable through web search but CI still returned HTTP error; it describes RPD's own ALPR disclosures, 30-day routine retention and annual spending. Still held for direct source byte/claim verification. No current backend telemetry, sharing permission or camera location is inferred.

Outcomes: **12 historical holds, 1 superseded, 11 unresolved; zero new publisher-HTML hashes independently verified by the recheck**. Original historical receipts remain unchanged and the current source-review ledger is separate.

## New release

- scripts/recheck_three_held_government_originals.py: exact-source historical receipt validation, bounded official-host HTML acquisition, literal evidence anchor requirement, and source-authenticated supersession to the already verified Colorado city termination record.
- data/held-government-source-resolution-2026-10-27.json: immutable source-recheck receipt with current disposition and source specificity.
- government-source-hold-reviews.js: allowlisted identities, hash of superseding original, and fail-closed status/uncertainty validations.
- government-source-hold-review.html: mobile-accessible original review lifecycle, linked from existing Agency Evidence Conversion and 51-state national matrix.
- GitHub Actions: weekly government recheck; separate browser source-status acceptance test.

All statuses describe **source document availability**. Do not infer an agency's installed camera fleet, platform access, completed device removal, Flock vendor policies, or lack of Flock from a 403 response.

### Subsequent P0 blockers

Resolve the other **nine** government original-source acquisition holds, along with Florida and North Carolina. Use authenticated original municipal publisher paths, page-specific official documents and documented authority-preserving redirects. Prefer existing source-audited original government records to infer nothing about current operations until supported by new primary evidence.
