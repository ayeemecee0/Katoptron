# M10 · Six-state official government ALPR source watch
**Implemented:** October 27, 2026. Verified original publisher material only.

## Scope and outcome

Katoptron now has an original-government publisher watch for **10 distinct official publication URLs across six U.S. states**: California (CA), Wisconsin (WI), Virginia (VA), Texas (TX), Delaware (DE) and Oregon (OR).

- The seeded registry is [data/national-government-audit-source-portals.json](../data/national-government-audit-source-portals.json): seven official government HTML publication pages and three exact original government PDF URLs. It is a **curated publisher list**, not all cities or ALPR agencies in those states.
- The [bounded first-party Python source scanner](../scripts/scan_national_government_audit_sources.py) only reads those exact original URLs; ordinary public publisher links must remain on a hardcoded approved government host. It does not follow unreviewed redirects, scrape unrelated websites, call third-party search APIs, access private portals or download plate data.
- The first successful full run, [GitHub Actions #40565097570](https://github.com/ayeemecee0/Katoptron/actions/runs/40565097570), marked **all 10 official sources accessible**, recorded **13 unique candidate publisher links** (of which **nine need individual content review** and **four match already page-verified originals**), and generated **three PDF SHA-256/page-count receipts**. The scan was metadata-only: **0 facts**, **0 camera pins**, **0 sharing-network edges** auto-published. Nine unmatched source links remain content-review candidates, **not nine independently proven Flock audits**, camera installations or contract facts. Already-reviewed originals cannot repeatedly consume the new-source review queue.
- [Scheduled government-source review workflow](../.github/workflows/scan_national_government_audit_sources.yml) runs once a week and keeps a 14-day GitHub Actions artifact, not a production source-of-truth database. The public [national audit library](../national-audits.html) displays vetted government starting URLs so users can independently inspect them. Its linked candidates do not silently become audited findings.

## Three original additional report reviews

Beyond the existing four separately reviewed police-department-authored government reports, the national public library gains three additional original-PDF reviews with their own clear publisher types and precise source-page citations:

| Original publisher | Evidence tier | Source-reviewed finding |
|---|---|---|
| [San Mateo County Civil Grand Jury, California, August 3, 2026](https://sanmateo.courts.ca.gov/system/files/grand-jury/auto-license-plate-readers-report.pdf#page=2) | **Independent government oversight** (20 pages) | Reports historical policy documentation, internal auditing and in-state sharing control gaps among reviewed San Mateo County ALPR operators. The grand jury gave a countywide ALPR inventory of **more than 582 cameras as of March 30, 2026** (PDF page 3): **not 582 currently verified Flock cameras**, and no individual coordinates. |
| [City of Austin Office of the City Auditor, Texas, May 2025](https://services.austintexas.gov/edims/document.cfm?id=452710#page=2) | **Independent government oversight** (21 pages) | Found quarterly ALPR audits generally accurate but with data/timing gaps, and flagged potential risks from ambiguous Flock contract language (PDF page 2). Described historical **40 fixed Flock cameras** and nearly **500 vehicle-mounted Axon** cameras (page 3). These are different vendors and cannot be added into a Flock total. May 2025's precise issue day is **not specified**. |
| [Woodburn Police Department, Oregon, February 2, 2026 revised impact assessment](https://www.woodburn-or.gov/DocumentCenter/View/3298/Flock-Impact-Assessment-FINAL-2-3-26#page=7) | **Police-department-authored impact assessment, NOT independent oversight** (98-page PDF) | Department retrospectively reports its first Flock camera activated March 3, 2025, and officers' Flock user access ended November 11, 2025. Historical self-report, not proof of present camera status, license-plate movements, or external audit findings. |

Original file SHA-256 receipts checked directly against the official published PDFs:
- San Mateo County civil grand jury `8f38bed56c568d6e6875bbbcc92d3578f59098d4e86c402a4ae87c79ecdb8489`
- Austin City Auditor `3399cc05ee5f8cc48b4b1dd7c215a3e65f0786d61501a662591df2f595b3eea0`
- Woodburn police assessment `24ef40a0d2f72e9b618cfe98e27e3f059d6012effafd621f83f6f70880810f33`

[Original three-PDF government provenance inspection #40564492070](https://github.com/ayeemecee0/Katoptron/actions/runs/40564492070) and [source-freshness verifier #40565974439](https://github.com/ayeemecee0/Katoptron/actions/runs/40565974439) independently checked original files, their authored-page text anchors and hashes. The periodic verifier **fails closed** if a document changes or becomes unavailable; it does not treat failure as proof that a report or deployment has been withdrawn.

## Falsification and privacy controls

1. **Publisher provenance:** All 10 source URLs must be directly from an explicitly allowlisted original government host and prescribed path. Only HTTPS, no embedded credentials, no arbitrary redirect or unapproved query arguments.
2. **Publication roles:** Two new reports are civil government external oversight; the Woodburn report was written by Woodburn Police, and cannot be promoted to an independent report by changing its JSON publisher label. Existing San Bruno and Green Bay agency-authored statements retain their separate review tier.
3. **Scope of automatic evidence:** HTML extraction reads descriptive government anchor text, plus a bounded adjacent description when a city archive labels PDF links generically as "Backup". It skips individual ALPR search logs, raw vehicle reads and person-level record types. PDFs are fingerprinted **without storing text** in the discovery artifact.
4. **Limits:** HTML pages are at most 1.6 MB; individual PDF originals at most 8 MB and 110 pages. The first 10 watch sources were reachable as tested, but other governments are unindexed. Unavailability is **unknown**, not withdrawal.
5. **Publication rules:** Discovered documents do not automatically change camera maps, sharing networks, policies, department conduct or compliance ratings. Only separately verified reviewed original pages are displayed as attributable historical claims.

## Acceptance and next priorities

- `python -m unittest discover -s scripts -p 'test_scan_national_government_audit_sources.py' -v`
- `python scripts/scan_national_government_audit_sources.py`
- `python -m unittest discover -s scripts -p 'test_verify_national_government_oversight.py' -v`
- `python scripts/verify_national_government_oversight.py`
- `node scripts/test_national_government_sources.cjs`
- `node scripts/smoke_national_audits.cjs`
- CI: [national source watch workflow](../.github/workflows/scan_national_government_audit_sources.yml), [original government oversight verifier](../.github/workflows/verify_national_government_oversight.yml), [accountability browser acceptance](../.github/workflows/audit_accountability_acceptance.yml).

**Next:** Add original city/state publication indexes only after authenticating government publisher domains; prioritize independent auditors, statewide oversight agencies and records that establish verifiable changes to public ALPR policies, contracts, program operation and restricted sharing. The present **six states monitored** and **five states with individually source-reviewed national-library PDFs** are meaningful footholds, not a comprehensive national census. Minnesota's **42 separate reviewed external auditor PDFs** remain under their own state-archive verifier.
