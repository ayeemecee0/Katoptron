# Recovery of original-government research sources in 11 states · October 29, 2026

## Purpose
The preceding operational check tested 59 curated publisher URLs in 51 state jurisdictions, with 46 accessible and 13 held; 11 states had no accessible curated original at that time. This change **adds**, rather than overwrites, an independently located alternative official publisher source in each of the 11 affected states. No historical source URL or last-known-good hash is erased, and no recovery candidate is counted accessible until the strict remote source monitor successfully retrieves it.

The supplemental original-source registry is `data/nationwide-recovery-government-originals-2026-10-29.json`. It contains 11 entries, each with documented issuer, source URL, source type and a limitation. Together with the prior 45 seeded and 14 curated legacy sources, the monitor now attempts **70 government original URLs across all 50 states and DC**. Access to an alternative source solves a state-level source-health gap *only when that alternative is independently reached and parsed in the live scheduled run*. It never establishes statewide Flock coverage.

| State | Original-government replacement category | Distinction that must be preserved |
| --- | --- | --- |
| CO | Routt County sheriff Flock termination announcement | Agency announcement does not verify finished vendor termination or all equipment removed |
| FL | Panama City commission 2026 Flock decisions | Commission vote does not prove physical equipment removal |
| HI | Hawaii State Legislature 2026 ALPR committee report | Proposed legislative measure, not an enacted policy or Flock procurement |
| IA | Iowa Public Information Board Flock records decision | Government open-records proceeding, not a recent deployment |
| MI | Michigan government Flock procurement catalog | State contract listing not a purchaser invoice or city-specific use |
| MS | Mississippi public procurement notice | Flock proposal/solicitation, not awarded contract or payment |
| NC | Hillsborough town government Flock termination update | Town source statement; no independent completion audit |
| NV | Las Vegas Metropolitan Police Department government transparency page | Agency-authored public index linking Flock information; not independent confirmation of current operations |
| NY | New York Attorney General 2025 law-enforcement oversight report | Recommendations on ALPR/AI disclosures are not enacted law or a local agency Flock contract |
| UT | Utah DPS SIAC technology transparency | State ALPR explanations do not prove that Flock supplied every system |
| WV | West Virginia legislature traffic-camera law | Legal context, not evidence of an agency buying Flock |

## Evidence-review conversion, separate from document availability
The original monitor records dated availability and SHA-256. New fingerprints create baseline receipts, not policy/contract claims. Changed bytes produce `review_nationwide_source_changes.py` review packets. It rejects promotion unless there are:
- A genuine changed original source with authenticated before/after observed hashes.
- Two distinct, independently retrievable original-government versions.
- Exact original-document page numbers and quoted, different relevant wording.
- A named editor, review date, original issuer, why the difference matters, legal/action-status caveat and unresolved questions.
- Explicit editorial approval and the distinction between documentary language and proven wrongdoing or equipment operation.

The review approvals file intentionally starts **empty**. The scheduled job reports its real number of approved documentary differences; *no source change is automatically approved*. Three manually reviewed, **source-attributed government-action research leads** are published separately under `nationwide-research-leads.html`: Panama City, Michigan procurement and Hillsborough. They are not represented as verified before/after content changes or independent confirmations of completed government actions.

No private plate-read data, locations, credentials, FOIA submissions or bulk camera locations are published.

## Next milestones, in value and revenue order
1. **P0 Source reliability:** obtain successful original retrieval in all 11 previously uncovered states and replace any remaining held sources after verification. Measure distinct states with one accessible original, not number of search hits.
2. **P0 Editorial throughput:** verify original before/after versions for the 15 existing changed-source hashes (where original archives actually exist). Approve the first five page-cited documentary differences or explicitly hold them; no fabrication for inaccessible historical content.
3. **P0 Reliable evidence storage:** retain bounded encrypted source-version artifacts and metadata beyond temporary CI cache; record source removal/redirects, editor decisions and reproducible hashes.
4. **P1 Research delivery:** supply 10 new, uniquely source-qualified investigation leads with private researcher filters and opt-in alerts; zero duplicates or historical alert replays.
5. **P1 User validation:** 10 research pilot users, 5 completing a sourced task, 3 independently demonstrating willingness to pay.
6. **P2 Agency completeness:** expand monitoring beyond one original per state and report local agency inventory by original-source provenance, not inferred statewide coverage.
