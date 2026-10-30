# Professional research intelligence · Five capabilities

## Operational boundaries

This intelligence center reuses Katoptron's existing verified source publishing pipeline. The daily [original-government version watcher](../.github/workflows/watch_original_government_versions.yml) fingerprints approved government HTML pages; first observations establish baselines and changed texts are privately queued for editorial review. That workflow **never publishes its unreviewed findings as news**.

The public [Watch events](../government-watch.html) are separately sourced government disclosures; `professional-intelligence.js` reads only records with `evidence_tier=original_government` and allowlisted event kinds. The 51-entry historical government docket is validated by the original-docket gate. **No new detector may treat a historic record as a fresh event.**

### 1. Investigative Lead Engine
Public government-source records produce dated research leads with original URLs, why they may merit reporting, unresolved questions and verification steps. Newly published reviewed events are read from the existing Watch table, not directly from the confidential crawler review queue. The scanner covers only its approved publisher sources, not every contract or all jurisdictions nationwide. A source disappearing results in an error/hold, not an absence finding.

### 2. Cross-agency discrepancy / gap finder
Only validated, SHA256-bound original-page review transitions may carry the **confirmed_documentary_difference** label; this verifies reviewed document-wording differences, not policy effectiveness or wrongdoing. Different government statements within one exact agency may be **apparent_inconsistency_needs_review**. Unanswered docket questions are **missing_evidence**, not proof that no contract exists. Cross-jurisdiction records are context and never automatically contradictions. Page references are displayed only where reviewed anchors provide them; otherwise *exact page not independently verified*.

### 3. Evidence acquisition
Uses the selected original-source context to identify likely **official custodian roles**, link already indexed primary documents and prepare an editable narrowly scoped public records request. It never opens a FOIA portal, transmits a request, infers jurisdiction-specific statutory deadlines, or searches private ALPR reads. The researcher may copy the draft and track subsequent requests, replies and dates inside the existing RLS-protected research workspace.

### 4. Personal in-app research feed
`research_intelligence_follows` is a separate opt-in table. Owner-only RLS protects follows, topics and optional question; DB-generated `opted_in_at` cannot be updated via authenticated privileges. A Watch event counts as *new* only when observed after the follow began, while other published events remain in the clearly labeled previously published section. Following here **never enables Government Watch email**, or any other outbound message. New event availability depends on independent editorial Watch publication.

### 5. Investigation package
One click exports a standalone, printable HTML brief with source timeline, original government URL appendix, qualified discrepancy types, unknowns, verification tasks, official roles and an **unsent** request draft. Output text and href attributes are HTML-escaped and links only accept safe HTTPS. No private case notes, credentials, records-response attachments, individual plate observations or surveillance search queries are included.

## Validation / next commercial test
- `node scripts/test_professional_intelligence.cjs`: source and label qualifications, historical baseline, topic filters, page-pinned comparison, request restrictions, escaped HTML
- `node scripts/smoke_professional_intelligence.cjs`: locally hosted preview → lead → comparison → editable draft → downloaded package → simulated confirmed-user follow and deletion
- `scripts/test_research_tenant_isolation.sql`: actual isolated Postgres RLS checks including unauthenticated isolation, other account privacy, owner withdrawal, immutable follow timestamp
- Existing research-workspace and original-government tests remain release gates.

User research must still measure novelty of discoveries, fact-checking time, usefulness and willingness to pay. Passing browser tests does not establish a useful original investigation or a delivered email.
