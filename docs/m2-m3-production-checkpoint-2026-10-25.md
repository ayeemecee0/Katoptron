# Katoptron M2/M3 continuation acceptance checkpoint — October 25–26, 2026

> **Latest October 26 update:** M2 Discovery **engineering scope signed off at 100%** after migrations 135–137 and original-doc pipeline/owner-only review acceptance. The historical 92% value below describes the earlier checkpoint. National source and camera evidence remain substantially incomplete. See [M2 engineering sign-off](./m2-discovery-engineering-signoff-2026-10-26.md). M3 source-specific verification remains separately open.


## M1–M3 scope
- M1 Foundation: **100% engineering scope signed off** in `docs/m1-foundation-engineering-signoff-2026-10-25.md`. Not full production-owner operational sign-off.
- M2 Discovery: prior **92% estimate retained**. Source acquisition and PDF-byte provenance now work, but independently verified document contents, nationwide agency publisher evidence and new GIS sources remain incomplete.
- M3 Evidence Verification: prior **92% estimate retained**. Generic LPR sources now fail closed in Flock-only route evidence. Complete source-specific external agency verification is still missing.

Percentages are carried-forward engineering estimates, not independently assessed measured completion scores. Do not raise them merely because tests pass.

## M3 source Flock label boundary deployed
- PR https://github.com/ayeemecee0/Katoptron/pull/6 merged on main: commit `ea3f4acda88221812e79f3fc7337aa7f36996e34`.
- Migration `131_positive_flock_source_label_route_gate.sql` applied to production with a rolled-back rehearsal and post-migration regression.
- Added per-record `source_flock_label_status`, with **default unconfirmed**, explicit source-level `source_flock_identified` and `generic_lpr` classifications, and an immutable route-label UPDATE guard. This is a source-label claim, not per-device serial/manufacturer verification or operational status.
- Live counts immediately after deployment: **293 government GIS positions from seven positively Flock-labeled sources**, **23 government GIS generic LPR positions from Live Oak TX**, **316 total government source-mapped locations** (eight approved sources). The generic 23 remain shown on the documented map but do not qualify for Flock-only route comparisons.
- Added frontend gate and negative JS tests; complete integration validation, browser smoke, community map and Pages deployment passed on merged commit.

## M2 government-original PDF byte provenance deployed
- PR https://github.com/ayeemecee0/Katoptron/pull/7 merged on main: commit `344138dff745c67f5d69a3cf409c24191a6538bc`.
- Migration `132_private_original_government_pdf_bytes_receipts.sql` applied in production after rolled-back SQL and RLS rehearsals.
- Added scheduled private `observe_original_government_pdfs.py` worker. It selects original-government same-host HTTPS PDF leads, safely downloads at most 12 bounded PDFs per run, validates PDF header/EOF and content media type, records ONLY SHA-256/size and retrieval timestamp, and uses a private retry ledger to avoid repeating failed links and starving unattempted URLs.
- Raw PDF bytes, text and speculative source claims are not published or stored by the worker. A fetched PDF is **not** an independently reviewed document. No signed contracts, sharing permissions, policy changes, installed equipment or license plate searches can be inferred.
- Public acquisition dashboard now explicitly reports `pdf_downloaded_unreviewed_documents`, separate from content-verified documents; raw link and receipt tables remain private under RLS.
- First merged workflow https://github.com/ayeemecee0/Katoptron/actions/runs/40273612095 **passed**.
- Production first-run results: **12 links attempted, 10 successfully observed PDF bytes, 2 held fetch errors**. Of 10: 7 labelled meeting records, 2 policy leads, 1 contract lead. These are **document link classifications, not independently verified contents**.
- The source registry still has **74 document hyperlink leads**: 47 meeting records, 15 policies, 7 audit links, 3 contract links and 2 sharing export links. **Zero** reached `document_content_verified` in this continuation.
- Complete validation, community map and GitHub Pages deployment passed on M2 merged commit (run https://github.com/ayeemecee0/Katoptron/actions/runs/40273612213).

## Real priorities to close M2/M3
1. Original-content verification of retrieved government PDFs: independently substantiate specific contract parties, signatures, action dates, spending figures, policy effective dates and sharing list direction. A successful SHA observation is the start of document review, not the end. Preserve private access limitations and separate original-source dates from real-world events.
2. Review the six GIS candidates missing original-agency endorsement. Existing unendorsed third-party ArcGIS org titles are not independently authenticated municipality camera inventories.
3. Obtain qualifying new city/state Flock GIS or original map metadata to improve coverage, without merging duplicate observations or invented points.
4. Resolve external source evidence for held Menifee 27 positions, Shelbyville 12 source-attributed observations, and Monterey government original camera-map PDF. Missing evidence should remain a documented hold, not a reason to change source classifications.
5. Keep original GIS source freshness/withdrawal tests, source-label regression tests and PDF byte-vs-fact separation as release gates.

## Policy and scope boundaries
No camera coordinates were newly approved by this checkpoint. All routes remain synthetic and source-limited; map and route counts are not real-time read/detection counts. Community observations, secondary vendor portal network, original verified government publisher sharing sources, and GIS camera positions remain separate evidence tiers. Full launch requires independent M9 operational and human acceptance gates.
