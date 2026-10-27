# Katoptron (Κάτοπτρον)

Katoptron is a **nationwide Flock Safety camera-map and route-surveillance education project**. Its primary product combines an evidence-backed map, an optional planned-driving-route simulator, and separately linked government records. The map NEVER invents camera coordinates: exact pins and approximate areas require distinct source verification. All simulated detections are hypothetical; the site never accesses private Flock plate reads or tracks actual vehicles. The legacy synthetic simulator remains available separately.

## Map and route engineering acceptance (October 26, 2026)

**M4 Maps & Routing engineering scope: 100% signed off** after live-origin
Geoapify, main map, independent community-route, accessible mobile browser,
and exact-count official-source corridor tests passed. Read the
[M4 engineering sign-off and evidence limits](./docs/m4-maps-routing-engineering-signoff-2026-10-26.md).
The [M4 code fix](https://github.com/ayeemecee0/Katoptron/pull/17)
prevents 1,000-row database response caps from silently hiding mapped sources:
dense regions are subdivided for complete route checking; if full retrieval
cannot be proven, results are **UNKNOWN** and simulated replay is withheld.
The [expanded browser test](https://github.com/ayeemecee0/Katoptron/actions/runs/40376719470)
independently confirms opt-in OSM comparisons do not change the Flock-only
model. Engineering completion is **not** national source completeness, a
verification of real detections, an external-provider quota guarantee, or M9
production launch readiness.

## Searchable published OSM nearby evidence and routing sample health (October 25, 2026)

- **[Search nearby community camera records](./nearby.html)** queries the latest complete persisted [OSM 15m proximity audit](./supabase/migrations/097_published_osm_nearby_candidates.sql) with exact OSM source-ID matching, distance bands and pagination. Each source link opens the original OSM node/way. The labels **possible geographic overlap** and **not confirmed same hardware** must never be promoted to active-camera or deployment claims.
- The first completed national published snapshot includes **4,935 near-coordinate source pairs**, **8,412 source records involved**, **1,927 pairs up to 5m**, and **3,008 pairs over 5m through 15m**, sourced from **116,159 community observations**. The earlier read-only CSV produced 4,929 pairs from a different 116,128-row download; these are distinct dated audits.
- Publication is fail-closed: the weekly worker stages source-key candidates privately, verifies the **exact count** against PostgREST, and only then marks the snapshot published. RLS blocks anonymous reads of incomplete snapshots. The underlying government camera list and original OSM report table remain unmodified. GitHub Actions also retains a short-lived CSV backup.
- The [hosted-origin Geoapify health monitor](./.github/workflows/monitor_route_providers.yml) now saves **daily fixed public fixture** routing and geocoding checks in an append-only [public health table](./supabase/migrations/098_public_fixed_route_provider_health.sql). The map presents the check date and separates passed, provider-error, inconclusive and stale states. It **does not** know remaining account-wide Geoapify credits or guarantee user route reliability.
- Both public-source systems use private worker credentials **only in GitHub Actions Node/Python steps**, never in static client code. They do not collect vehicle plate reads, private route history, or actual vehicle movements.

## National proximity audit and source freshness (October 25, 2026)

- A read-only nationwide scan of **116,128 OSM community observations** found **4,929 pairs at different coordinates within 15m**, involving **8,403 OSM records**. **1,924** pairs are within 5m, and **3,005** are 5–15m apart. These are potential overlaps, not proven identical cameras.
- [Audit results and candidate source-ID CSV](https://github.com/ayeemecee0/Katoptron/actions/runs/40164365899). The ODbL-derived artifact is retained for seven days by the workflow. The bounded [nearby candidate algorithm](./scripts/osm_nearby_candidates.py) runs weekly, makes **no database writes or merges**, and is separately validated across grid boundaries and high latitudes. Its public source is a different download from the earlier 116,159-row production snapshot.
- Individual OSM map popups now distinguish when the observation was last edited by an OSM mapper from when it was last included in an imported dataset. An edit older than a year is *not* evidence of inactivity or camera removal.
- The [routing-provider transport](./routing-provider.js) honors a bounded HTTP 429 `Retry-After` interval and will not repeat quota-limited requests during that browser's cooldown. Geocoding and routing failure state are separate. A failed route is **unknown**, not camera-free.
- Per-browser cooldowns **cannot establish account-wide quota usage**, which must be monitored with Geoapify's own dashboard. An existing scheduled hosted-origin check uses fixed public test routes; it does not collect private user routes.

## Independent community comparisons across driving alternatives (October 24–25, 2026)

- **Main map:** Opt-in `Compare community-reported cameras` checks **each supplied driving alternative**, not merely the selected route. Each route card independently displays the number of OSM observations within an **illustrative 120 m roadway proximity band**, and possible **30 m spatial overlaps** with government-verified locations when its official evidence scan completes. These are mapping comparisons only: no actual license-plate detections, estimated capture odds, safe-route ranking, or claim of current camera operation.
- The [bounded community route engine](./community-route.js) subdivides high-density bounding boxes, deduplicates source OSM IDs, and never treats a truncated response as a full census. The limit is **1,000 rows per query, 240 source queries and 40,000 distinct OSM records per alternative**. Exceeding any bound, a failed network query, or an unsupported complex corridor yields **UNKNOWN**, not a misleading zero.
- The community scan is canceled when a route is replaced or the option is disabled. Complete results are cached for each routing alternative; geometry-based proximity calculations are recalculated only if its official evidence changes. The original-government camera timeline and simulation do **not** consume community observations.
- [Automated end-to-end testing](https://github.com/ayeemecee0/Katoptron/actions/runs/40162013981) checked **two alternative routes** independently with a deterministic router and production-backed public OSM observations. [CI validation](https://github.com/ayeemecee0/Katoptron/actions/runs/40162033602) covers dense query subdivisions, exact-count fail-closed behavior, source deduplication and cancellation.
- The latest completed nationwide snapshot reconciliation yielded **116,159 community-reported observations**, distinct from **293 verified original-government GIS points**. The separate [possible overlap inventory](./supabase/migrations/095_possible_cross_source_osm_proximity.sql) found 172 government points with exactly one nearby OSM observation, 22 with multiple nearby observations, and 99 with none within 30 m; proximity is not confirmed device identity.

## Nationwide Flock-labeled community locations — major coverage expansion (October 24, 2026)

- **[Nationwide community camera map](./community-map.html)** exposes a distinct OpenStreetMap-derived public tier with **116,160 Flock-tagged camera-location observations in production** at the October 24–25 import checkpoint, compared with the earlier 293 separately verified original-government GIS points. This is a fundamental new geographic data source, not new government verification.
- The openly licensed source, `https://data.dontgetflocked.com/cameras.geojson.gz`, was audited in [read-only GitHub Actions](https://github.com/ayeemecee0/Katoptron/actions/runs/40158408183) with 144,273 point features and 116,128 Flock-branded at audit time; the subsequent fresh import yielded 116,160. Source changes between downloads explain why snapshot totals need not match.
- The [separate community table](./supabase/migrations/092_separate_osm_community_flock_camera_layer.sql) keeps immutable OSM IDs, point geometry and source dates under `community_osm`; the original-government camera inventory remains unchanged. The map uses bounded public Supabase viewport queries (zoom in for individual points), not an inaccessible third-party vector-tile CORS endpoint.
- The [importer](./scripts/import_osm_community_flock.py) validates source identity, geometry and complete-input bounds; the [successful full import](https://github.com/ayeemecee0/Katoptron/actions/runs/40158798913) populated production at ~66 MB total database size. These records have **not** been independently confirmed as operational, and may overlap original-government records. Never add community counts to verified GIS counts or default route simulation detections.
- Sources: © OpenStreetMap contributors, ODbL 1.0, redistributed by the [DeFlock open-data pipeline](https://github.com/flockhopper3/deflock-data). OSM source-item links are accessible from point popups. No plate reads or private movement data were acquired.

## First-party Flock Safety disclosures (October 24, 2026)

- **[Direct vendor transparency directory](./portals.html):** Katoptron now separately publishes **13 individually researched Flock-hosted agency portal snapshots in five states (CA, TX, WA, FL and AZ)**. The public source dates are in June–July 2026; these are historical source-snapshot metrics, **not live camera counts or present-day activity**.
- **[Vendor-source snapshot migrations](./supabase/migrations/088_vendor_first_party_portal_snapshots.sql):** immutable, source-dated Flock first-party claims about **LPR and other cameras**, retention days and past-30-day searches, hotlist hits and vehicle detections. A missing portal metric is represented as NULL, never zero. The vendor is authoritative about its own published claim; a second government citation is not required simply to attribute that claim to Flock.
- Vendor figures **do not create or supplement GIS camera pins**; verified geographic positions remain 293 across seven original-government source datasets. Menifee's vendor-reported 44 mixed-category devices do not establish a location for any of its 27 separately staged Esri candidate point features.
- **[Nationwide state evidence index](./supabase/migrations/090_public_state_vendor_evidence_footprint.sql)** contains three distinct counts: government-verified GIS points, dated government program notices, and agencies with Flock's own published disclosures. Vendor camera totals are never added to canonical GIS point totals.
- Source citations are exact original `transparency.flocksafety.com` URLs; new snapshots currently require individual source review. **No Flock API harvesting, browser scraping workflow, speculative coordinates, bulk sharing-partner republishing or unauthenticated database writing was introduced**. Confirm lawful authorized access before any automated feed.
- [Methodology](./methodology.html) explains how a future Flock-published **individual georeferenced camera inventory** can qualify as primary evidence without duplicative government confirmation. No such vendor-provided coordinates have been identified in these portal reports.

## Source-linked cross-period agency audits (October 27, 2026)

The [Accountability Audit](./agency-audit.html) now supports **22** exact-original independent audit reports in **17** reviewed Minnesota agency dossiers, with original PDF SHA-256 hashes and page-specific findings. **All 16 of the 16 state-index titles explicitly naming Flock have been independently page-reviewed**, including West Saint Paul (10 historical stationary Flock units) and Wyoming (four). These are auditor-attributed historical observations, not current device censuses, individual camera locations or assertions of wrongdoing.

Original historical comparisons document Woodbury's transition from BOSS-backed mobile ALPRs in the 2019–2021 period to stationary Flock in its 2024 report, followed by a same-manufacturer **15 → 17** historical stationary-unit comparison across its 2024 and 2026 audit reports. Edina has a separate, explicitly audit-date-only BOSS-backed mobile to later Flock stationary comparison. Shakopee has an Elsag mobile-reader history independently corroborated in 2022 and 2024, with Flock fixed/Axon squad equipment described in 2026. **BOSS is software, not proof of any manufacturer.** The engine never adds mobile and fixed units or infers a live camera count. An agency without two comparable reviewed periods displays **no comparable evidence**, not "unchanged".

See [cross-period validation and sources](./docs/m10-cross-period-original-audit-history-2026-10-27.md); raw plates, user routes, and personal data are not fetched or displayed.

## Automatic historical agency original-source review queue (October 27, 2026)

The [Minnesota original ALPR audit library](./mn-alpr-audits.html) now automatically surfaces a **prioritized original-document review queue**, derived from the existing state legislative index and the separately reviewed original audit catalog. The latest source scan found **137** original archive reports, **0** Flock-named titles remaining unreviewed after the October 27 expansion, and **21** additional same-agency historical or other-vendor audit candidates. **An older report title is not proof of earlier Flock equipment**; all candidates stay metadata-only until source pages are independently verified.

The [weekly historical original-source workflow](./.github/workflows/scan_mn_historical_queue.yml) inspects at most **12** priority original PDFs and creates SHA-256 / page-count receipts in a 14-day Actions artifact. The latest rotating batch successfully fingerprinted **12 of 12** selected original reports; two PDFs were temporarily unavailable to an earlier scanner batch, not confirmed withdrawn. It does not extract personal plate data or auto-publish PDF findings, make map pins, or claim live settings. Read the [original source queue architecture and verification limits](./docs/m10-automated-historical-alpr-original-review-queue-2026-10-27.md).

## National government-policy evidence and Washington statewide ALPR register (October 27, 2026)

The [national source library](./national-audits.html) has **eight additional original government PDF documents** independently hash- and page-checked from a nine-document discovery batch: Green Bay's historic published ALPR policy versus a **separately labeled unadopted draft** (30-day May retention text versus a seven-day September proposal); Green Bay's dated monthly aggregate use and named source-reported access list; the Green Bay Flock order form with stated $1.392 million five-year billing schedule but **unverified execution/payments**; Austin's original 2023 Office of Police Oversight memo and **nonbinding June 2025 commission halt recommendation**; and derivative auditor/grand jury summaries explicitly not counted as new investigations. The **ninth San Bruno policy link remains held**, as its original URL redirected and independently verifiable PDF bytes were unavailable.

[Washington's searchable public agency ALPR registrations](./wa-alpr-registrations.html) add **97** original Attorney General self-certification entries and **96 state-linked policy locations** in a source-dated snapshot, without treating registrations as proof of Flock cameras or certified vendor identity. The Attorney General says it has **not independently verified** those agency certifications. [Weekly statewide rechecks](./.github/workflows/build_wa_ag_alpr_registry.yml) flag changes without inventing shutdowns or newly installed cameras. Separately, the [national first-party source watch](./.github/workflows/scan_national_government_audit_sources.yml) now monitors **14 official government starting URLs across eight states**, adding Illinois and Washington. Some sources are unavailable to the strict exact-URL fetcher and remain unknown rather than silently published.

[Source-by-source original evidence, audit caveats and technical controls](./docs/m10-nine-original-policy-documents-and-washington-registry-2026-10-27.md).

## Six-state original government source watch and new oversight reports (October 27, 2026)

The [national original government ALPR library](./national-audits.html) now has **seven** individually original-PDF page-reviewed reports covering **five states**: California, Wisconsin, Minnesota, Texas and Oregon. The new additions include **two original government-independent oversight reports** (the [San Mateo County Civil Grand Jury](https://sanmateo.courts.ca.gov/system/files/grand-jury/auto-license-plate-readers-report.pdf) and the [Austin City Auditor](https://services.austintexas.gov/edims/document.cfm?id=452710)) and one distinctly labeled, **police-department-authored Woodburn impact assessment**. These sources establish dated findings and publisher-reported historical program changes, **not verified live ALPR camera locations, current network permissions or new Flock camera counts**.

The new read-only [weekly national original-government publication scanner](./.github/workflows/scan_national_government_audit_sources.yml) monitors **10 approved public publisher URLs across six states** (CA, WI, VA, TX, DE and OR). Its first source scan checked all ten and queued **13 relevant original government publication links** (**nine awaiting individual original-page review** and **four already source-reviewed**), fingerprinting three official original PDFs (all with **zero facts automatically promoted**). Candidates and provenance receipts are kept in a 14-day CI artifact and not automatically added as published claims. Its inputs are the [original government source registry](./data/national-government-audit-source-portals.json), and the [new reviewed CA/TX/OR government oversight manifest](./data/verified-national-government-oversight.json) uses its own recurring SHA-256 and page-text verifier. These are validated footholds, **not comprehensive nationwide source coverage**.

[Read the provenance, source roles, privacy limitations and next acquisition priorities](./docs/m10-six-state-original-government-source-watch-2026-10-27.md).

## Completed original-audit historical conversion and national report expansion (October 27, 2026)

- The [Minnesota state original audit library](./mn-alpr-audits.html) now reconciles all **21** previously identified exact-agency historical review candidates. **20** have newly independently source-page-reviewed external original reports; one 2017 Hennepin County internal audit was separately verified and clearly labeled as an **agency-internal report, not independently external-audited**. In total **42 source-pinned external Minnesota audit reports** are curated, with individually checked government PDF hashes and page references. An empty pending-review queue means only the original 21-candidate review set was processed; it does **not** establish a complete statewide or nationwide audit census.
- [Nationwide original government ALPR audit library](./national-audits.html) launches a separate evidence type for **four page-reviewed original agency-authored reports**, including two reports from **San Bruno, California**, one from **Green Bay, Wisconsin**, and the historical Hennepin internal report. State-level disclosure claims are cited to original public PDF pages and checked by weekly, exact SHA-256 and original-page verifiers. San Bruno's potential indirect sharing questions, Green Bay's publisher-stated 299 sharing agencies and separate Flock/Axon equipment classes are historical attributed claims, not a verified present sharing network or any map coordinates.
- **Evidence boundaries:** BOSS/PAGIS is historical back-office software, not Flock manufacturer proof. Elsag and Axon patrol-reader reports are displayed as their own original technology histories and never added to later stationary Flock equipment counts. Failed original fetches mean unavailable evidence, not camera or contract withdrawal. Original Hennepin County 2020 state-auditor PDF is publicly decryptable with an empty user password; its verification still requires the exact pinned source hash and page anchors, without credentials.
- [Original sources and acceptance methodology](./docs/m10-national-original-audit-acquisition-2026-10-27.md) records this bounded conversion. This is a **first expansion into two additional states**, not completed nationwide source acquisition. Regional independent audit and agency-authored audit evidence tiers remain separated.

## Milestones 7–9 — Analytics, accessibility and launch controls (October 23, 2026)

**M9 unattended production preparation ~90% (October 26):**
[Read the current production hardening and residual launch gates](./docs/m9-unattended-production-hardening-2026-10-26.md).
Service-role-only private quota monitoring passes; public GIS no longer exposes
anonymous SECURITY DEFINER source predicates; browser, Auth/Storage, public health
and release workflows have fresh successful checks; the first nine-workflow
release heartbeat passed. **Full private-account production is NOT certified**
until owner-controlled actual email delivery and confirmation, encrypted private
Auth/DB/Storage backup restore, account-side key/quota safeguards and independent
human accessibility/beta tests are approved. The public evidence-limited beta
remains available without claiming nationwide camera completeness.


- [Public evidence analytics](./analytics.html) now accurately separates **293 original government GIS points source-labeled Flock**, **23 generic government LPR points whose manufacturer is unconfirmed**, **0 independently corroborated published sites** and **12 source-attributed unconfirmed municipal observations**. Those categories may not be added to claim unique operating devices. The latest original-government total is **316** GIS points, with **24** documented government programs, **34** accountability records and **17** states with some public evidence (October 26, 2026). This is **not** a national surveillance census.
- **M7 analytics engineering 100% accepted:** [M7 signed-off original source reconciliation](./docs/m7-evidence-analytics-engineering-signoff-2026-10-26.md) fixes a prior false "12 corroborated" chart, verifies exact database row counts and reconciles Flock/generic/unknown manufacturer labels nationally and by state. Full browser, database, privacy, accessible UI and CSV checks pass.
- [Evidence analytics design and source limitations](./docs/milestone-7-evidence-analytics.md): security-invoker SQL views, dated monthly **records**, state comparison and safeguarded CSV export. No telemetry or private contributions.
- **M8 accessibility preparation ~95% (October 26):** [M8 automated acceptance and outstanding manual gates](./docs/m8-autonomous-accessibility-acceptance-2026-10-26.md) documents passing axe-core WCAG A/AA screens at **320/390/1280 CSS pixels** on all 11 public pages; separately passing real Chromium **320px forced-colors, 24px targets, painted keyboard focus, reduced motion and text-spacing** checks on all 11 pages; and full browser mobile/map/route acceptance. High-contrast CSS, focus visibility and touch target areas have been hardened. **These tests do not establish actual NVDA/VoiceOver/JAWS compatibility, real physical-device access or WCAG 2.2 AA certification.** The earlier [M8 implementation record](./docs/milestone-8-accessibility.md) remains available.
- [Launch, operations and blocker checklist](./docs/milestone-9-production-readiness.md): public health monitors, public-only weekly snapshots, error-response guidance and a public issue form for original-evidence corrections. **Private Supabase data is not backed up by GitHub Actions**.
- Existing Katoptron Supabase organization remains **Free**, and no new paid hosting was provisioned. The Geoapify browser key is public; the owner verified the configured GitHub Pages origin and the live hosted allowed/rejected-origin browser tests passed. The provider remains quota-limited and is not a contracted uptime SLA. The public evidence-limited MVP is distinct from broad private-contribution production readiness; see the current [MVP acceptance checklist](./docs/mvp-beta-user-acceptance.md).

## Milestone 6: Government accountability (October 23, 2026)

- [Accountability directory](./accountability.html): browse the source-backed, deduplicated original-government record index by state, type and documentary date; inspect original sources and export public records with full evidence links.
- Published facts keep program disclosures, original agenda mentions, legislative decisions, editorial government actions, executed agreements, contract-form PDFs and agency-reported deployments in **separate evidence categories**. No inference from council action to an individual vote or a signed contract.
- Public figures: dated company-issued Flock Safety professional-role evidence is explicitly labeled as vendor attestation, **not** live employment verification. Individually recorded government votes or public statements can be published only from original named evidence; none have met that threshold in the present database.
- Production directory initially contains 30 distinct government entries (20 programs, five agenda mentions, four editorial actions, one deployment). The original 33 source rows remain intact for audit, while duplicate undated disclosures are hidden in the directory. There are no verified executed contracts or individual votes yet.
- RLS-invoker public views, private-only review authority, source-provenance checks, SQL regressions, browser smoke and read-only health monitoring were implemented. The latest GitHub Pages/CI results still need separate release confirmation.
- [Milestone 6 engineering and acceptance report](./docs/milestone-6-government-accountability.md).

## Milestone 5: Community evidence submissions (engineering signed off October 26, 2026)

**M5 reporting engineering is 100% accepted**, following actual disposable
authenticated-user JWT, real private Storage upload/download/owner deletion,
editorial audit, withdrawal, account-owned permanent report erasure and cleanup.
[See the full M5 engineering sign-off and retained launch caveats](./docs/m5-community-reporting-engineering-signoff-2026-10-26.md).
The [live end-to-end QA](https://github.com/ayeemecee0/Katoptron/actions/runs/40381340892)
passed and removed every disposable test identity and private photo. Real
email delivery and confirmation-link usability are **not** established by the
admin-confirmed temporary QA test accounts and remain an M9 launch gate.

- [Report possible Flock cameras](./submit.html): signed-in intake, evidence URLs, dates and optional metadata-stripped private images, limited to three reports per contributor in a true rolling 24-hour window.
- [Private reviewer dashboard](./community-review.html): allowlisted editorial reviewers inspect private screening matches, photos and supporting URLs, with written and audited reviewer outcomes.
- **Automatically staged does not mean verified.** Eligible report details enter the separate private candidate queue only; no new report can certify itself, enter canonical verified counts or appear publicly without separately qualifying reviewed evidence.
- Contributors can inspect their own report history, attach a requested missing private photo or original HTTPS link, withdraw reports and delete their own private photos through Storage. After successful photo removal, they can permanently erase the withdrawn report and its report-derived evidence without resetting the rolling three-report anti-spam allowance.
- Public publication permission is separately requested and **off by default**. Public case eligibility still checks independent evidence provenance and review status.
- [M5 final acceptance](./docs/m5-community-reporting-engineering-signoff-2026-10-26.md) confirms real Auth JWT and private Storage HTTP upload/download/owner-delete plus negative permission tests, all with disposable cleanup. Email link delivery to an actual human-owned mailbox remains untested.

## Current project status

- **Primary public experience:** [Nationwide camera map and route simulator](https://ayeemecee0.github.io/Katoptron/) is the homepage. Search arbitrary US start and destination points, display real roads from a public routing demo, inspect any published evidence-backed camera pins or uncertainty areas, and optionally replay clearly distinguished synthetic potential sightings.
- **Map records database:** [Migration 018](./supabase/migrations/018_camera_map_locations.sql) creates the RLS-protected `flock_camera_locations` table. **293 original-government verified exact GIS points in seven jurisdictions** were confirmed in production and independently recovered from an owner-held SQL backup on October 24, 2026: Peoria AZ (74), Newport Beach CA (69), Webster TX (53), Lawrenceville GA (45), Monroe WA (18), El Paso County CO (16), and Alachua County FL (18). Unmapped areas do not demonstrate absence of surveillance.
- **Archived fictional simulator:** [Original synthetic model](https://ayeemecee0.github.io/Katoptron/legacy-simulator.html) remains accessible for demonstrations.
- **Source-verified public database:** [Verified government records](https://ayeemecee0.github.io/Katoptron/records.html), backed by Supabase read-only public views and row-level security.
- **Automatic public evidence verification:** [Daily discovery workflow](./.github/workflows/discover.yml) finds official government matters, then [automatic Flock mention verification](./.github/workflows/auto_verify_agenda.yml) re-fetches live Legistar records and publishes only exact, source-verified agenda mentions with explicit Flock Safety titles. No manual click required.
- **Automatic legislative-action verification:** [Legislative decision verifier](./.github/workflows/auto_verify_decisions.yml) independently checks dated official Legistar history events, exact adoption/failure wording, governing body and matching pass/fail flag. The [public records page](./records.html) displays only qualifying events as *recorded legislative decisions*, not signed contracts. No manual review required for qualifying events.
- **Optional exceptions review:** [`agenda_evidence_reviews`](./supabase/migrations/006_legistar_source_integrity_and_review.sql) holds ambiguous or incomplete records. The [review dashboard](https://ayeemecee0.github.io/Katoptron/review.html) is available for difficult contract, action, or deployment claims, not required for already-proven official agenda mentions.
- **Explicit government-domain authority:** [Government-domain approval policy](./docs/official-government-domains.md) limits custom domains and ambiguous Legistar tenant aliases to individually reviewed government evidence.
- **Automated code and database checks:** [Validation workflow](./.github/workflows/validate.yml).

**Automation policy:** Public government agenda mentions with exact, re-fetched official API titles naming **Flock Safety** are published automatically. They are labelled as *agenda mentions*, never approvals, signed contracts, vendor payments, or installed cameras. Automatically verified legislative action events now have a separate evidence tier; signed contracts, individual votes and deployments still require stronger source rules.

Read the [automation and source-integrity policy](./docs/automatic-official-verification.md) for the current operating model. The [October 2026 project audit](./docs/project-audit-2026-10-21.md) documents the earlier manual-first architecture and the original data-quality findings.

## Source integrity and publication policy

- **Discovery is not verification.** Search snippets and news reports remain private. A government agenda mention may be published automatically only after an exact live API matter match, explicit Flock Safety in the official title, and pre-verified tenant/jurisdiction identity.
- **Flock Safety is not synonymous with ALPR.** Vendor identification must be explicit in the linked primary government source.
- **An authorization is not an executed contract.** Distinguish proposed, failed, adopted, signed, deployed, superseded, and terminated statuses. Do not infer an individual's vote from an agency-level decision.
- **Original primary sources:** official government records are linked wherever available. The Legistar API's `MatterId` is not assumed to equal a public LegislationDetail page `ID`.
- **Publication is evidence-tiered.** Official Flock agenda mentions and corroborated legislative action-history events are verified automatically in separate read-only public tables. The workflow service-role still cannot write verified human-edited actions, executed contracts, deployments or personal voting records. The optional reviewer interface remains for unresolved claims.
- **Privacy:** no private number plates, individual movement histories, personal addresses, or inferred real camera routes. All simulator vehicles, cameras, and detections are fictional.

## Repository

| Path | Purpose |
| --- | --- |
| [`index.html`](./index.html) | Synthetic simulator and clearly identified illustrative research links |
| [`records.html`](./records.html) | Live, verified public records; not the unreviewed news/agenda queue |
| [`scripts/discover.py`](./scripts/discover.py) | Unverified news leads |
| [`scripts/discover_official.py`](./scripts/discover_official.py) | Government-page discovery; **review-only** |
| [`scripts/discover_source_registry.py`](./scripts/discover_source_registry.py) | Conservative government-source and Legistar portal discovery |
| [`scripts/verify_government_sources.py`](./scripts/verify_government_sources.py) | Checks official government links, jurisdiction identity, and Legistar API access |
| [`scripts/discover_government_records.py`](./scripts/discover_government_records.py) | Bounded historical Legistar scanner, queues exact official API MatterIds |
| [`scripts/auto_verify_flock_agenda.py`](./scripts/auto_verify_flock_agenda.py) | Automatically verifies exact official Flock Safety agenda mentions from live API titles |
| [`scripts/auto_verify_legislative_decisions.py`](./scripts/auto_verify_legislative_decisions.py) | Automatically verifies exact dated full-legislative-body outcomes with corroborating pass/fail fields |
| [`.github/workflows/auto_verify_agenda.yml`](./.github/workflows/auto_verify_agenda.yml) | Runs after successful government discovery and on relevant updates |
| [`.github/workflows/auto_verify_decisions.yml`](./.github/workflows/auto_verify_decisions.yml) | Automatically verifies recorded legislative action events after source verification |
| [`supabase/migrations/013_automatic_verified_flock_agenda_mentions.sql`](./supabase/migrations/013_automatic_verified_flock_agenda_mentions.sql) | Immutable verified agenda mentions, public read-only policy and exact-provenance guards |
| [`supabase/migrations/015_auto_legislative_decisions.sql`](./supabase/migrations/015_auto_legislative_decisions.sql) | Independently verified, immutable, dated legislative events with revocation cascade |
| [`docs/automated-legislative-decisions.md`](./docs/automated-legislative-decisions.md) | Exact evidence requirements, interpretation limits and live validation logs |
| [`supabase/migrations/`](./supabase/migrations/) | Database schema, reviewed government-domain authority, editorial staging, and publication guards |
| [`docs/project-audit-2026-10-21.md`](./docs/project-audit-2026-10-21.md) | Full audit, known limitations, and next-step priority |

## Operations

The database is already created and connected. Migrations **003 through 015** have been applied to the existing Supabase project; migrations 001 and 002 were the initial schema setup. All new migrations are tested in a disposable PostgreSQL database before production.

To launch a new discovery run, use [Discover public Flock records](https://github.com/ayeemecee0/Katoptron/actions/workflows/discover.yml) and select **Run workflow** on `main`. The workflow runs daily on a schedule.

Only the Supabase **publishable key** is permitted in browser code. Keep the database service-role key restricted to GitHub Actions secrets and trusted server-side operations.

## Next milestone

Build automated verification for **executed Flock Safety contracts** from signed government agreements or equally authoritative contract records. Legislative-decision verification is now implemented and will publish only when explicit governing-body action, action date and pass/fail evidence agree. No future verification tier should infer signed contracts or deployments from proposal titles.

## Route/map MVP limitations and next milestones

The core map and route simulator are implemented as a static GitHub Pages site backed by a new read-only Supabase public camera-location interface. The API is intentionally empty until independent verification of specific camera coordinates or municipal deployment areas. This is not an all-camera census, and a city having Flock-related agenda records does not prove where cameras are deployed.

The **next implementation priority** is automatic camera discovery, source verification, and duplicate suppression from official georeferenced inventories and independently corroborated public data, holding uncertain reports unpublished. Only then will map pins appear. Community submissions should be accepted into private candidate storage, not automatically into the public map.

The beta uses [Photon's public demo geocoder](https://github.com/komoot/photon) and the [OSRM demo router](https://github.com/Project-OSRM/osrm-backend). They can throttle, reject or become unavailable. Before widespread traffic, use properly provisioned geocoding and routing infrastructure. Queries go from the user's browser directly to these services; Katoptron does not persist route searches, license plate numbers or inferred personal home/work locations.

The proximity simulation's 120-metre radius is an illustrative **route-to-mapped-point** distance threshold, not a manufacturer-specified camera reading range. Approximate program areas never produce point-camera detection events. An optional fictional-sighting toggle adds completely synthetic samples only to the route demonstration and never to the confirmed camera inventory.


## Daily nationwide camera-source pipeline (October 2026)

Official camera coordinates and crowdsourced claims have **separate security tiers**. The official GIS workflow checks only authority bindings already approved in the database and specifically supported by code. Its first production scan qualified 18 Monroe, Washington Flock ALPR cameras from the city's own camera-systems point layer. Record locations are immutable, new coordinate evidence uses distinct fingerprints, and missing/changed records are revoked only after a complete official inventory check. A separate freshness timestamp records successful rechecks.

The nationwide community import streams an OSM-derived US camera dataset maintained by FlockHopper/DeFlock, © OpenStreetMap contributors, ODbL 1.0. On its first successful production run, it inspected 143,968 ALPR features, found 115,934 Flock-tagged candidate entries, and submitted 1,586 records from one 30-day rotating shard to the **private unverified** research queue. That queue is NOT a list of verified Flock cameras. OSM mirrors are not independent corroboration of OSM.

Current remaining work: broaden official municipal GIS source bindings with separate government evidence for each city; implement independent-source corroboration for queued community points; provide rate-limited community submission intake; and add administrative alerting for delisted GIS assets. No routine manual approval is required for fully proven source-bound GIS records, and uncertain cases stay private.


## GIS discovery expansion and evidence revocation (Oct 21, 2026)

New ArcGIS layers cannot be assumed to be government-owned merely because their titles say Flock. The [GIS candidate workflow](.github/workflows/discover_camera_gis_sources.yml) checks pinned ArcGIS point layers and queues metadata privately. Savannah municipal council Flock procurement records do not independently establish ownership or installation status of a specific ArcGIS layer, so those layers remain unverified candidates, never new public camera pins.

[Migration 021](supabase/migrations/021_camera_gis_authority_candidates.sql) ensures new government GIS camera publications require currently verified source/jurisdiction authority, and revoking authority withdraws already published pins from anonymous queries. The scheduled worker cannot approve new authoritative sources.

The [cross-source evidence matcher](.github/workflows/match_camera_evidence.yml) compares OpenStreetMap community reports with already verified municipal GIS camera positions using a maximum 30-meter proximity threshold. [Migration 022](supabase/migrations/022_camera_source_matches.sql) recalculates distance server-side and rejects mismatches. These private evidence links are not additional public cameras. Unmatched reports stay private.


## Owner-bound automatic government GIS verification

The county expansion adds a [government root binding](./supabase/migrations/023_owner_bound_gis_authority.sql), a [live authority verifier](./scripts/auto_link_gov_gis.py), and [daily GitHub Actions](./.github/workflows/auto_link_gov_gis.yml). Owner-reviewed GIS authority is limited to a particular El Paso County government-operated host and exact Sheriff layer path. The verifier independently re-fetches the county government GIS web page, GIS map-service metadata, Flock_Cameras point layer schema, and nonempty bounded feature inventory. Only if all checks succeed does an auditable database function promote the source. Daily location ingestion then separately verifies current official layer metadata before public publication. Third-party ArcGIS layers still cannot be promoted solely from names or vendor mentions.

The first production run automatically approved the county's source and discovered 16 county Flock-camera points, raising the verified map inventory to 34. This is not a nationwide camera census, proof the devices are active, or evidence of real ALPR detections. To add a different government domain, its original government identity must first be independently established and root-scoped. The current verifier does not crawl every municipality or automatically trust arbitrary government subdomains.


## Production readiness

See [Current production readiness audit](./docs/production-readiness-audit-2026-10-22.md), [evidence methodology](./methodology.html), and [privacy](./privacy.html). Live government GIS source verification covers five jurisdictions, with additional private candidates from national discovery. Public demo route/geocoder infrastructure is not a production-scale service.


### Third verified GIS deployment: Peoria, Arizona

On October 22, 2026, Katoptron independently checked the City of Peoria government's GIS host, its Public Works MapServer point layer 286 explicitly named Flock Cameras, and its individual CameraID and Location fields. The live read-only probe returned 74 features with valid camera identifiers and geographic coordinates. Migration [026](./supabase/migrations/026_peoria_city_camera_source.sql) approved this exact municipality-operated layer; the existing daily verifier independently reread layer metadata, published 74 records, and rechecked 34 previously published points with zero production errors. These are published GIS points, not proof of active readings.


## Nationwide location/map milestones 1–3 (October 22, 2026)

**Government GIS discovery:** The older official-source pipelines remain, plus [daily nationwide 50-state search rotation](./scripts/discover_nationwide_gis.py) that accepts *only original public government webpages* into a private candidate queue. Because Bing and DuckDuckGo returned no usable .gov search hits in the first run, it now also seeds from the existing nationwide discovery/verified-agenda registry. The [independent GIS catalog scanner](./scripts/discover_government_gis_catalog.py) walks folders and layer metadata on owner-approved municipal GIS servers; a matching Flock layer becomes an unverified candidate, never automatically an approved host or a camera pin. Search/indexing may still miss government pages.

**Universal verifier:** [Profiles migration 028](./supabase/migrations/028_camera_profiles_history.sql) stores immutable owner-reviewed camera classification profiles, and [generic official GIS verifier](./scripts/auto_verify_camera_profiles.py) applies them without per-city Python exceptions. Its first production recheck qualified all 108 existing points and rechecked them without duplicate publications or withdrawals. New sources still require independent government authority and reviewed verification rules before automatic publication.

**Nationwide map usability:** The homepage adds city/address/map coordinates search, jurisdiction and record-label filters, explicit original source evidence tiers, and per-camera public [evidence event history](./supabase/migrations/028_camera_profiles_history.sql). A separate directory of [dated government programs without camera coordinates](./supabase/migrations/030_government_programs_without_coordinates.sql) includes original government publications from South Portland ME, Provo UT, League City TX, Perry GA and a **terminated** Los Altos Hills CA program. These are text/source records, **not fake pins or active-coverage assertions**. No credible deployment geometry source has yet qualified for publication of an approximate mapped area.

**Completion limitation:** The software stages and map interfaces are developed, but nationwide evidence coverage remains sparse (206 government GIS points, five jurisdictions). Broad-source discovery, automatic government-root authenticity for newly discovered hosting providers, and independently verified approximate area geometries remain ongoing. Do not claim the entire nationwide camera inventory is complete.


### October 22: Lawrenceville GA and Webster TX municipal GIS expansion

Independent current city-hosted GIS source probes and original city GIS portal documentation supported two more municipality-specific verified source profiles. Lawrenceville GA [original city GIS portal](https://www.lawrencevillega.org/592/GISMaps) links the city-owned point layer containing 55 camera records, but its CameraType field explicitly identifies only 45 as PD Flock Cameras; the other ten PD School Cameras are **excluded**. Webster TX [city Maps directory](https://www.webstertx.gov/868/Maps) links the city's GIS host, whose service explicitly identifies Webster PD Flock license-plate cameras, with 53 named points. The profile-driven publishing pipeline confirmed 45+53 new verified points and rechecked the previous 108. Current Katoptron public camera inventory is **206 exact government GIS points across five regions**, not a national census or evidence cameras are operational.


### Nationwide ArcGIS catalog discovery

The [ArcGIS Online search worker](./scripts/discover_arcgis_catalog.py) runs each day using Esri's documented [public item search API](https://developers.arcgis.com/rest/users-groups-and-items/search/). It examines only public ArcGIS Feature Service metadata on allowlisted Esri-hosted URLs and stages candidate Flock point layers **privately**. The first production run found 15 candidate services, successfully examined 14, and submitted six additional unverified Flock source layers (ten private GIS candidates total). It cannot authorize a government source, geolocate a published camera, prove vendor ownership or infer operational status. Original government host authentication remains a separate prerequisite. No camera was auto-published from an ArcGIS title alone.

### Government ownership evidence correlation and fail-closed publication

The [government-link corroboration workflow](./scripts/corroborate_candidate_government_links.py) compares each privately staged ArcGIS candidate against **exact URLs actually linked from original, previously verified municipal disclosure pages**. Every positive match retains the government page URL, original HTML digest, GIS link and link label in the private `government_gis_disclosure_leads` registry. No third-party map title, search result, or hyperlink receipt is sufficient to promote a new trusted source on its own.

The production pipeline initially returned no exact original-government hyperlinks to its 10 private GIS candidates after checking 10 accessible government source pages; accordingly, no candidate was published. Its daily scheduled runs can discover new evidence as government disclosures change.

National .gov page discovery now pages its archived government-source URLs instead of overfilling the backend API response buffer. The first successful resumed scan found seven government URL leads, examined five pages, and staged four original government Flock citations privately. These are *research evidence*, not verified camera coordinates.

Browser smoke uses a pinned official Playwright container with its Chromium dependencies already present, eliminating a long installation stall. The [successful Chromium job](https://github.com/ayeemecee0/Katoptron/actions/runs/39826753143) covered the current public map and synthetic route. The read-only service-role grant in [migration 032](./supabase/migrations/032_readonly_backend_government_program_citations.sql) allows private verifier jobs to use already-published government-program citations without granting data writes.

## Milestones 1–3 implementation checkpoint — October 22, 2026

**Nationwide discovery:** The 50-state original-government web search rotation, public ArcGIS item scanner, municipal GIS catalog crawler and original-government hyperlink correlator run independently. New .gov-operated GIS sources can now qualify without city-specific Python code only when a fresh original government Flock page directly links the exact GIS point layer on the same government domain family. Changed government HTML with the same verified camera map link is captured in append-only evidence history. Unverified GIS records remain private.

**Universal verification:** Generic camera source profiles support government GIS and explicitly government-endorsed Esri-hosted Flock data as distinct provenance categories. The latter requires a reviewed original-government page, an exact map-layer hyperlink, unique ArcGIS item/organization identity, complete original camera IDs, bounded geometry and deduplication. All published sources are rechecked; successful detection of a removed official link withdraws the associated source and camera pins. Transient web failures do not trigger revocation. Camera encounter simulation remains illustrative and never uses real plate reads.

**Nationwide map:** Exact government GIS pins, separately dated government program records, source history, location search, jurisdiction filters, mobile layout and route replay are live. Source-backed deployment polygons have a separate government GIS verifier and are never fabricated from a city boundary or a guessed camera radius.

**Actual published coverage:** 206 verified camera GIS points across five jurisdictions (Peoria AZ 74, Webster TX 53, Lawrenceville GA 45, Monroe WA 18, El Paso County CO 16). Ten additional ArcGIS source layers and four government pages remain unverified research leads. There are **zero qualifying approximate deployment polygons** and no additional newly qualified national government source. This is a working nationwide data-acquisition and visualization system, **not** an exhaustive nationwide camera inventory.

Key workers: [first-party government source verification](./scripts/auto_register_original_gov_gis.py), [externally hosted government-endorsement verification](./scripts/auto_attest_external_arcgis.py), [generic live GIS checks](./scripts/auto_verify_camera_profiles.py), [government source withdrawals](./scripts/recheck_auto_original_gov_gis.py), [ArcGIS endorsement withdrawals](./scripts/recheck_external_arcgis_endorsements.py), and [original deployment polygons](./scripts/discover_official_flock_areas.py). The full migration series includes 034–042 with RLS and backend-function privilege regression tests.

**Remaining non-software blocker for nationwide coverage:** Government agencies often do not publish individual camera coordinates or Flock deployment geometry. The system must hold those locations unknown, not guess or make publication rules less strict. Later product milestones, including production routing providers, community intake, full accountability directory, accessibility, load tests and operations hardening, are not complete.


### October 23: five additional dated original-government Flock program disclosures

Katoptron's text-only public directory now contains **10 original-government program records** in addition to 206 exact GIS camera locations. Five newly reviewed official disclosures are [Leander TX](https://www.leandertx.gov/995/Flock-FAQ) (explicitly **terminated** September 4, 2026), [Hidden Hills CA](https://hiddenhills.gov/2026/09/30/flock-safety-license-plate-cameras-faq/) (three guard-shack Flock ALPR cameras reported), [La Cañada Flintridge CA](https://lcf.ca.gov/public-safety/flock-alpr-public-safety-cameras/) (LASD-administered Flock program), [Prosper TX](https://www.prospertx.gov/748/Technology-Transparency) (license-plate readers and distinct live-feed camera technology), and [Shakopee MN](https://www.shakopeemn.gov/public_safety/police_department/reports___transparency.php) (seven Flock ALPR cameras described, with specific offline/relocation disclosures). **No camera pins or deployment polygons were inferred from prose, approximate intersections, or an agency's program count.** These text records remain dated historical/public-agency claims, not current uptime assertions.

An additional safeguard now applies when a city directly endorses a third-party ArcGIS *service-root* link: the live service listing must contain **exactly one** Flock camera layer matching the numbered dataset; a partial candidate registry cannot make an ambiguous multi-layer map appear authoritative. This safeguard is distinct from direct numbered-layer government hyperlinks.


### State-level completeness: GIS points versus non-georeferenced agency evidence

The [source-specific state evidence index](./supabase/migrations/048_state_evidence_index_pins_and_dated_programs.sql) uses a row-level-security-invoker view to report two **separate** measures: exact government GIS camera points, and dated official Flock program disclosures (including those that were terminated). States with documented programs but without verified camera GIS coordinates appear with an explicit **actual coverage unknown** label. No city-centroid pin, county-shaped deployment polygon, or assumed camera number is created from these records. As of October 23 the view has nine states with some sourced information; four have only unlocated program disclosures. All other states remain unknown, not necessarily Flock-free.


### October 23: Asheville, Seabrook and Newport Beach original-government records

[Asheville city council minutes](https://council-minutes-archive.ashevillenc.gov/Minutes.2026-08-25.html) document adoption of Resolution 26-180 by a 5–2 vote, calling for termination of its Flock contract and suspension of access. They mention eleven former city-operated devices, **not verified physical removal**. [Seabrook police FAQ](https://www.seabrooktx.gov/m/faq) lists eight installed Flock readers by intersection and direction, but no independently surveyed pin coordinates. [Newport Beach Legistar](https://newportbeach.legistar.com/LegislationDetail.aspx?GUID=84D5BF30-0671-47C6-939F-5266748FCD6B&ID=7643929&Options=&Search=) records a proposed September 2025 Flock-contract amendment; the agenda is not proof of its adoption. With these three entries the original-government disclosure directory covers **13 dated records**, three explicitly reporting termination decisions, while the independently georeferenced camera map remains at 206 source-backed points.

The separate public Newport Beach GIS catalog lists a **Flock Unit Locations** layer in its broader EmployeeMasterMap. A private read-only endpoint probe checks accessibility and schema only; no individual locations from this staff-oriented GIS service are assumed suitable for public republication without independent review and source confirmation.


### Sixth verified government GIS jurisdiction: Newport Beach, California

The public [City GIS NewportGIS Geocortex layer directory](https://nbgis.newportbeachca.gov/Geocortex/Essentials/REST/sites/NewportGIS/map/mapservices/7) directly lists **Flock Unit Locations** (#299) within the City-operated `EmployeeMasterMap/MapServer`. Separately, [official City Legistar Flock records](https://newportbeach.legistar.com/LegislationDetail.aspx?GUID=84D5BF30-0671-47C6-939F-5266748FCD6B&ID=7643929&Options=&Search=) establish the Flock program. The source uses typed `OBJECTID_12` and `FlockUnitNo` fields rather than ordinary `OBJECTID`; a revised source-profile verifier now supports this independently authorized OID variant. A privacy-preserving read-only probe verified **69 point geometries, 69 uniquely identified Flock units, and a complete stable ArcGIS returnIdsOnly inventory**. Migration [050](./supabase/migrations/050_newport_beach_official_flock_unit_locations.sql) grants authority to only this exact original City GIS layer; the sharded production verifier published 69 official GIS point coordinates. No staff notes, additional employee GIS attributes, plate reads, device uptime claims, or other unreviewed map layers were copied. The public map now contains **275 exact source-backed GIS points across six jurisdictions**. Newport Beach remains a dated source-specific snapshot rather than a claim all 82 devices in the vendor's July report have surveyed positions.


### October 23: seven more original-government Flock program notices (20 total)

The separately sourced, text-only nationwide program directory now contains **23 original-government records in 13 states**, five documenting terminated city programs or council actions. The new original sources are: [Henrico County VA](https://henrico.gov/news/2026/10/henrico-police-to-eliminate-flock-cameras/) (announced intention to cancel; completion unverified); [Panama City FL](https://panamacity.gov/m/newsflash/home/detail/811) (September 8 vote affecting 41 state-right-of-way Flock devices, with remaining city devices unresolved); [Lafayette CO](https://www.lafayetteco.gov/m/newsflash/home/detail/10277) (ended use and started early termination, with removal pending); [Elgin TX](https://www.elgintexas.gov/m/newsflash/home/detail/1855) (council ended city's association); [Liberty Hill TX](https://www.libertyhilltx.gov/m/newsflash/home/detail/395) (city states program cameras removed); [Poughkeepsie NY](https://www.cityofpoughkeepsie.gov/m/newsflash/Home/Detail/417) (mayor **intended** to veto a termination measure, not proof that a veto occurred); and [Las Cruces NM](https://lascruces.gov/lcpd-provides-video-transparency-portal-on-flock-cameras/) (police introduced a Flock transparency portal). Every record carries its date and original government URL; none creates a camera pin or polygon. On October 24 two additional official agency cases were recorded: [Apache Junction, AZ](https://apachejunctionaz.gov/1241/Public-Safety-Technology) and [Alexandria, VA](https://www.alexandriava.gov/police-department/license-plate-reader-dashboard-and-response-to-city-council-questions-on-flock). They link dated official police camera maps as **cartographic documents** rather than machine-readable verified camera points; no screenshot-derived coordinates were promoted. On October 24, the [original Menifee Police Department ALPR page](https://menifeepolice.org/automated-licesnse-plate-reader/) was added as an additional program-only entry. A separate first-party publisher-associated GIS Flock layer yielded 27 complete original point features, privately staged for individual authority review; none was publicly promoted. Current independently verified exact point inventory is **293 across seven jurisdictions**.

### Source-specific withdrawals

Migration [053](./supabase/migrations/053_two_pass_official_gis_withdrawals.sql) requires **two complete original GIS camera inventories at least 12 hours apart** before an individual coordinate can be withdrawn from the public map because it disappeared from one GIS inventory. A single missing record is held in a private ledger; reappearance clears the hold. Mass changes or partial inventories remain fail-closed, while a separately verified **government source revocation** continues to withdraw its dependent records according to its original authority policy. Backend-only privileges, real rollback transaction tests and automated verifier checks cover this distinction.


### Genuine original-government programme polygons without camera pins

[Migration 055](./supabase/migrations/055_government_program_sourced_flock_areas.sql) now supports a second, independently protected polygon-evidence channel: an original government Flock programme record can directly hyperlink an original GIS **Flock deployment-area polygon** even where no individual camera coordinates have been released. It does **not** inherit any camera-point authority. The original source must still have a live direct GIS link, exact government apex, explicit Flock-specific polygon layer, stable GIS feature identifiers and verified closed original WGS84 rings; generic city boundaries, arbitrary buffers, school cameras or terminated programmes never qualify.

[The daily programme-polygon verifier](./scripts/discover_programme_flock_areas.py) now checks these original sources and attempts publication only through a service-role-only RPC after all evidence validation. [Migration 056](./supabase/migrations/056_polygon_rls_private_gis_authority_predicate.sql) retains anonymous access to qualifying **public polygon records only**, without exposing the private government camera-source registry. The [public monitoring code](./scripts/monitor_public_health.py) independently checks both provenance channels, geometry, dataset totals and original-area verification freshness. A rollback-only live database test confirmed that an otherwise qualified unlocated programme can be rendered publicly while a terminated programme is excluded.

The first production scan checked twelve accessible programme pages and found **zero** directly sourced original-government Flock polygon GIS layers. Therefore the website correctly displays **zero verified approximate polygons**; no inferred coverage was published. This is a remaining documentary evidence gap, not a software restriction requiring an existing point-camera source.


## Minnesota government ALPR audit registry

[Search original Minnesota ALPR audit reports](./mn-alpr-audits.html), with Flock-named, other-vendor and manufacturer-unspecified **titles** kept distinct. The state archive yielded **137** report entries in the first live scan, **16** mentioning Flock explicitly in the title (October 26, 2026). Those are state index links, not 137 independently reviewed reports or current device/agency-compliance claims. [Source methodology and scope](./docs/minnesota-official-alpr-audit-registry.md).
