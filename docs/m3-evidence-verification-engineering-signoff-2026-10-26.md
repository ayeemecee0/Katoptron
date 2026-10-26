# M3 Evidence Verification — Engineering acceptance (October 26, 2026)

## Decision
**M3 engineering scope signed off at 100%.** This means the publication and verification pipeline, source classification, independent proof paths, provenance, non-promotion, public evidence tiers, expiry/revocation controls, and automated negative tests are implemented and running. This **does NOT** mean every surveillance camera in the United States has been independently identified, that each GIS point is an operating Flock camera, or that every private source candidate has externally validated provenance.

## Source-specific production inventory, independently queried

| Classification | Records | Interpretation |
|---|---:|---|
| Source-verified government GIS positions | 316 | Exact coordinates copied from 8 separately reviewed original GIS authorities |
| Positive *Flock-labeled source* government positions | 293 | 7 original government GIS sources, **not** individually confirmed active hardware |
| Government GIS generic LPR camera positions | 23 | Live Oak TX; individual manufacturer not source-established; **excluded from Flock-only route simulation** |
| Source-attributed unconfirmed points | 12 | Visible on a separately labeled provisional layer, excluded from verified camera count and Flock-only route |
| Public `government_verified` evidence cases from independent attestation | 0 | No raw private case auto-published |
| Public `independently_corroborated` case points | 0 | Two-source review/sign-off still required; no false source independence |
| Private GIS source candidates | 13 | 3 already covered, 4 parked with reasons, 6 requiring government publisher endorsement |
| Private candidate point cases staged | 12,217 | All still `candidate`, private until required independent proof and review |
| Source attestation entries | 12,227 | 12,217 staged, 10 reviewed; individual observations are **not** unique installed camera counts |
| Point disposition cases | 62 | 23 considered equivalent to already published positions, 39 held for separate source endorsement |
| Pending verified-camera withdrawal records | 0 | No phantom source deletion triggered |

The counts are an audited October 26 snapshot, not guaranteed static or exhaustive.

## Engineering acceptance boundaries

1. **Multiple legitimate source routes:** independently reviewed original government GIS, vetted original agency-owned organization or original government document carrying exact points, or independently corroborated provisional observations. Candidate discovery never self-approves.
2. **Positive Flock provenance:** every published canonical GIS position is joined to an approved, exact source/jurisdiction identity. New imports default `unconfirmed`; migration 138 prevents a service-role import from directly asserting `source_flock_identified` or even `generic_lpr`. Only a database-owner-reviewed source classification can change the label. Source-label evidence is not individual serial number/manufacturer verification.
3. **Live audit freshness:** recurring `audit_m1_m3_production.py` validates every source digest, stable original source identity, coordinates, no duplicates, 365-day government-source recheck deadline, 14-day freshness of provisional city-attributed evidence, valid clock-skew limits, and positive label/source concordance. Unknown government source labels fail closed for Flock-only route evidence.
4. **Public/private partition:** `flock_public_tiered_camera_points` is `security_invoker` and permits only eligible owner-reviewed `government_verified` and `independently_corroborated` cases, or separately labeled `source_attributed_unconfirmed` points. Private raw evidence and candidate cases are not accessible to anonymous users.
5. **Revocation and rechecks:** source status changes, missing/incomplete original inventories and two-pass confirmed source removals cannot silently elevate or invent cameras. Stale evidence becomes ineligible under the relevant tier-specific RLS policies. Original records and histories are retained.
6. **Real negative regression tests:** empty disposable PostgreSQL CI checks schema and trigger safety; live production SQL tests the full 316 source-label baseline and verifies service-role insert escalation is rejected within rollback. Python failure tests reject changed/missing labels, unapproved positive Flock source keys, out-of-date or future source timestamps, malformed hashes and geometry, duplicate record identities, unreviewed source authority and cross-tier overlap.

## Deployment and acceptance evidence

- M3 implementation: [PR #16](https://github.com/ayeemecee0/Katoptron/pull/16), merged onto `main` as `e8d06cc44706d8b08f8d9a36f32dd0c45d29922a`.
- [Migration 138](../supabase/migrations/138_m3_positive_flock_source_label_insert_guard.sql) applied after rolled-back production rehearsal.
- [SQL M3 evidence release checks](../scripts/test_m3_source_label_integrity.sql): live production **PASS**, including negative automated source classification escalation.
- [Python M3 production read-only audit](../scripts/audit_m1_m3_production.py): tests source-label positive allowlist, generic LPR guard, provenance, geometry, recheck freshness, and 12 public source-attributed observations.
- [Production M1-M3 acceptance](https://github.com/ayeemecee0/Katoptron/actions/runs/40372458358): **PASS** on merge commit.
- [Full release validation on PR head](https://github.com/ayeemecee0/Katoptron/actions/runs/40372204832): **PASS**.
- [Pages deployment](https://github.com/ayeemecee0/Katoptron/actions/runs/40372455672): **PASS**.
- Supabase security advisor reports no new M3 disclosure concern; remaining preexisting project notices are covered under later operational milestones.

## Evidence questions not answerable from current original sources

- Six externally hosted Esri GIS camera layers do not yet have independently attributable local government endorsement. Esri organization titles are **not** independent endorsement.
- Menifee's 27 held GIS features and Shelbyville's 12 separate lower-confidence city-attributed points cannot become confirmed Flock hardware solely through their GIS appearance.
- Monterey's government PDF map remains insufficiently independently georeferenced and individually manufacturer-confirmed.
- Multiple alternate government GIS sources with nearby coordinates may be duplicate physical devices; proximity by itself does not identify a device or justify duplicate official pins.
- A complete nationwide hardware/uptime/source coverage census has no defensible denominator. Discovery and source-specific investigation must continue without treating uncertainty as absence or fabricating exact points.

## Acceptance conclusion

**M3 software and verification safeguards: 100% of the bounded engineering acceptance scope.**

**Nationwide verified coverage and device-level identity: incomplete/unknown.** Further source acquisition, independent corroboration and human source evidence review are continuous research/data work, not a reason to falsify the engineering completion metric.
