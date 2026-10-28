# M10 · National ORI agency research denominator, separate from government evidence

Source retrieval: October 27, 2026 (October 28 UTC runner time). Live run: https://github.com/ayeemecee0/Katoptron/actions/runs/40626549258.

The open CC0 [IROPO agencies.csv](https://iropo.org/sources/) compiles the FBI Crime Data Explorer's `/agency/byStateAbbr/{state}` directory. This **secondary** provider says its last FBI data retrieval was September 30, 2026. The dataset comprises **19,636 state and local law-enforcement agency ORI directory entries** in all 50 states and D.C. Its original CSV byte fingerprint as fetched in CI is `66e2bbe4e78b92c929a615b8be0f713d3ea8d780c25be541c3ddadeb0ebc792a`.

This is **not** a direct independently page-reviewed FBI government original, a statutory police agency census, an agency currently operating roster, or evidence any agency deployed Flock or an ALPR device. Reporting participation and administration change. Stable ORI codes are proposed as **research reconciliation identifiers only**, subject to original-government confirmation before joining to agencies in Katoptron.

## Execution and product

- `scripts/build_fbi_derived_agency_roster.py` acquires the exact 1.7 MB public CSV, checks schema, ORI uniqueness, 51 state coverage, row bounds, and uses only public ORI/name/type/county fields. It deliberately drops all latitude/longitude to avoid conflating law-enforcement office positions with camera coordinates. It outputs a complete research roster, with every item labeled unverified agency current status and no Flock assumptions.
- `.github/workflows/build_fbi_derived_agency_roster.yml` refreshes monthly and preserves the full 19,636-record ORI directory for 21 days, with source checksum and per-state reports. It uses no API credentials or production DB writes.
- `data/secondary-fbi-ori-state-agency-research-2026.json` holds all 51 state exact counts from the successful live provider. `ori-agency-coverage.js` validates source fingerprint, counts and factual classification.
- `nationwide-policy.html` now compares **three independent denominators** per state: 2026 Census geographic records, secondary FBI ORI agency directory entries, and individually source-verified historical ALPR policy dossiers. None is represented as proof of Flock equipment or a completed policy census.
- Browser acceptance and unit tests reject duplicate ORIs, new camera-coordinate claims, false operational-agency verification, wrong hashes, or fabricated state totals.

## Remaining verification frontier

A complete and current federal or authoritative state law-enforcement agency census, real agency legal identity and Flock vendor use all require **independent evidence**. The 19,636 ORI entries are high-yield acquisition leads, not 19,636 verified police deployments. Per-jurisdiction policy adoption and exact camera position must be proved separately. No historical source should be automatically treated as a present-day operating policy. Nationwide full factual coverage remains incomplete.
