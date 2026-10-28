# M10 · Original policy history and opt-in source-version watch

Date: 2026-10-27. Source baseline: 18 exact Agency X-Ray publishers / 25 original-page-verified documents at merged #66.

## Problem and product

Existing comparison showed isolated published policy pages, but did not distinguish a draft proposal from a genuine adopted amendment or let readers follow newly verified policy versions. The new `policy-history.html` is linked from Agency X-Ray, Agency Comparison and Government Watch.

It takes only existing original-government Agency X-Ray verifiers as input, keeps typed document lifecycle, dates, PDF SHA-256 and page citations, and builds a verified policy version index. Contract forms, general vendor statistics, training bulletins and unrelated oversight documents are excluded from policy history. A policy publishing date or AGO registration date is never silently treated as an adoption date.

## First page-reviewed before/after documentary comparison

- Green Bay Police Department May 4, 2026 published Policy 424, reviewed page 2: written maximum ordinary ALPR retention of 30 days; not confirmed current effectiveness or actual data deletion.
- Green Bay September 2026 revision, visibly DRAFT; source effective/adoption date **not established**. Reviewed page 4: proposal to reduce ordinary retention to seven days; **not an enacted policy change**.
- Two immutable original sources, two separate SHA-256 values and page-specific citations. No current software configuration, legal-compliance score, current sharing permissions or change in actual practice is inferred.
- Kittitas's four-page 2026 scanned policy is likewise always labeled DRAFT and never counted as adopted.

## Local source-watch behavior

An explicit user action opts in to watching an exact source-identified agency on the **current device**. On follow, the browser records the known `document-id@SHA-256` fingerprints as a baseline; prior historical originals are not replayed as new alerts. A future visit can identify *newly indexed, original-page-reviewed* documents that differ from that baseline. Unwatch and mark reviewed are available, storage unavailable is reported and never treated as success. Maximum 15 followed agencies; no email address, plate observations, routes, GPS or other personal information is sent to the application as part of this local feature.

**Scope limitation:** this is not an email, push, scheduled crawler or background notification. Existing Government Watch email subscriptions are separately authenticated and currently cover their own event categories. No new schema permission, mail category or production database migration is falsely claimed. Original-source drift that fails the upstream validators is held, not presented as a detected policy amendment.

## Verification

- `scripts/test_policy_history.cjs` runs against the real original government ledger and rejects missing page citations, a draft promoted to published, spoofed HTTP source, forged draft adoption date, wrong-page citations and initial follow replays.
- `scripts/smoke_policy_history.cjs` exercises real mobile Chromium source loading, original-page links, Green Bay proposal boundary, Kittitas draft, opt-in state persistence, explicit unwatch, and deep links.
- `audit_accountability_acceptance.yml` includes both tests as blocking release gates.

## Next action

Connect new **qualified source-publication events** to a separately consented email category, requiring a schema migration, authenticated sender behavior and replay/identity regression checks. That must not be conflated with live operational policy changes or promised before backend deployment and SMTP verification.
