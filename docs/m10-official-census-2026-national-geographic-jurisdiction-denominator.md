# M10 · Official Census 2026 all-state local geography research baseline

This milestone builds the official federal **geographic research denominator**, rather than pretending 51 state-level URLs encompass every city, county, township or police department.

**Source:** [U.S. Census Bureau's 2026 Gazetteer files](https://www.census.gov/geographies/reference-files/2026/geo/gazetter-file.html). The exact official original archives were acquired and validated in [GitHub Actions run 40625767004](https://github.com/ayeemecee0/Katoptron/actions/runs/40625767004).

| 2026 geographic category | 50 states and D.C. rows | Original ZIP SHA-256 |
|---|---:|---|
| County and county equivalents | **3,144** | `6a99ca00efbc0be5112e225d4102704c51d5ce3b16e3afd6e4159460595fd12a` |
| Census places (including census-designated places) | **32,071** | `af678e2d990827c89ee39b98c82de6e90b693c7361ff0e559ae3076670dd2863` |
| County subdivisions, including statistical units | **35,442** | `9d528b39b70a27075c863b1572f27eadaf24484d5435fac17fc3b4cdd36434c2` |
| Total research geography records (overlapping categories) | **70,657** | Three original federal sources |

Data semantics:
- **Geographies are NOT 70,657 distinct governments.** Unincorporated Census places are not necessarily municipalities. County subdivisions include statistical units and overlap counties/places. Some municipal governments cross geographic borders.
- **Geographies are NOT law enforcement agencies.** One police agency may serve many geographies or a municipality may outsource police services. The BJS [2018 Census of State and Local Law Enforcement Agencies](https://bjs.ojp.gov/data-collection/census-state-and-local-law-enforcement-agencies-csllea) is a distinct, dated federal agency-universe reference. Do not join them by string similarity or assume continued operation.
- The Census data provide **no original policy, Flock vendor status, retention policy, law enforcement sharing access, installed camera locations, or verified ALPR program**. Zero operational facts were added.
- All records are traceable to official U.S. Census Bureau ZIP files, not a crowdsourced coordinate or model-inferred municipality.

Implementation:
- `scripts/build_census_2026_jurisdiction_universe.py` downloads three exact `www2.census.gov` HTTPS ZIPs, blocks redirects, enforces compressed/extracted size limits, validates field names, 51 states, unique census GEOIDs, and bounded row counts, and emits a source-hashed, complete 70,657-record named geography research artifact without GPS camera points or police agency assertions.
- `scripts/test_build_census_2026_jurisdiction_universe.py` covers ZIP traversal, duplicate identifiers, missing state, corrupted input and false coverage semantics.
- `.github/workflows/build_census_2026_jurisdiction_universe.yml` builds and preserves named full original-derived geographic research data as an artifact on a **weekly** schedule (retained 21 days). Independent acquisition is read-only and does not email users or write new public camera coordinates.
- `data/census-2026-state-geography-coverage.json` stores 51 state-level exact original source-based totals and immutable source SHA-256 fingerprints so the website remains usable even if a future government source check is held.
- `census-geography-coverage.js` fails closed if government source hashes, category sums or agency/equipment evidence tiers are altered.
- `nationwide-policy.html` juxtaposes original 2026 geographic denominators with independently reviewed Flock accountability evidence, **without equating them**.
- Live mobile Chromium, repository and security checks cover state census totals and forbid operational Flock inference.

### Next agency verification expansion

This geographic baseline supports rigorous targeting. The next step is to obtain the most recent source-dated official national police agency directory by stable identifier, reconcile *exactly* to jurisdictions when official organization identities agree, and retrieve original government policies across verified source authorities, with uncertainty held. Every individual department remains **unverified** until its own original evidence qualifies; a nonmatch is not a negative Flock finding.
