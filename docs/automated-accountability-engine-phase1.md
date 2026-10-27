# Katoptron Automated Accountability Engine — Phase 1

**Implemented:** October 26, 2026. **Deployment tier:** source-cited public research beta; **not** independent agency compliance certification.

## Product

- [Accountability Audit](../agency-audit.html) lets a visitor choose an indexed locality (or open an X-Ray linked permalink), loads already published Katoptron source records and the separate reviewed signed-agreement view, and constructs an on-demand reproducible evidence assessment.
- Pure deterministic [audit engine](../agency-audit-engine.js) evaluates **published-only** government events, verified government GIS coordinates, original Flock portal snapshots, original publisher-named sharing observations, and *only* independently reviewed signed contracts. No hidden editorial/private queue or personal routes are queried.
- Date-limited checks identify changed source-reported retention between snapshots from the **same original publisher**, different first-party readings on the **same publisher and same date**, or first-party/secondary retention differences **only with an exact original Flock portal identity match and matching observation date**. These are labelled *source differences*, never misconduct or actual policy effective-date findings.
- Explicit evidence gaps identify what Katoptron has not obtained: original government decisions, signed contracts, first-party Flock transparency snapshots, original sharing lists, authenticated exact GIS inventory, and comparable first-party history. Missing index entries are **unknown**, never evidence of nonexistence or camera-free zones. Incomplete original sharing excerpts are called out.
- When the vetted contract read endpoint is unavailable, the audit says **lookup unavailable** rather than claiming no executed contract. Source-documented contract end dates lead to review tasks, not assertions of renewal/termination.
- Each supported positive fact is linked to original HTTPS public evidence. Public gap questions are marked as questions, *not* facts. The interface offers a print/save-as-PDF report and a **locally generated, unsent** public-records request draft requiring user review. No sending, signing, account signup, data modification, AI hallucination, or backend storage.
- The same source data as existing X-Ray remains separately tiered; a shared locality label is **not** an assertion that two government agencies are the same Flock operator. Secondary license terms and attribution remain in the source pages and methodology.

## Why this is an initial release, not a completed independent audit

The platform's initial read-only inventory at development time contained **316** exact government-source-mapped positions across eight jurisdiction labels, **37** public accountability events across thirty locality labels, **24** documented program disclosures, **14** Flock vendor snapshots, and **zero** verified executed contracts in the separate public signed-contract view. The absence of signed contracts is a research coverage gap, not a finding that the agencies lack agreements. These counts are a point-in-time observation, not a national census.

The report cannot know unrecorded government documents, real equipment uptime, law-enforcement query logs, current reciprocal sharing, contract compliance, actual retention configuration, or undisclosed policy exceptions. Its *research priority* P1/P2 is not a surveillance risk rating and does not rank legality or police conduct.

## How to validate

- `node --check agency-audit-engine.js`
- `node scripts/test_agency_audit_engine.cjs`: fails closed for unavailable contracts, unrelated secondary identities, different collection dates and unverified GIS; detects same-date source differences and dated first-party retention changes; rejects unsafe source URLs and verifies an unsent records-request draft.
- `node scripts/smoke_agency_audit.cjs` on a Playwright setup pointed at a running local web server or deployed GitHub Pages: confirms live source loading, a real Folsom locality report, HTTPS citations, safe draft, reloadable permalink and narrow mobile layout.
- `.github/workflows/validate.yml` and `.github/workflows/browser_smoke.yml` integrate these tests with release checks.

## Next releases

1. **Acquire and verify original evidence:** agency-owned signed agreements, public audit/retention policies and controlled public sharing list exports, using existing source classes and review gates. This is the actual bottleneck; reports cannot infer missing evidence from prose.
2. **Versioned original-source discrepancy workbench:** preserve snapshots with source integrity receipts and reviewer resolution state, distinguish corrected publisher statements from historical settings, and list unresolved tasks without automated allegations.
3. **Owner-authorized oversight workspace:** provide auditable workflows for redacted aggregate audit exports only with explicit agency authorization and privacy review. Do not collect raw license plates, target individual drivers, request private search logs, or expose sensitive access records.
4. **Validate customer value:** measure researcher time saved and rate of evidence questions actually resolved in blinded evaluations, not unverified 'compliance scores', publicity or synthetic accuracy metrics.

Maintain approximately 10% acquisition and existing map/discovery pipeline maintenance, preserve public evidence privacy/RLS and do not automatically publish uncertain source candidates.
