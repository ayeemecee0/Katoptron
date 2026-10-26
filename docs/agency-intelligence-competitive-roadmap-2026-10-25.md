# Katoptron's competitive differentiator: agency intelligence

Implementation date: 2026-10-25 America/Los_Angeles.

## Decisions
The product is a public accountability and local-government evidence intelligence platform with its Flock-specific camera and community maps remaining accessible as supporting visual evidence. Do not rebuild DeFlock's physical-camera map as the sole value proposition.

### Core workstreams, in order
1. **Agency X-Ray**: merge documented government programs, source-mapped GIS and Flock's source-dated agency disclosures into unified locality dossiers. Locality equivalence is a browsing convenience, **not independent proof that the same agency controls all cameras in town**. Every claim retains its original source.
2. **Local Government Watch**: initially an on-device read-only saved-locality tracker showing currently published dated government and vendor evidence, including items not previously seen on that device. Background automatic email/push alerts require explicit subscriber opt-in, verified change detection, SMTP sender, abuse limits, delivery controls and a privacy assessment. The current launch DOES NOT email or monitor while closed.
3. **Documented Access & Sharing Explorer**: distinguishing allowed access from actual searches and from reverse/recriprocal sharing. Initial secondary-source portal observations are explicitly dated and attributed. Only directly authenticated named sharing edges can be certified as first-party.
4. **One-click research briefs**: phase two once agency identity and original-source records support reliable citations and rights attribution. Should emit a dated PDF/HTML export with evidence tier per claim, original URLs and explicit unknowns; never invent votes, contracts, plate data or camera coordinates.

## First implementation
- [Agency X-Ray](../agency-xray.html) uses the existing published Supabase tables and views: `flock_accountability_events`, `flock_documented_programs`, `flock_camera_locations`, and `flock_vendor_portal_snapshots`. Government points, Flock vendor totals and governments' dated actions are always separate.
- [Local Government Watch](../government-watch.html) uses source-dated published events and portal snapshots, persists watch choices only in this browser's localStorage, and allows explicit reviewed-state changes. Never calls the service role or writes private personal routes.
- [Sharing Explorer](../sharing-explorer.html) has a small carefully attributed **secondary snapshot** from [Perfect World's September 2026 portal index](https://everythingisperfect.org/flock/portal), derived from EyesOnFlock, plus a research-only named access-list example. Secondary readings are NOT represented as independently verified first-party links. Original agency portal data and a document-based directed relationship ledger remain the next acquisition task.
- [Shared code](../agency-intelligence.js) provides bounded pagination, explicit locality normalization, HTTPS-only source links and segregated tier accounting.
- [Browser acceptance](../scripts/smoke_agency_intelligence.cjs), [unit tests](../scripts/test_agency_intelligence.cjs), and the existing release validation protect the first increment.

## Flock Portal Research is not a physical camera dataset
The Perfect World/EyesOnFlock index includes 1,439 portals in 45 states as of its 2026-09-10 index. Its location pins are city/county **gazetteer centroids**, not Flock camera coordinates; the report says 51 agencies cannot be geographically placed. Their report is explicitly CC BY-SA 4.0 and a secondary reading; only one was independently read by that project. The data can inform a separate agency disclosure coverage view, direct-vendor recheck queue, and eventually the sharing ledger. NEVER promote it to verified GIS camera locations, as that recreates the inaccurate-ocean-marker problem.

The [flockcameralocations.com/network source](https://flockcameralocations.com/network) separately offers a CC BY-SA 4.0 EyesOnFlock-derived sharing-network index dated 2026-09-23. Candidate schema: source agency, recipient, source snapshot date, original portal URL, independent first-party corroboration state and confidence. Reusing data requires license attribution, original creator credit, changes listed, source snapshot integrity, explicit CORS/hosting design and a bounded identity crosswalk. A rendered agency geographic center cannot become camera coordinates.

## Acquisition priorities
1. Find and reconcile canonical agency identifiers including Flock portal slugs, program jurisdictions and government operator names. Exact locality match alone is not verified identity.
2. Acquire network sharing links with source/date/permission direction. Present secondary observations in a labeled research tier before first-party recheck; don't falsely call a portal's list a search log.
3. Create weekly immutable portal snapshots and structural diffs for retention and sharing lists, with source 403/unavailable as UNKNOWN, not withdrawn. Rolling 30-day search/hotlist metrics must not be treated as month-over-month growth.
4. After authenticated change events, support users' opt-in alerts without storing habitual travel history.
5. Add one-click brief generation once a source-qualified dossier has sufficient dated evidence.

## Current limitations
This first increment is an interactive beta, not a 1,439-portal local database import, a verified sharing-network graph, a persistent cloud watch subscription or a one-click evidence PDF. It does not add new confirmed government GIS camera points. Maintain RLS and source-publishing boundaries.

## Maintenance priorities
Keep existing Milestone 1 foundation and map pan invariants green, retain source withdrawal checks and the local private evidence boundary. Allocate about 10% to the original camera discovery pipeline maintenance until next genuine agency GIS location source is documented.
