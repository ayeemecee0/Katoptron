# Peoria, Arizona: original city GIS inventory acquisition

## Source and checks
- City-controlled GIS portal: https://gis.peoriaaz.gov/portal/sharing/portals/self — public ArcGIS Enterprise portal labels itself **Peoria GIS Portal**.
- City's own development-services page links directly to the same GIS hostname: https://devservices.peoriaaz.gov/devservices/Cap/CapHome.aspx?module=Building (its **View Building Permit Map** link goes to `https://gis.peoriaaz.gov/PeoriaPlanReview.html`). This is independent agency-domain attribution of the GIS hostname, **not** agency approval of a particular police camera dataset.
- Exact `Flock Cameras` source: https://gis.peoriaaz.gov/arcgis/rest/services/PM/pmPublicWorks/MapServer/286
- Original read-only source inventory verified **74** complete camera GIS features with unique ArcGIS ObjectIDs and distinct camera IDs, bounded original coordinates and stable before/after ID snapshots: https://github.com/ayeemecee0/Katoptron/actions/runs/40167182149
- Police department's Flock transparency portal reports **81 LPR and other cameras** as of July 23, 2026: https://transparency.flocksafety.com/city-of-peoria-pd. Its scope and date may differ from the city GIS layer.

## What this DOES and DOES NOT prove
This gives independent original city-domain proof of the GIS server, typed complete source data and a public vendor portal acknowledging a Flock program. It does not establish which of the 74 are operating now, whether the 81 cameras are the same category or snapshot period, or whether any of Peoria's mapped locations overlap records already in Katoptron.

The two counts must not be subtracted to invent seven additional points or justify publication. Metadata fields may show locations rather than active install states.

## Next acceptance gates
1. Independently re-fetch live city-hosted layer metadata and reconcile any status fields, plus source dataset's editing and update policy.
2. Add source-governed candidate registration (no per-city SQL or manual public inserts), preserving original URL/refresh timestamps/evidence provenance.
3. Run privacy-preserving approximate-neighbor and exact-source deduplication against the complete published inventory; preserve source-specific identities.
4. Check the current publication authority RPC's requirements before enrolling Peoria; specifically, no silent bypass of reviewed-source registry or RLS.
5. Approve only those records that independently pass all relevant source/geometry/duplicate/status requirements; then re-query public counts.

## Public safety boundary
No private camera coordinates or individually identifying device values appear in this report. Do not publish raw source exports in GitHub. Do not mark published until independently queried from production.
