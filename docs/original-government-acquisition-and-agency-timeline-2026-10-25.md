# Original government acquisition + Agency Accountability Timeline
Date: October 25, 2026 (America/Los_Angeles). GitHub Actions runs and Supabase UTC snapshots may use October 26.

## Scope completed in this implementation

### P0: Government source acquisition
- Added migration `128_original_government_document_acquisition.sql` with private RLS-protected original government document leads, private candidate-name review, private scan logs and public aggregate-only metrics.
- `scripts/acquire_original_government_documents.py` reads vetted original government ALPR/Flock program pages, dynamically selected from **verified** source-backed programme records, with capped daily nationwide rotation (up to 22 original pages), content length/time limits, public-IP DNS tests, HTTPS/.gov original-host restrictions, strict within-government www redirects and deduplication.
- Classifies original linked resources into **contracts, policies, audits, meeting records, and sharing documents**. A classified document LINK is never promoted into an executed contract, policy effective date, governing-body vote, or valid sharing grant without actual content evidence.
- Candidate named recipients are extracted ONLY from size-limited well-structured CSVs and stored privately; sensitive search-log/plate/driver headers fail closed. Named-recipient extraction results remain `review_required`, never directly appended to public sharing graphs.
- Scheduled `.github/workflows/acquire_original_government_documents.yml` runs source safety/unit tests and records source reachability and the actual lead counts. Original source errors, 403, unrelated redirects and missing sections are held rather than interpreted as absent cameras or revoked permissions.
- `original-acquisition.html` displays aggregate-only daily conversion counts with source warnings, distinguishing **document leads** from **document content independently reviewed**.
- Latest live scan: **22 seeded public government pages**, **19 successful fetches**, **74 unique original document leads**, **0 independently content-verified document links**, **0 private CSV recipient candidates extracted**, **3 source failures**. No imaginary council votes, camera coordinates, signed agreements, or outgoing sharing were automatically created.

### Original government named sharing list expansion
- Migration `130_portage_original_government_access_list.sql` adds **7 verbatim named relationships** from the Portage (IN) city police Flock original page `https://portagein.gov/547/Flock-Information-Center`.
- They are explicitly PARTIAL outward publisher-named observations. Federal status is publisher wording, not Katoptron classification. All 7 currently have unresolved canonical recipient identities. Neither permission uptime nor actual ALPR searches nor recipient reciprocity was inferred.
- Total original publisher-named directional observations now **202 across 7 original publisher URLs**, with **184 exact recipient-ID matches** across the whole original layer. This is independent original publisher provenance but not proof of currently active permissions. The much larger source-attributed secondary sharing network remains a different tier.

### P0: Source-dated agency accountability chronology
- `agency-timeline.js` and `agency-timeline.html` join dated government evidence, original Flock vendor snapshot dates, agency-reported program-status observations, original government/Flock sharing-list observations, independently reviewed signed contract milestones (only when source exists) and actual comparable secondary retention snapshot differences (only with two non-null dated values).
- Timeline separates **undated evidence** explicitly; source observation dates are not installation/start dates, signed contract end dates are not renewals, secondary retention differences are not independently authenticated current policy changes, and the city-name grouping is not a device-owner attestation.
- Migration `129_original_government_civic_milestones.sql` adds exactly **four** personally source-reviewed original-government statements (3 dated, 1 deliberately undated): Palo Alto City Council 7–0 ALPR vote April 3, 2023; city initially published partially redacted Flock logs April 21, 2026; Mill Valley's city-reported Flock suspension effective September 9, 2026; and Palo Alto's approximately $165,900 3-year vendor **estimate**, with no invented signed date, actual payment or contract execution.
- Original pages:
  - https://www.paloalto.gov/Departments/Police/Public-Information-Portal/Automated-License-Plate-Recognition-ALPR
  - https://millvalleypolice.gov/m/newsflash/home/detail/1639
- `agency-intelligence.js` joins those original civic milestones to public Agency X-Ray dossiers; `agency-xray.html` links to the new timeline and labels estimated expenses as estimates.
- `index.html` exposes original source coverage. Timeline is linked from every Agency X-Ray municipality profile.

## Actual tests and privacy
- `scripts/test_original_government_documents.py`: source authority, .gov HTTPS redirect guards, approved-program rotation, hostile link filtering, safe CSV extraction, error isolation and no automatic evidentiary upgrades.
- `scripts/test_agency_timeline.cjs`: date basis, duplication avoidance, source type segregation, undated records, absence of unjustified renewal, two-snapshot retention change.
- `scripts/test_original_government_acquisition_security.sql`: all candidate names, original document leads and scan logs inaccessible to anon/authenticated; aggregate-only public stats available read-only.
- `scripts/test_original_government_civic_timeline.sql`, `scripts/test_portage_original_government_access.sql`: prove original source civic event dates, estimate vs executed spending and verbatim Portage publisher recipient counts.
- `scripts/smoke_agency_timeline_and_acquisition.cjs` and expanded `scripts/smoke_agency_intelligence.cjs`: actual live-source Chromium acceptance for Palo Alto, Mill Valley, Folsom, Portage original-government link evidence and source coverage dashboard. The existing no-ocean-marker and route evidence regressions remain part of the same browser suite.
- Migration 128-130 applied successfully to Supabase; full release validation, latest Chrome acceptance and GitHub Pages deployment passed on commit `604467a82...` before this note.
- Supabase live checks confirm **0 anonymous reads on unreviewed documents**, **0 authenticated reads of private raw CSV candidates**, read-only public aggregate counts and civic chronology, and **0 unindexed foreign keys** reported by advisor.

## What is not 100% and why
- The source-acquisition mechanism is in production, but **74 hyperlink leads still require document-content verification**. Extracting a CSV name does not prove an outward grant direction or present access, and the most promising Portage CSV redirects inconsistently, so this run produced **zero CSV identity candidates**.
- Dated source documents are sparse nationally; only true source dates can appear as actual event dates. More verified government records, signed contract documents and policy history are needed for a complete municipal chronology.
- Original-publisher sharing evidence is now **202** of ~490,214 licensed secondary directional claims, not national current-permission verification. Source 403s are not evidence of revoked access.
- Email delivery remains independently gated on real SMTP sender credentials and an authorized confirmed subscriber.
- Use review and original-source verification instead of rapidly inventing dates, reciprocal sharing, hardware position, or legal allegations.

## Current engineering priorities
1. Convert the high-value 74 government document leads through document-level original-source verification, especially signed contracts, sharing agreements, Flock ALPR policies and date-specific council actions.
2. Extend original authority and document parsing adapters to additional verified .gov programs, maintaining source-specific confidence and source withdrawal monitoring.
3. Expand signed-cost and scheduled renewal timeline milestones only where source-backed signed agreements and dates are published. Distinguish actual spent, estimated cost and signed contract value.
4. Continue primary sharing source acquisition; never relabel large secondary graph as independently current without original dated evidence.
