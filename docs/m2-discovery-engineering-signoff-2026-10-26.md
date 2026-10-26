# Milestone 2 — Discovery engineering sign-off
**Date:** October 26, 2026, America/Los_Angeles
**Decision:** 100% of the bounded M2 **engineering acceptance scope** implemented and validated. **Not** 100% of nationwide original-government evidence, camera locations, agreements, or agency sharing permissions.

## Verified end-to-end capabilities

1. Nationwide original-source discovery: existing scheduled government/Legistar/Esri/GIS discovery, provider safety checks, deduplication, source classification, automatic government-directory source rotation and explicit original-publisher gates. New original camera coordinates require source-specific corroboration (M3).
2. Original document-link acquisition: 22 reviewed/rotated government page seeds, 19 successful fetches in the latest logged scan, 74 unique original .gov document leads. HTTPS, publicly resolvable DNS, same-host redirects and bounded downloads enforced. A link is a research lead, not its content.
3. Source appearance lifecycle: migration 135 and `record_original_document_link_scan`. An observed link updates original-source last-seen provenance after **successful** page reads. Two *successful* scans missing a link are required to report the link not currently shown; server errors/403s do not revoke evidence. Past review status is preserved. Restore of a source link clears the absence streak.
4. PDF byte integrity and private machine triage: previously downloaded 10 government-linked PDFs, 9 with extractable text and 1 scanned/image-only. New scheduled `triage_original_government_pdf_content.py` uses a hash-pinned parser, verifies already recorded exact document bytes and limits size/pages. Records ONLY private boolean classification indicators, page counts and document SHA-256; no raw excerpt, plate data, location, signed amount, inferred recipient, or validated legal claim. Machine triage never changes `document_content_verified`.
5. Independent content-review gate: migration 136 introduces owner-only private receipts keyed by original PDF content checksum and a service-role promotion guard. One first-party source, Alexandria Police Department Directive 10.40, effective October 28, 2025, has a manually checked, narrow source scope. It is **general LPR policy**, not proof of a Flock-specific manufacturer, current sharing permissions or installed cameras. Original: https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf. Review based on original PDF pages 1, 5 and 6.
6. Conversion dashboard: `original-acquisition.html` exposes aggregate-only total leads, fetched PDFs, automated triage and *independently* verified document count, plus links absent after two successful scans. Unreviewed source names, raw documents and private evidence remain inaccessible to anonymous and authenticated users.
7. Closed new database index advisories: migration 137 covers the two original-document foreign keys identified in Supabase performance advisor. No M2 missing-foreign-key-index notices remain after migration.

## Tests and deployment evidence
- M2 PRs: [#13](https://github.com/ayeemecee0/Katoptron/pull/13), [#14](https://github.com/ayeemecee0/Katoptron/pull/14), [#15](https://github.com/ayeemecee0/Katoptron/pull/15).
- Migrations 135–137 applied in production after transactionally rolled-back rehearsals.
- `scripts/test_m2_source_discovery_acceptance.sql`: government source disappearance/reappearance, unchanged review state, RLS and restricted source-scan RPC.
- `scripts/test_m2_original_content_review_acceptance.sql`: original document scope/hash receipt and negative service-role self-promotion.
- `scripts/test_m2_discovery_signoff_sql.sql`: FK indexes, RLS and owner-only original review.
- `scripts/test_m2_private_pdf_content_triage.py`: parser bounds, exact digest matching, no personal content persistence and no inferred public facts.
- GitHub Actions full validation passed on committed M2 branches and source-document/PDF worker and map runs passed after PR #13 deployment.

## Production evidence baseline at acceptance
- 74 original-government document hyperlink leads, 74 private appearance-history entries.
- 10 historically observed PDF byte versions, 10 machine-triaged, 9 with text, 1 not machine-readable.
- 1 independently reviewed original **general LPR policy** source. **73** other document leads are still not independently content verified.
- 316 government-GIS-sourced camera point observations across 8 approved sources (293 positively Flock source-labeled, 23 generic LPR). Manufacturer/device operation is not independently established for every mapped point.
- 6 GIS candidate sources remain awaiting first-party local agency endorsement and must NOT be auto-approved.

## Explicit boundaries / next milestones
- **M2 engineering:** 100% (repeatable, tested discovery and provenance-management mechanisms).
- **Nationwide data coverage / source completeness:** unknown and demonstrably incomplete. It cannot honestly be assigned 100% or a fixed denominator.
- **M3:** actual source-specific hardware/camera verification, geographic authority and GIS manufacturer qualifications continue independently.
- **M6:** publication of corroborated, independently interpreted contract amounts, signed dates, retention policies, sharing direction and individual government votes remains source-specific. A keyword match is not evidence.
- **M9:** operational launch, sender-controlled opt-in email credentials, security advisors beyond the M2 private tables, disaster recovery and human accessibility acceptance remain separate gates.

**Acceptance rule:** do not reopen M2 engineering merely because new original-government sources enter its queue. Reopen only for a demonstrated source-acquisition failure, provenance false upgrade, broken liveness/retry cycle, leaked private content, or failed release CI.
