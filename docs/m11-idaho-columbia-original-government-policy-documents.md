# M11 · Additional official Idaho and Missouri ALPR governance original PDFs

Date reviewed: 2026-10-27. Independently acquired from original government publishers and source-hash/page verified in [GitHub Actions run 40633464566](https://github.com/ayeemecee0/Katoptron/actions/runs/40633464566), with a second strict original-page-claim verification workflow.

## Idaho Falls, ID · Original police procedure, not a signed Flock contract

[Original two-page Idaho Falls Police Department Supplemental Procedure 127](https://www.idahofallsidaho.gov/DocumentCenter/View/20519/Automated-License-Plate-Readers), department's published Lexipol document imprinted 2026/07/30. Original PDF SHA-256: 9d53f9a247818cffff263cd18cf2bf0a14ae66ceca20e126578625fd62e8cf60.

- [Page 1](https://www.idahofallsidaho.gov/DocumentCenter/View/20519/Automated-License-Plate-Readers#page=1): explicitly written for Flock Safety systems; normally 30-day custom hotlists; instructions against treating an alert alone as probable cause or reasonable suspicion.
- [Page 2](https://www.idahofallsidaho.gov/DocumentCenter/View/20519/Automated-License-Plate-Readers#page=2): category restrictions, documented search case/reason fields, 30-day standard evidence retention and case-preservation exceptions.

This confirms written source text, not measured present retention, audit compliance, legal-effective date, camera uptime, or any independently surveyed camera locations.

## Columbia, MO · Original adopted general surveillance ordinance, not Flock approval

[Original nine-page City of Columbia Ordinance 025792](https://www.como.gov/archive/2024/10/ordinance-025792.pdf). Original source SHA-256: 37e043de9a93a84337e3d9af37b7d4be377476084742832b63aca29353959f48. The [city's 2026 official review page](https://beheard.como.gov/safety-cameras-review) independently identifies Council's October 7, 2024 adoption of the law enforcement surveillance oversight ordinance.

- [Page 1](https://www.como.gov/archive/2024/10/ordinance-025792.pdf#page=1): city surveillance oversight process.
- [Page 2](https://www.como.gov/archive/2024/10/ordinance-025792.pdf#page=2): annual report obligations for general locations, interagency sharing, public complaints, internal audit findings and costs.
- [Page 4](https://www.como.gov/archive/2024/10/ordinance-025792.pdf#page=4): automatic license plate readers expressly within surveillance-technology categories. Inclusion is not vendor-specific procurement approval.
- [Pages 6–8](https://www.como.gov/archive/2024/10/ordinance-025792.pdf#page=6): technology use policy scope, retention, public notification, sharing and city council review procedures; preexisting technology policy transition.
- [Page 9](https://www.como.gov/archive/2024/10/ordinance-025792.pdf#page=9): police chief's annual report deadline before March 15 and subsequent public presentation.

The ordinance applies to police surveillance technology generally. It does not establish a distinct signed Flock purchase or agreement, prove that any report was filed, or furnish precise Flock equipment coordinates. The scanned signatures have not independently been visually compared; the original text and separate city adoption history corroborate the enacted policy framework.

## Implementation and guarded publication

- Original bounded source acquisition: scripts/inspect_idaho_columbia_originals.py
- SHA-pinned exact original page and claim validation: scripts/verify_idaho_columbia_policy_originals.py
- Two-source ledger: data/verified-idaho-columbia-government-policy-originals-2026-10-27.json
- Strict browser validator: new-state-original-policy-pages.js
- Public original government document comparison: new-state-policy-originals.html, linked from main map
- CI: inspect_idaho_columbia_originals.yml and new_state_policy_originals_acceptance.yml with source tamper and mobile Chromium tests.

**Two new individually page-reviewed government original documents, across Idaho and Missouri.** Both were already represented in the earlier HTML statements, but are now upgraded to separately source-PDF-reviewed governance records. This does **not** increase the 18-agency/25-PDF agency-dossier baseline until that separate indexed dossier ledger has been reconciled. No exact geospatial point, active sharing grant, live retention configuration or signed Flock vendor contract is generated.
