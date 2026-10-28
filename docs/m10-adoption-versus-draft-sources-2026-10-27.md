# M10 – Government policy adoption evidence and source rechecking

Review date: **October 27, 2026**.

## New findings, with two explicitly distinct evidence tiers

1. **Apache Junction, Arizona — city ordinance adoption.** On the Apache Junction City Clerk [public notices register](https://www.apachejunctionaz.gov/999/Public-Notices), the table of ordinances *adopted by Council* identifies **Ordinance No. 1579** (Automated License Plate Readers) and records **October 6, 2026**. The [city police public safety technology page](https://www.apachejunctionaz.gov/1241/Public-Safety-Technology) independently says the Council unanimously approved the ordinance on that date and broadly describes access, retention, training, auditing and misuse penalties. The register's *becomes effective on* field is empty. This is an original municipal HTML adoption record, **not an individually SHA-verified, page-reviewed enacted ordinance PDF**. Legal effective date, technical implementation and actual compliance were not verified. Original PDF linked from city clerk source remains for future individual review.

2. **Green Bay, Wisconsin — revision published as draft, no verified adoption.** On the [official GBPD Policy Manual listing](https://www.greenbaywi.gov/1223/Policy-Manual) reviewed October 27, the published **May 2026 Policy 424** and **DRAFTED REVISION ... September 2026** remain separate links. Existing page-reviewed originals show May's 30-day written limit versus September's proposed seven days. The **draft status is established**, but the completeness of the department's internal adoption records is **not**. No policy enactment, seven-day configuration or lack of internal approval may be inferred from the listing alone.

A city clerk's formally adopted municipal ordinance and a police department's proposed PDF revision are **different legal acts and evidence types**. Neither confirms live camera operations.

## Implementation

- `data/verified-policy-adoption-status-2026-10-27.json`: dated original government HTML-receipt ledger, explicit source basis, effective-date null, status, summary, corroboration and evidence limits.
- `policy-adoption-evidence.js`: exact-URL, source-identity, legal-status, event-date and uncertainty validation; immutable allowlist and fail-closed result.
- `policy-history.html`: separate adoption-vs-draft panel with both original primary government links, not counted toward the existing 18 agency / 25 PDF original-document baseline.
- `scripts/monitor_policy_adoption_originals.py`: bounded read-only check of exact official government publisher listing URLs. A changed link or an inaccessible source produces a `needs_review` receipt and never auto-publishes a verified policy or sends an email.
- `.github/workflows/monitor_policy_adoption_originals.yml`: daily original publisher freshness checks and 14-day downloadable review receipts. No secrets, database write or source auto-promotion.
- Tests: `scripts/test_policy_adoption_evidence.cjs`, `scripts/test_monitor_policy_adoption_originals.py`, mobile `scripts/smoke_policy_history.cjs` and the accountability acceptance workflow.

## Next evidence action

Acquire and separately review Apache Junction's actual ordinance and city-code text, including whether the City Clerk later posts a legal-effective date. Track Green Bay's post-public-comment policy approvals and any new official PDF version. Only a reviewed original approving action (or authenticated current effective policy version) can upgrade the status. Extend the bounded recheck pattern to other government publishers *one at a time* without claiming statewide completeness.

**Email:** This feature only adds a read-only original-source recheck. Existing email infrastructure still lacks SMTP configuration; no email delivery is claimed.
