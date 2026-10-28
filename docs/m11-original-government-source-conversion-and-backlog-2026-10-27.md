# M11 · Original-government Flock evidence conversion, national backlog and source-only map links

**Release baseline:** October 27, 2026; original-source acquisition executed October 28 UTC.
Live reproducible original-source verification run: https://github.com/ayeemecee0/Katoptron/actions/runs/40628982546

## Automated qualification and publication

The new `scripts/convert_official_flock_disclosures.py` reads a bounded 11-agency original source registry, retrieves exactly identified municipal HTTPS pages, rejects unsafe/cross-publisher redirects and plate-search URLs, strips executable HTML, and requires multiple independent claim-specific source-text anchors. A missing source or changed anchor is **HELD**, never automatically upgraded to policy adoption, exact device positions or operational activity. It records SHA-256 of original publisher response.

**11 new source-authority government agency statements across 11 states** passed live acquisition: Siloam Springs AR, Idaho Falls ID, Lafayette IN, Lexington KY, Salem MA, South Portland ME, Robbinsdale MN, Columbia MO, Rio Rancho NM, Gallatin TN and Lafayette CO.

The verified results are published as source-hashed, individually accountable municipal HTML statements in `data/verified-agency-html-source-disclosures-2026-10-27.json`, using GitHub Pages' static file publication. **No manual SQL, Supabase migration or privileged database access is needed** for these public sourced records.

The classification is explicit:

- Eight original municipal pages describe Flock use in dated agency-authored statements. **Do not treat as independent confirmation of current live operations or individually verified equipment.**
- Salem MA describes a decision not to renew and planned replacement, not independently completed removal.
- South Portland ME reports all Flock cameras removed by June 22, 2026. This is a dated city-authored completion statement, not an independent inspection.
- Lafayette CO announces immediate discontinuation, contract termination and removal process. The later physical-removal status is not independently established.
- Source-reported retained data, equipment counts, contract dates and budget amounts stay attached to the municipal original. No policy-effective date is inferred unless directly authenticated. **Zero exact GPS camera points and zero live sharing edges** are added.

These **11 source-hashed HTML publication records are distinct from the existing 18 agency dossiers with 25 individually source-page-reviewed PDFs**. The verified PDF dossier count is not inflated.

## All existing source-review gaps are actionable

`data/nationwide-original-source-and-agency-backlog-2026-10-27.json` enumerates the **12 known held government URL originals** with a specific follow-up for each source problem (redirect, HTTP error, size, wrong media, unreadable PDF or network timeout), plus **97 Washington AGO agency self-certification registrations**, with exact agency and official policy links.

- **11 of 97 WA agency originals** already have independent page reviews and exact original SHA checks. The state-issued registration is still not vendor proof.
- **86 of 97 WA agencies** retain an actionable original-policy page-review hold. A linked policy alone is not a verified Flock deployment or operating status.
- **Two official PDF candidates** include Robbinsdale, MN Policy 427, held for individual original-page review, and Brookings, SD Policy 13D1, which must be reconciled against its already reviewed original rather than counted twice.
- **99 unresolved review items** are precisely classified: 12 national original URL holds, 86 WA original-policy reviews, and one genuinely new original policy PDF candidate. The preexisting Brookings PDF is a duplicate, not new coverage.

A disposition **is not resolution of the underlying evidence**. These remaining source-review holds are clearly visible, searchable, and not automatically promoted to facts.

## Agency X-Ray, national matrix and camera source boundaries

- Agency X-Ray presents 11 new original government statements, the source-observed publication category, source date, original SHA receipt and original publisher URL. Nonrenewal/removal are not displayed as active.
- `agency-evidence-conversion.html` allows users to search the 11 authority-specific originals, compare two source-limited agency statements, and inspect the held national/WA/document review queue.
- The 51-state evidence matrix counts HTML-authority records separately from original-page-reviewed PDF dossiers and self-certified state agency registrations.
- The map now links three official geographic source documents: Apache Junction's 2026 municipal Flock diagram, Lexington's original government LPR location disclosure, and Columbia's publicly described ward-distribution material. They are **source-only references**; they do **not** create plotted coordinate points, routing sensors, coverage estimates or simulated detections.
- Existing vetted GIS point, provisional, community-report and schematic evidence tiers remain separate. A source-reported equipment count is never a substitute for precise underlying geographic evidence.

## Safety and CI

- `m11_conversion_acceptance.yml` tests source identity, shutdown-status classification, complete backlog dispositions, mobile browser comparisons, and map diagram evidence boundaries.
- `convert_official_flock_disclosures.yml` rechecks exact original government publishers, bound formats, claim-specific text and byte fingerprints on schedule; any drift is a review-only hold.
- The broader `audit_accountability_acceptance.yml` protects existing Agency X-Ray and national coverage flows from regressions.

**Remaining work that cannot be called complete:** independent original policy PDF verification for the 86 WA registrations and Robbinsdale Policy 427; resolving the 12 government source acquisition holds; identifying and verifying new exact geospatial camera locations; proving live data-sharing configuration and legal-effective dates. No statewide agency inventory has been completed.
