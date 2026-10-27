# Katoptron Automated Accountability Engine — Phase 2 original evidence conversion

**First verified-source increment:** October 26, 2026 (US Pacific). **Status:** first curated external independent-auditor original source, automatic source checks and reduced acquisition false positives; nationwide original contract/policy acquisition is NOT complete.

## Audited starting inventory (production, observed October 26)
- 74 original-government document hyperlink leads; 47 labeled meeting records, 14 policies plus one independently content-reviewed policy, 7 audits, three contract-labeled leads and two sharing exports.
- 10 original PDF links had undergone **metadata-only** machine triage (nine text-readable with keyword flags, one scan-only with no extractable text). This is not content review.
- Existing independently verified original-document content receipt: Alexandria Police Department Directive 10.40, a *general LPR policy*, explicitly not manufacturer-specific Flock proof.
- Verified executed contract records in the separate signed-agreement publication view: **zero**. The existence of a government hyperlink named “Flock Contract” does not demonstrate a signature or actual expenditure.

## First additional page-reviewed original audit: Shakopee, Minnesota
**Original public document:** [Independent ALPR Audit Report, June 15, 2026](https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf) (Minnesota Legislative Reference Library; auditor Lynn Lembcke Consulting; five pages).

The source was visually reviewed page-by-page. Its audited period was March 1, 2024–April 15, 2026, with an April 23 audit. The auditor describes six permanent Flock ALPR locations during that period (p. 1), Flock 30-day retention contrasted with Axon 60-day retention (p. 2), audit trails and role-related restrictions (p. 4), and concludes no discrepancies noted in the examined statutory categories (pp. 2–5). These are **the third-party auditor's time-bounded findings**, not Katoptron's independent verification of system controls, present day camera count, current agency permissions or current legal compliance. Shakopee's newer public agency page describes seven ALPR cameras; those descriptions differ in *counting units and date* and MUST NOT be presented as a proven contradiction.

**Publication:** The [curated source manifest](../data/verified-independent-audits.json) identifies exactly `shakopee|MN`, report publisher, date, document pages, individually page-linked statements and auditor scope. The [Agency Accountability Audit](../agency-audit.html?place=shakopee%7CMN) loads it without a secret, and the evidence inventory renders page links to the original state-government archive. A city name alone cannot make this source apply to another agency. No auto-publication of new contracts, device points or sharing edges occurs.

**Freshness:** [Source check](../scripts/verify_independent_audit_source.py) permits only an exact state-government archival PDF host/path, refuses redirects, enforces bounded pages/content and requires original page-identifying text. [Scheduled GitHub Action](../.github/workflows/verify_original_independent_audits.yml) fails visibly if the source is unreachable or a reviewed claim is no longer supported by retrieved pages. That failure means *unavailable or potentially changed*, never proof a policy was revoked or an auditor withdrew a finding. Historic review date remains visible. Unit and browser tests independently exercise source boundaries, matching locality and page citations.

## Acquisition precision fix

The original link hunter captured generic website navigation including “Privacy Policy,” “City Auditor,” “Lanterman Auditorium Reservation,” and “Purchasing & Contract Administration” as purported Flock/ALPR policies, audits or contracts. The [acquisition script](../scripts/acquire_original_government_documents.py) now requires a Flock, ALPR or license-plate-reader signal in the **specific link** for those sensitive document classes, not merely on the surrounding program webpage. Original ALPR audit PDFs, contract PDFs, named sharing exports and policy PDFs still qualify. No old private lead is automatically deleted, no already-reviewed fact is demoted, and newly found government links remain candidates until individually reviewed.

## Next proof-of-value priorities

1. Obtain the original Shakopee executed Flock agreement from the official portal or city clerk and visually verify signature/date/term. The city page advertises “Flock Safety Contract” but its hosted PDF currently redirects or is unavailable to some independent clients. The document must **not** be published as an executed agreement merely from its filename.
2. Resolve Portage's original scanned “FLOCK CONTRACT.pdf” through **manual visual review of the original document**, not text-extraction or OCR hallucinations, and separately review annual spending source documents.
3. Connect future independently reviewed source receipts to a normalized, source-dated, read-only evidence feed as each original fact is established. Automatically flag original-source changes but require actual evidence before concluding policy changes or legal noncompliance.
4. Measure conversion of link candidates to verified documents and the time to answer a concrete agency question. Hundreds of unreviewed leads or a larger database row count are not a value metric.

No new private data collection, schema/RLS loosening, paid provider, broad platform expansion or automatically filed public-records request is introduced by this increment.
