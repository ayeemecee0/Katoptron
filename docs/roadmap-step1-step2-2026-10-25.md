# Katoptron steps 1–2: expansion and national intelligence (25 October 2026)

## Live production acceptance
- Original government exact Flock locations: **293**, unchanged, seven authenticated government GIS sources.
- Source-separated OpenStreetMap community observations: **116,159** (OSM-derived, not necessarily active or unique devices).
- Private unreviewed Shelbyville TN point cases: **12**; Menifee CA: **27**; no publication authorization changed.
- Live Oak TX original-city camera map research: **23** distinct original ArcGIS point features, `Device_Type` is generic **LPR Camera** for all 23. No per-device Flock manufacturer proof, despite the direct original city police Flock webpage → ArcGIS camera-app source link. Source affiliation at individual ArcGIS layer and installed/active status are not established; **0 Live Oak private cases or public verified camera pins created**. See [issue 5](https://github.com/ayeemecee0/Katoptron/issues/5).
- Original-government-linked private Flock portal leads: **4**, up from two; still not automatically approved. Public independently government-linked vendor directory currently returns **0**, because current reviewed source pages did not expose qualifying links when fetched. Do not represent zero as no Flock programs.

## Delivered: national intelligence / step 2
1. Source-reconciled bounded 3° / metro-level density markers instead of missing map points in city views exceeding the 1,000-result public API limit. Example: 1,481 original OSM points in a bounded Atlanta viewport reconcile exactly into five density groups. Low-zoom group centers are **not cameras**.
2. A read-only, RLS-respecting Supabase density RPC with caller permissions, strict bounds and cell count limits. Tested with anon role and complete source row counts.
3. Default nationwide OSM map and original government GIS evidence remain independent; click a government point to inspect nearby original OSM observations via the separately sourced 30m cross-source proximity view.
4. Map and browser accessibility passes at published commit; user location/plate tracking absent; OSM route comparison remains optional and never counted in government verified camera matches.

## Delivered: source expansion / step 1
1. Confirmed original government police Flock page links a city ArcGIS map, traced the published ArcGIS application to a real Web Map and exact public point layer, and reconciled all 23 source IDs and georeferenced original LPR cameras without logging private positions.
2. Added privacy-safe, unreviewed-only private staging code and offline tests for Live Oak. **Do not claim staged** until an authenticated protected GitHub workflow is installed and run; current production check returns 0 Live Oak private cases.
3. Continued automatic government GIS catalog discovery, original Esri source relationship checks, weekly source rechecks, and four original-government-linked private vendor portal leads.
4. Created an RLS-protected read-only directory for refreshed direct government-to-Flock vendor links and an automated source recheck worker. The directory currently has 0 entries and must never imply camera installations from a portal link. Vendor snapshots remain separately labeled.
5. Linked the city's original camera map publicly in the Flock disclosure source-directory page, explicitly not elevating its 23 generic LPR positions into independently government-Flock-verified points.

## Remaining external or policy-specific gates
- Confirm per-device Flock identity in Live Oak's generic LPR Camera layer or a city document that expressly ties all mapped device records to its Flock installation inventory; independently attribute underlying ArcGIS app/Web Map publisher and check first-party adoption dates/operational status.
- Run protected private evidence staging for eligible Live Oak points with complete source hashes and proximity checks; never use anonymous write privileges to make staging easier.
- Obtain and recheck source-specific original-government camera GIS endorsement and approve Shelbyville 12 and Menifee 27 through separate established controls, not by copying candidate values into the canonical table.
- Expand distinct first-party geo-registered sources to grow *verified exact* nationwide coverage beyond 293. Current community reach is nationwide, verified exact reach is still limited.
- Continue source freshness and fail-closed reconciliation; if source origin becomes unavailable, mark UNKNOWN and do not invent a count or device.
