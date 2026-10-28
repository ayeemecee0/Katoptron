# M10 · Original-source agency dossiers inside Agency X-Ray

**Implemented:** October 27, 2026.

## What changes

The nationwide research index already covers 50 states and Washington, D.C., but nationwide publisher coverage is not itself agency-level evidence. Page-reviewed originals were previously distributed among separate Washington, Nebraska, Oklahoma, Rhode Island/South Dakota and original-government document views.

[Agency X-Ray](../agency-xray.html) now has a separate **verified original-government agency dossiers** search that works independently of the camera map, locality search, portal identity matching and the signed-contract lookup. It presents ten original-page-reviewed government documents grouped into **six exact source-publisher identities**, each with original PDF links, reviewed page numbers, original SHA-256 and a fixed document/status type:

| Exact agency or government contracting party | State | Number of reviewed original documents | Distinction |
| --- | --- | ---: | --- |
| Oklahoma City | OK | 4 | 2026 signed city/vendor amendment; approved renewal; staff memo that is not a vote; signed funds availability that is not payment |
| Dakota County Sheriff's Office | NE | 1 | 2025 agency-authored aggregate counters; period end is not document publication date |
| Providence Police Department | RI | 1 | Department-published effective General Order 350.05, September 4, 2026 |
| Brookings Police Department | SD | 1 | September 22, 2026 revised department policy with chief signature |
| Kittitas Police Department | WA | 1 | Four-page original visibly marked **DRAFT**, not proven adopted |
| Moline Police Department | IL | 2 | Dated signed 2024 order plus signed September 2026 future pause/removal terms, not confirmation of completed shutdown |

**Total: six identities, ten documents.** Counts are source documents, not camera units or operational agencies. The Moline 2024 order's equipment count is historical contractual scope; the later signed removal agreement does not establish that each camera was removed. The Oklahoma City 109 partner figure is a dated city self-report, not 109 independently corroborated bilateral sharing relationships.

The new typed [agency dossier adapter](../verified-agency-dossiers.js) *reuses* the existing independently reviewed ledgers and their validation modules. It does not append these records to a city based on fuzzy spelling or infer that a local police policy proves the city operates a specific Flock camera. Each source document retains its original verified pages and role. A signed amendment, staff recommendation, completed annual aggregate and proposed policy are never combined into a fabricated unified operating status.

## Reproducibility and controls

- [Unit regression](../scripts/test_verified_agency_dossiers.cjs) verifies the six exact keys, source citation pages, original counts, and immutable source boundaries; it rejects forged camera coordinates, manufacturer/current-status claims, alternate government URLs, modified signed/draft status or modified aggregate counts.
- [Mobile Chromium acceptance](../scripts/smoke_verified_agency_dossiers.cjs) covers the 390-pixel-wide Agency X-Ray display, original-only agency search, government page citations, date types, direct deep links such as `agency-xray.html?original=moline-police-il`, reset control and separation from the locality evidence group.
- The existing [automated accountability acceptance workflow](../.github/workflows/audit_accountability_acceptance.yml) runs both regressions on changes. If any required source ledger is missing or invalid, the standalone original-source section fails closed and does not show unsupported policy or device claims.
- The dataset retains original publisher government URLs and source dates. The user-facing labels distinguish policy effective date, source date, draft manual imprint and aggregate *period end*, because those dates have very different evidentiary meanings.

## What remains unresolved

This is an initial **six-agency cross-index**, not a nationwide agency-by-agency census. There are far more original records in Minnesota, Washington and other monitored sources awaiting exact identity reconciliation and a source-specific integration. The national source acquisition workflow still has held URLs, incomplete per-state original-document depth and no automatic verified camera location publication from paperwork alone.

Next priority: adapt the same exact-agency source index to remaining individually original-page-verified Washington and Minnesota agency records, keeping issuer aliases, independent-audit snapshots and draft/non-Flock records in separate evidence tiers. This will expand useful Agency X-Ray coverage without weakening verification.
