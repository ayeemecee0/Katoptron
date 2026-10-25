# Katoptron: source-freshness and immutable-evidence continuation (October 25, 2026)

## Current production baseline independently queried
- 316 currently verified exact GIS **source-mapped camera locations**, 8 jurisdictions/sources. This includes 23 police-published Live Oak, TX ALPR map observations; Live Oak map records do **not** independently establish that every device is Flock-manufactured, installed on a specified date, or operating now.
- 12 separately published **source_attributed_unconfirmed** Shelbyville, TN points. These are *not* independently government-endorsed individual Flock camera installations and are excluded from verified-route simulation.
- 116,159 nationwide OpenStreetMap Flock-tagged community observations; they are neither unique, agency-certified, nor proven operational devices.
- 24 documented original-government Flock programs, which are **not** camera positions.
- 27 Menifee source-feature candidates remain held; their original police affiliation, precise inventory status, and count differences remain unresolved.

## Live bug reproduced
A newly changed city webpage's raw SHA-256 modified the computed private receipt even though the fresh original city-to-Esri organization relationship and complete 12-object GIS inventory still passed. The private attestation is append-only and cannot be overwritten, so scheduled refresh and private staging both failed with `InventoryHeld:private_provenance_drift`, despite 12 lower-tier points already published. Repeatedly retrying did not fix the proof mismatch.

## Repair and explicit safeguards
1. Source-refresh failure diagnostics now disclose **only** reviewed internal reason codes, never unpublished GIS coordinates, raw URLs/responses, HTTP exception strings, or service secrets.
2. For a **known already-published** source, a changing city-page HTML fingerprint can be treated as a nonsemantic page-content change **only after** the fresh original city hyperlink still independently resolves to the identical ArcGIS publisher and the full typed ObjectID point inventory is validated twice. Previously staged original case identity, source URL, source family, geometry, authority URL, attestation status and original published SHA must all match. No new camera point may use the exception.
3. The old immutable attestation SHA is **retained** rather than rewritten; only the existing lower-confidence map row's `source_checked_at` advances. Withdrawn, changed, duplicated, missing, or unreviewed-new records remain blocked. The verified canonical camera table is never updated by this path.
4. The separate private-staging worker records an explicit GitHub warning/held state for the already-staged immutable page-fingerprint mismatch; its workflow then runs the independent guarded source refresh. A genuine missing website, incomplete GIS inventory, changed point, credential failure, or any other mismatch still fails.

## Live acceptance
- Source refresh succeeded: https://github.com/ayeemecee0/Katoptron/actions/runs/40233987889
- Private-stage hold + source refresh succeeded: https://github.com/ayeemecee0/Katoptron/actions/runs/40234109994
- Full regression suite passed on the source-recheck test commit: https://github.com/ayeemecee0/Katoptron/actions/runs/40233988115
- Public Pages deploy passed on the source-recheck test commit: https://github.com/ayeemecee0/Katoptron/actions/runs/40233988086
- A direct Supabase follow-up confirmed 12 active source-attributed rows with an updated checked timestamp. This is source freshness, **not** evidence that each individual Flock camera is installed or live.

## Deliberate blockers and priorities
**P0:** Find genuinely distinct first-party Flock-specific GIS camera inventories; do not re-acquire already-trusted layers or promote search hits. Release labels must distinguish source-verified *positions* from Flock hardware/manufacturer certainty.
**P1:** Gather an exact police/agency-authored Menifee GIS endorsement before any new government-verified publication. Shelbyville's individual-camera proof remains parked; existing municipality-linked map observations remain low confidence.
**P1:** Auth email delivery, real user test, external provider origin/quota settings, restore of privately encrypted off-device database/Storage backup, and accessibility acceptance still need owner/human validation before full production.
**P2:** Newport Beach original GIS polygon service catalog still fails optional polygon discovery (issue #1). Hold polygon growth; do not infer maps or suppress factual missing-source warnings.
**Maintenance:** Continue scheduled original-source rechecks and backlog dispositions, approximately 10% of development effort.

## Accounting rules
Never add together 316 official source locations, 12 source-attributed locations and 116,159 community observations as if they were distinct installed devices. This continuation repaired continuity/revalidation and produced **zero newly verified camera points**; Live Oak's additional 23 were already present when this work resumed.
