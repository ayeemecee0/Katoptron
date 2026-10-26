# M4 Maps and Routing — engineering acceptance (October 26, 2026)

**Decision:** **100% of bounded M4 map and routing engineering scope accepted.** This certifies working source-labeled map layers, public provider integration, planned-route comparison, synthetic replay safeguards, completeness/error handling and automated browser acceptance. It does **not** certify a nationwide inventory of operating Flock hardware, actual vehicle detections, guaranteed third-party availability or production readiness (M9).

## Delivered map and routing capabilities

1. **Nationwide map:** Leaflet/OpenStreetMap with 316 exact government GIS-sourced camera positions across eight reviewed publisher sources, 293 positively Flock-labeled government GIS positions and 23 Live Oak generic LPR positions. Device manufacturer for each point, current operation, camera direction, true coverage and surveillance-free travel remain unproven. Government-document-only deployment areas, public program records and provisional community evidence retain separate legends and caveats. 12 municipal source-attributed observations remain *unconfirmed*, independent of the verified inventory.
2. **Real US driving routes:** browser-only origin/destination handling and external street-geometry routing via enabled Geoapify with a public, website-scoped browser key; demo OSRM/Photon is explicitly opt-in configuration only. Up to three route alternatives are validated for length, endpoints, coordinates, topology and dimensions. Where unavailable, the site neither invents a straight-line driving route nor assumes a route is camera-free. Alternative geocoder matches require deliberate selection.
3. **Actual full-corridor published-data queries:** `route-evidence-query.js` verifies PostgREST's `Content-Range` **exact** count for both original-government camera and public tiered-evidence layers for every planned-route bounding region. A response capped by the server at 1,000 rows is subdivided geographically until every relevant response is verified complete, subject to fixed limits of 240 region queries and 40,000 source records. Failure, malformed counts, clipped regions, abort, inconsistent source identities or data overload returns **UNKNOWN**, never a false complete or zero result.
4. **Map viewport completeness:** main map read paths now also request an exact count and reject partial 1,000-row responses. On overload users must zoom in. This is better than silently hiding unknown mapped points or falsely certifying an exhaustive viewport. The national map remains explicitly a partial evidence database.
5. **Flock-only manufacturer-source boundary:** Flock-only synthetic route counting strictly requires a positively source-labeled Flock government GIS record. The 23 generic LPR camera coordinates, source-attributed-unconfirmed records, community OSM positions and unreviewed alternative-government cases cannot enter Flock-only simulated encounters.
6. **Synthetic timeline:** observation positions and elapsed-times are derived from real routed line geometry and illustrative 120 m *point-to-road proximity*, **not** a camera's detection range, active uptime, access logs or actual license-plate reads. Fictional observations are off by default and visibly differentiated.
7. **Source-independent optional community comparison:** opt-in OpenStreetMap route observations are queried across each corridor with an independent complete-result algorithm. Overlap with official-source observations is labeled possible, not added to counts or treated as uniquely identified hardware. Turning it on/off or switching alternative routes cannot alter government evidence or the official simulator.
8. **Reliability and privacy:** capped external requests, cancellation of superseded routes, no browser persistence of user addresses, credential-free transport to external routing/geocoding (apart from published browser key) and explicit error/quotas. External routing and geocoding providers receive addresses or coordinates directly from the user's browser, as disclosed. The scheduled public provider-health probe uses only a fixed Sacramento/Folsom fixture, never actual user route inputs.
9. **High-resolution performance:** geographic corridor boxes now compute in linear time with constant per-box bounds tracking, including 20,000-vertex route regression coverage; bounded failure is explicit for very long/unsupported paths.

## Merge and live acceptance evidence

- [PR #17 — source count and route/map completeness](https://github.com/ayeemecee0/Katoptron/pull/17), merged as `0d70390564f8cd73254c413e4293b78eeaae54c6`.
- [PR #18 — opt-in independent OSM route regression](https://github.com/ayeemecee0/Katoptron/pull/18), merged as `588dc8d171558fe24b0a6fd1d12842e74a397059`.
- [Full GitHub validation](https://github.com/ayeemecee0/Katoptron/actions/runs/40376344984): PASS on M4 source changes.
- [GitHub Pages deploy](https://github.com/ayeemecee0/Katoptron/actions/runs/40376343467): PASS.
- [Original M4 release browser suite](https://github.com/ayeemecee0/Katoptron/actions/runs/40376344314): PASS, including synthetic HTTP 1,000-row truncation subdivision, missing exact totals `UNKNOWN` and disabled replay, real hosted Geoapify routing/geocoding/evidence lookup, responsive 390 px viewport and automated accessibility.
- [Expanded browser release suite](https://github.com/ayeemecee0/Katoptron/actions/runs/40376719470): PASS, including community-route OSM-independent comparison and identity-safe switching between alternatives. Live Geoapify PASS (2 routing, 1 geocoding calls from website origin).
- [Automated WCAG scan](https://github.com/ayeemecee0/Katoptron/actions/runs/40376344321): PASS. Human accessibility and usability testing remain M8/M9.
- [WCAG independent release acceptance](https://github.com/ayeemecee0/Katoptron/actions/runs/40376344288): PASS.

## Remaining boundaries and next priorities

- **Source coverage:** 316 verified-source positions do not represent a complete national Flock census; other agencies/cameras may be absent. Six unendorsed private GIS candidate layers and other site-specific source questions remain data-evidence investigation, not missing route engineering.
- **Operation and detection:** none of these tests establishes hardware uptime, camera detection range, travel direction, real plate reads or actual sharing.
- **Third-party dependencies:** hosted Geoapify tested successfully today, but future quota, account-side origin restrictions, SLA and billing limits cannot be guaranteed by browser tests alone.
- **M5:** actual user submissions and community review acceptance are separate.
- **M8/M9:** independent human usability/accessibility testing, operational monitoring, real-account provider quota validation and launch security/privacy review are separate release gates.

**M4 engineering: 100%.** Coverage completeness and production launch readiness: deliberately not certified.
