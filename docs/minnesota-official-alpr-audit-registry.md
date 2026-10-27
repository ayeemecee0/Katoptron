# Minnesota original ALPR audit registry — automated public index

**Scope:** official public metadata from the [Minnesota Legislative Reference Library](https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735). This is not independently reviewed document content or a surveillance census.

## Original source coverage

The first bounded live scan on October 26, 2026 identified **137** uniquely linked report PDFs on the official state archive, including **16** titles explicitly naming Flock. Some titles name other vendors and many leave the manufacturer unspecified. These are _title categories only_, not verified manufacturers or present agency operating conditions. The separately reviewed Shakopee audit retains its independently checked page-level content receipts.

## Automatic operation

The acquisition script at [scripts/import_mn_alpr_audit_registry.py](../scripts/import_mn_alpr_audit_registry.py) reads one fixed HTTPS state index and parses its six public registry columns. The scanner rejects redirected or external URLs, mismatched report IDs, too few/too many extracted links, and inconsistent archive paths. It does **not fetch the underlying PDFs** or any license-plate data. The scheduled [GitHub Action](../.github/workflows/import_mn_alpr_audit_registry.yml) tests the parser and checks the original index before service-role-only upsert into the public metadata table. The source index SHA-256 and scan counts are privately recorded.

The RLS-protected public table offers only SELECT to anonymous and authenticated users. The service role alone can INSERT or UPDATE, never DELETE. Source URL and permitted evidence-tier values are constrained in the database. Missing a document link in a future scan is not proof an audit was withdrawn; missing rows are not deleted.

[Official Minnesota ALPR Audit Library](../mn-alpr-audits.html) offers searchable, source-linked public metadata. Each entry distinguishes official title and report receipt dates from actual auditor conclusions. HTML uses text-only rendering and only permits official state archive PDF hyperlinks.

## Verification and next work

Run the Python unit tests in scripts/test_import_mn_alpr_audit_registry.py, the real archive preflight, and the Playwright browser acceptance in scripts/smoke_mn_alpr_audit_registry.cjs. An independent auditor finding is allowed in the main accountability engine only after page and content-hash review. The next improvement is a versioned evidence-review queue that prioritizes original reports with Flock explicitly named in their title, and produces time-bounded findings only from checked original PDF pages.

No new map coordinates, signed agreements, active data-sharing permissions, current manufacturer identities, compliance scores or surveillance misconduct assertions are inferred from this registry.
