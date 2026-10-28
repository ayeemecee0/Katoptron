# M11 · Washington original policy acquisition expansion

Original source acquisition run: https://github.com/ayeemecee0/Katoptron/actions/runs/40630114755

Previous verified state Attorney General registration baseline: 97 self-certification entries, 11 separately individually page-reviewed exact original agency policies, 86 without an individually page-reviewed original.

The 86 remaining state-linked policy URLs were checked directly with bounded HTTP requests. Results:

- **60 public original PDFs retrieved**, each with original SHA-256 and total page count.
- **26 held**, due to missing/invalid original source type, server restrictions or network/access problems. Every held source remains independently unresolved.
- Exactly **three of the 60** PDFs contained the literal “Flock” keyword in the extracted first three pages. These are *keyword triage leads only*, not verified equipment, vendor identity, adopted policy or document-effective dates.
- **Zero** new verified operational Flock installations, individual camera geographic coordinates, actual sharing relationships or legal policy adoptions were inferred from receipt acquisition.

Source files:
- `scripts/acquire_remaining_wa_ag_policy_originals.py`, bounded allowlisted source acquisition, no redirects and source hash/page count capture.
- `scripts/test_acquire_remaining_wa_ag_policy_originals.py` tests safe URLs, prior exact original deduplication, unavailability and unknown content.
- `data/wa-ago-remaining-original-acquisition-2026-10-27.json` stores 86 individual acquisition receipts with original links, hashes, page counts, held statuses and explicit no-content-review classification.
- `.github/workflows/acquire_remaining_wa_ag_policy_originals.yml` schedules weekly original-source checks, read-only, retaining artifacts for 21 days.
- `agency-evidence-conversion.html` now displays 60 acquired PDF receipts/26 held sources as a separate, unreviewed original acquisition tier within WA's 97 registration items and shows each individual agency's source hash if retrievable.
- Dedicated data integrity, browser and general accountability regressions prevent falsely upgrading receipt retrieval to live Flock operation or legal policy status.

**Remaining substantive review:** Individually examine the retrieved originals' agency policy text and original pages before qualifying any specific claim. The 26 acquisition holds require canonical source recovery or alternate official publisher original. The 11 historical page reviews remain preserved and separate.
