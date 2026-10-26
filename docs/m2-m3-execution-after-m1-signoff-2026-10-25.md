# Katoptron M2/M3 execution after M1 sign-off — October 25, 2026

## Engineering milestone state
- [M1 foundation engineering ACCEPTED (100% scope)](./m1-foundation-engineering-signoff-2026-10-25.md). Production launch controls remain separately gated.
- M2 discovery: development continues, no exhaustive national camera coverage claim.
- M3 evidence verification: development continues, conditional manufacturer claims cannot be upgraded from a generic ALPR map.

## M2: actual due-source starvation fixed
The previous scheduled GIS workflow called `reconcile_flock_gis_candidate_lifecycle()` BEFORE classifying overdue candidates. Migration 111's function advances unchanged overdue dates by 30/90 days, meaning a source could reach its due date and get postponed automatically instead of inspected. This is a substantive research-backlog liveness defect, not an external-source verification failure.

- [Migration 112](../supabase/migrations/112_due_candidate_preflight_without_cooldown.sql) introduces owner-restricted/service-role-only `reactivate_changed_gis_source_evidence()`. It inserts new candidates and opens changed original-agency metadata, but **does not advance unchanged due dates**.
- [Candidate reconciliation worker](../scripts/reconcile_gis_candidate_lifecycle.py) supports `--reactivate-only`; its existing full finalization remains after triage.
- [Scheduled triage workflow](../.github/workflows/triage_gis_verification_backlog.yml) now runs **reactivation-only → inspect due candidates → assign cooldown**.
- [Rollback-only SQL acceptance](../scripts/test_due_source_triage_preflight.sql) passed against live Supabase: newly discovered leads due now; unchanged due lead stays due; a completed pass schedules cooldown; meaningful government link changes reopen it; no new GIS authority is approved.

## M2: another authentic original vendor disclosure
A new original first-party vendor agency snapshot was manually checked and inserted as [migration 113](../supabase/migrations/113_monterey_original_flock_portal_snapshot.sql):

- [Flock Monterey CA Police Transparency Portal](https://transparency.flocksafety.com/monterey-ca-pd), portal last-updated **2026-07-24**.
- Portal-reported 37 **LPR and other cameras**, 30-day retention, 113 search sessions, 1,752 hotlist hits and 499,980 vehicle detections in its then-current 30-day window.
- The portal links the City Police's government-hosted [ALPR camera map document](https://files.monterey.gov/Document-Center/Departments/Police/Inside-MPD/Policies-Procedures-Training/ALPR/ALPR-Cameras.pdf). That PDF was inaccessible through the available reading tools. Its georeferenced camera positions, individual-device manufacturer and freshness remain UNVERIFIED. No invented coordinates or GIS records were published.
- [Test](../scripts/test_monterey_vendor_without_camera_points.sql) passed in live Supabase, confirming 14 originally sourced vendor agencies (up from 13), now 10 CA agencies, and **0 Monterey camera pins**. These aggregate portal metrics are not additions to the 316 original-government GIS point count.

## M3: stop generic LPR source points inflating Flock-only route matches
One accepted government original camera map has 23 georeferenced generic `LPR Camera` features in Live Oak, Texas. The source link genuinely comes from the original Police Flock program, but per-device manufacturer and operating status are **not** supported. Previous planned-route comparison used all canonical source-mapped GIS points indiscriminately.

- [route-comparison.js](../route-comparison.js) introduces `eligibleForFlockRoute`, excluding the explicitly identified city original generic-LPR GIS layer and any source whose original evidence explicitly says `NOT per-device manufacturer`.
- Its `summarize()` independently applies that gate; provisional and municipality-associated unconfirmed tiers also cannot enter Flock-only results even if called outside `map.js`.
- [map.js](../map.js) applies the same gate to fetched corridor candidates, route simulation timeline and individual map popup. **The 23 city-published LPR points remain visible** in the source map, with an explicit manufacturer-uncertainty warning. No published source observations were deleted.
- [Route comparison regression](../scripts/test_route_comparison.js) rejects generic LPR, source-attributed and independently corroborated points, while retaining appropriately Flock-specific official records.
- [Public evidence regression](../scripts/test_public_evidence_labels.py) requires consistent front-end filters and truthful copy. [Methodology](../methodology.html) now explains that separate map views and Flock-only synthetic encounters have different proof thresholds.
- A source map point does not prove a current installed/active device or actual plate read. No user plate, vehicle or movement tracking occurs.

## Live final queried inventory
- 316 original government source-mapped locations / 8 approved GIS roots. **Not** 316 independently manufacturer-confirmed devices.
- 12 source-attributed-unconfirmed municipal point observations, source-separated and excluded from official Flock route.
- 13 private source candidates: 6 without qualifying original-agency publisher proof, 4 parked pending separate/duplicate proof, 3 already-covered.
- 14 dated direct original Flock vendor portal snapshots; these describe agencies, **not 14 more geographic camera layers**.
- This continuation added **0 verified camera coordinates**.

## Remaining work
1. Find independently original-agency authenticated Flock georeferenced datasets beyond the eight published government sources. Existing six external Esri org identity investigations need first-party endorsement; no title-only auto-approval.
2. Menifee 27 held exact candidates and Shelbyville 12 separately attributed public GIS observations require new city/police camera-layer/device endorsement for higher verification.
3. Confirm Monterey city original camera-map document can be accessed, source-authenticated and independently georeferenced before considering any exact points. Its current source is an agency-level portal report only.
4. Newport Beach original deployment-polygon source remains a P2 unavailable catalog, not a reason to invent bounding circles.
5. Recheck route comparisons with real users and continue monitoring unchanged sources / machine-readable evidence. M9 keeps Auth leaked-password protection, encrypted off-device restore, provider quotas and human accessibility acceptance as separate launch blockers.
