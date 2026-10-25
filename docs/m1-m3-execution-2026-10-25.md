# Katoptron M1–M3 development execution and acceptance — October 25, 2026

## Production audit (directly queried)

| Control | Observed result |
|---|---|
| Public-schema PostgreSQL RLS | 62/62 base tables enabled |
| Foreign keys without covering indexes | 0 after migration 109 (2 fixed) |
| Anonymous-callable SECURITY DEFINER helpers | 2, down from 4; both are narrow RLS source-status booleans |
| Privileged authenticated functions | 13 allowlisted in production; reviewer/owner functions contain UID and scoped permission checks |
| Source-verified canonical GIS positions | 316 across 8 independently reviewed GIS authorities |
| Live Oak TX source-mapped generic LPR positions | 23 of the 316; agency map georeference is documented, individual Flock manufacturer/operation is not |
| Source-attributed unconfirmed Shelbyville observations | 12, excluded from canonical government-source verified count and simulator |
| Independently source-tagged OSM observations | 116,159 (separate community tier; never additive unique hardware) |
| Unverified GIS source candidates | 13: 3 already-covered sources, 4 parked for independent endorsement/duplicate proof, 6 investigating original-government linkage |
| Private point case dispositions | 23 resolved to already-published positions, 39 held pending separate proof |

## M1 — Foundation hardening delivered
- [Migration 109](../supabase/migrations/109_m1_m3_source_fk_indexes.sql) installed two missing foreign-key indexes used by canonical candidate/source revocation and reconciliation. Follow-up Supabase performance advisor returned **zero unindexed foreign keys**.
- [Migration 110](../supabase/migrations/110_restrict_unused_public_definer_rpcs.sql) removed anonymous/authenticated EXECUTE from two privileged source functions unused by public RLS; service-role access is retained where required. The two remaining anonymously callable helpers are deliberately required by camera and polygon RLS policies.
- [SQL release acceptance](../scripts/test_m1_m3_acceptance.sql) enforces RLS on all current public base tables, restricted editorial/source authority grants, read-only public tiered view, source-specific revocation policy, no cross-tier duplicate publishing, and an explicit authenticated privileged RPC allowlist. No source approval or coordinate publication occurs during the test.
- The existing disposable PostgreSQL migration suite, private Auth/Storage acceptance, public map smoke tests and daily public health monitor continue to provide independent controls.

## M2 — Discovery lifecycle delivered
- [Migration 111](../supabase/migrations/111_evidence_driven_gis_source_reactivation.sql) now fingerprints original government link context, schema, ObjectID, layer identity and trust status. Changes reopen review immediately; unchanged leads automatically enter a bounded 30/90-day cooldown after triage. Reopening a lead is **not** source approval.
- [Regression](../scripts/test_source_evidence_reactivation.sql) passed against production inside a rolled-back transaction: new due lead, changed proof reactivation, subsequent cooldown, and zero accidental trusted-source promotion.
- [Live triage workflow](../.github/workflows/triage_gis_verification_backlog.yml) now reactivates changed evidence, investigates due candidates, and finalizes cooldown in one scheduled pass.
- The actual October 25 workflow verified 13 private GIS lifecycle states. Six external-source records remain research-blocked; no false publication occurs. No new original agency endorsement was established by source-title searches.

## M3 — Evidence verification and publication
- [Read-only production gate](../scripts/audit_m1_m3_production.py) cross-checks every canonical camera record against a currently approved exact GIS source identity, proof digest and source-check timestamp; checks bounds and uniqueness; requires Live Oak manufacturer's unconfirmed status to remain explicit; checks all active lower-confidence sources against their policies and verified points; ensures every discovered GIS source has a lifecycle record.
- [Offline negative tests](../scripts/test_audit_m1_m3_production.py) reject unverifiable sources, malformed digest/geometry, missing rechecks, duplicate official IDs, cross-tier overlap, lifecycle gaps and per-device manufacturer overclaiming.
- [Homepage](../index.html) and [methodology](../methodology.html) now explain that government source-mapped camera positions are **not** always per-device Flock-manufacturer certified; separate unconfirmed tier never becomes a verified route detection. [Copy tests](../scripts/test_public_evidence_labels.py) enforce this caveat.
- Daily [public GIS monitor](../scripts/monitor_public_health.py) now includes all eight source jurisdictions and the Live Oak 23-point baseline.
- Existing individually sourced original GIS rechecks, two-pass withdrawal, independent case reviewer and private original attestation flow remain mandatory.

## Independently verified workflow evidence
- [M1–M3 production gate successful](https://github.com/ayeemecee0/Katoptron/actions/runs/40236682770)
- [Discovery triage and lifecycle reconciliation passed](https://github.com/ayeemecee0/Katoptron/actions/runs/40236091640)
- [Eight-source public map health passed](https://github.com/ayeemecee0/Katoptron/actions/runs/40236409546)
- [Browser smoke passed](https://github.com/ayeemecee0/Katoptron/actions/runs/40236303719)
- [Full disposable PostgreSQL migration, RLS and regression validation passed](https://github.com/ayeemecee0/Katoptron/actions/runs/40236750949)

## Non-software acceptance dependencies
1. **Agency-specific proof:** Shelbyville's 12 source-attributed map observations and Menifee's privately held 27 GIS features still lack independent police endorsement of their exact individual camera-layer status. Do not inflate manufacturer-certified or verified camera totals.
2. **Six external GIS sources:** need independently attributable original agency source/publisher evidence. Their GIS titles and item-owner self-description are not sufficient.
3. **Newport Beach deployment polygons:** original GIS service-root catalog remains inaccessible; no unsupported deployment regions may be drawn.
4. **Full release:** email confirmation, actual private encrypted off-device backup restore, provider quota/origin controls, representative user accessibility acceptance and independent legal/privacy review are M9/production gates, not evidence that M1–M3 software has nationwide data.
5. **Coverage ceiling:** 316 GIS-source positions are not nationwide verified coverage. A complete national Flock hardware census cannot be certified without additional original source evidence.

**Accounting:** This pass created zero new verified camera positions. It repaired operational security, discovery readiness, live integrity checking, classification language and automatic regression monitoring. Existing official government camera positions, city-publisher map observations, vendor agency directories and independent community data remain disjoint evidence types, never a single additive device count.
