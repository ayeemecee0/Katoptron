# M7 Evidence Analytics — Engineering Sign-off
**Date:** October 26, 2026 (America/Los_Angeles)

**Decision:** 100% of the bounded M7 analytics engineering acceptance scope. This certifies accurate source-tier aggregation, transparent public evidence caveats, privacy controls, complete-data fetching and reconciliation, accessible public display, export integrity, automated regression and live-browser testing. It does **NOT** certify complete nationwide Flock camera coverage, current camera operation, installation trends or third-party historical completeness.

## Verified root cause and correction

The original `flock_analytics_overview` counted every public `flock_public_tiered_camera_points` row as `separately_corroborated_points`. Twelve source-attributed **unconfirmed** Shelbyville municipal observations were therefore presented as corroborated. Meanwhile 316 exact original-government GIS positions were shown without prominently separating 293 positive Flock-labeled sources from 23 generic LPR records where manufacturer is unknown.

Production [migration 141](../supabase/migrations/141_m7_source_tier_analytics_reconciliation.sql) fixes the national and state source-tier definitions:

- `source_flock_labeled_points`: 293 approved original government GIS positions whose **original source** explicitly identifies Flock; not proof of device-level uptime or active ALPR capture.
- `generic_lpr_points`: 23 exact government GIS positions with generic LPR evidence; not eligible for the Flock-only simulator.
- `unknown_manufacturer_points`: 0 now; a separate bucket for future exact government positions lacking either original manufacturer label.
- `exact_government_points`: 316 total across all three original-source labels. The three categories must sum exactly to the total for every state and nationally.
- `separately_corroborated_points`: **0**, counting only published `independently_corroborated` evidence cases. Source-attributed unconfirmed reports no longer qualify.
- `source_attributed_unconfirmed_points`: **12**, explicitly separate, provisional observations not evidence of confirmed active devices.
- `additional_government_verified_points`: **0** separately qualified published cases outside the original camera GIS inventory, without blending into other tiers.
- 24 published dated government program records, 34 public accountability records, and 17 states with some original-source GIS, government program/vendor or public accountability evidence. No evidence for a state is not proof cameras are absent.

## Complete data and privacy

- The dashboard uses three `security_invoker=true` views only and reads no private community submissions, contributor accounts, photos, plate numbers, user routes or private review.
- The new [analytics-data.js](../analytics-data.js) requests exact PostgREST `Content-Range` totals; uses stable ordering and at most 25 pages of 200 records per source. A missing count, silently truncated row page, duplicate row identity, count changes during retrieval, or budget exhaustion is a fail-closed result, **not zero**.
- Independent source and state reconciliation confirms all source-tier subtotals. If records do not reconcile, the dashboard withholds summary rendering and disables CSV export rather than distributing misleading statistics.
- The source-labeled Flock, generic LPR and manufacturer-unknown columns appear by state; the national summary also separately shows 0 corroborated vs 12 provisional, without implying independent proof.
- All timeline bars describe dates of *published documentary records*, not camera installation, removal, government expenditure, searches, plate reads, vehicle movements or real surveillance volume. Undated records remain excluded, with explicit caveat.
- CSV export retains formula-injection escaping and now exports separate manufacturer-source classifications, never private data.

## Passing acceptance and deployment

- [PR #20 — complete M7 reconciliation and frontend](https://github.com/ayeemecee0/Katoptron/pull/20); merged to main as `5a35ff882001645457e8c6336952a0251b20e213`.
- Supabase migration 141 rehearsed in a rolled-back production transaction with [M7 SQL acceptance](../scripts/test_analytics_m7.sql), then applied to production; the same acceptance reran successfully.
- [Full validation run 40384169393](https://github.com/ayeemecee0/Katoptron/actions/runs/40384169393): **PASS**, including disposable PostgreSQL migration, original source/provisional reconciliation and new Node exact-count pagination, duplicate and source-drift negative tests.
- [Full Chromium browser run 40384169397](https://github.com/ayeemecee0/Katoptron/actions/runs/40384169397): **PASS**, explicitly logged `ANALYTICS PASS: exact Flock/generic manufacturer-source reconciliation, dated records, CSV and fail-closed incomplete source`. The test injected a malformed apparently successful source response, saw "analytics unavailable or incomplete", and confirmed export disabled.
- [Automated WCAG 2.2 scan](https://github.com/ayeemecee0/Katoptron/actions/runs/40384169147): PASS.
- [Independent automated WCAG release acceptance](https://github.com/ayeemecee0/Katoptron/actions/runs/40384169115): PASS. Neither claims a human assistive technology review.
- [Live GitHub Pages deployment](https://github.com/ayeemecee0/Katoptron/actions/runs/40384162533): PASS.
- Public interface: [Katoptron evidence analytics](https://ayeemecee0.github.io/Katoptron/analytics.html).

## Sign-off boundary and next priority

The accepted bounded M7 engineering capability is **100%**. Source-specific national inventory completeness is unknown; no denominator supports a 100% national camera census, historical source coverage or true operating-ALPR prevalence. The analytics must never infer these from counts of records in Katoptron.

M8 accessibility and M9 production readiness retain separate independent human-accessibility, real email confirmation, usability, security, recoverability and deployment gates. Their earlier estimated percentages were not reaudited by this work.
