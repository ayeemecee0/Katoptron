# Milestone 5 — Community Reporting Engineering Sign-off
**Acceptance date:** October 26, 2026 (America/Los_Angeles).
**Decision:** **100% of bounded M5 engineering scope accepted.** This certifies implemented and tested privacy-bound contributor intake, moderation, photo storage, withdrawal, permanent erasure and safe publishing controls. It does **not** certify production email delivery, human beta usability, an independently observed physical camera, or nationwide crowdsourced coverage.

## End-to-end features

1. **Signed-in contributor:** Supabase Auth validates cached sessions with `auth.getUser()`; new account uses an email-confirmation callback to the hosted `submit.html` page. Private form accepts optional HTTPS source, observation date, description 40–1500 chars, supported US coordinates, an optional sanitized WebP image (3 MB input, 20 MP maximum, max 2,400 px output side), and a separate, unchecked public publication-consent box. No automatic official map pin.
2. **Private evidence:** report rows use owner-bound RLS; raw Screening, review history and photo objects are invisible to unauthorized users. The photograph is in a private Supabase Storage bucket under the authenticated user's ID and report UUID. Reporters may add missing source or photos while pending/needs evidence. The reviewer obtains 60-second signed photo links; live check confirmed bystander denial.
3. **Moderation:** approved reviewer access required; case reviewer must provide a substantive note. Review paths are needs_evidence, rejected or incorporated into a **private unverified** candidate; independent original evidence and explicit consent are required for eventual public promotion. Migration 139 removes the obsolete two-argument unaudited reviewer RPC.
4. **Withdrawal:** contributor can withdraw from any non-withdrawn status using an owner-only RPC. Private derived report attestations and point-case classifications are revoked. Reviewers lose new access to the withdrawn photo immediately, although an already-issued signed link can survive up to its 60-second expiry.
5. **Permanent deletion:** after withdrawal, owner deletes the actual private photo via the Storage API. The `delete_withdrawn_community_report(uuid)` RPC refuses deletion until the exact report directory has **no** remaining object, and then removes this user's private report, screening, reviewer history and deterministic report-derived evidence records. An unrelated signed-in user cannot erase another person's report. A Storage outage leaves the withdrawn private report intact and retryable.
6. **Spam protection survives erasure:** versioned migration 139 uses a private `user_id` + `submitted_at` append-only rolling-window ledger, excluding report descriptions, coordinates, URLs, photographs and submission references, so physically erasing three reports cannot reset the three-per-day limit. Database transaction advisory locking prevents concurrent over-submission.
7. **Expired rate-event privacy minimization:** migration 140 and a scheduled service-role-only GitHub Actions job purge entries older than 24 hours daily, including for accounts that never submit again. User account deletion also cascades to rate events.
8. **Live deployment and tests:** no dedicated new paid infrastructure or secret exposed in the public browser. The private disposable QA job creates three separate Auth users with admin-confirmed `@example.invalid` mailboxes; signs in with real passwords/JWTs, performs real Supabase REST/RLS and Storage binary operations, tests authorized reviewer status updates, withdrawal, owner-only photo removal and permanent report deletion, then confirms complete cleanup. The workflow runs on scoped M5 changes and weekly.

## Verified acceptance evidence
- [PR #19](https://github.com/ayeemecee0/Katoptron/pull/19), production merge `0e413391b89b342686aa017516a5bd2c73e31b44`.
- Migrations [139](../supabase/migrations/139_community_report_erasure_and_independent_rate_ledger.sql) and [140](../supabase/migrations/140_m5_daily_expired_rate_event_privacy_prune.sql), applied to production after rolled-back SQL rehearsals.
- [Full SQL/frontend validation](https://github.com/ayeemecee0/Katoptron/actions/runs/40381340882): PASS. Includes cross-account erasure denial, storage-object erasure precondition, no original-lead privilege escalation and fourth-report rejection even after removing the first report; private ledger expiry tests.
- [Live disposable Auth and Storage API acceptance](https://github.com/ayeemecee0/Katoptron/actions/runs/40381340892): PASS. Confirmed exact real private photo binary upload, authenticated own download, restore, bystander download denial, reporter's actual Storage DELETE, permanent report erasure, reviewer cutoff and **complete cleanup**. **Email delivery untested.**
- [Release browser acceptance](https://github.com/ayeemecee0/Katoptron/actions/runs/40381341089): PASS. Browser mock tested the new permanent-delete UI, genuine consent defaults, photo re-encoding, failed photo-deletion retry, reviewer mandatory explanation and attachments. Separate real Geoapify / mobile / accessibility smoke passed.
- [Private rate timestamp daily expiry](https://github.com/ayeemecee0/Katoptron/actions/runs/40381340889): PASS.
- [Pages deployment](https://github.com/ayeemecee0/Katoptron/actions/runs/40381338872): PASS.
- [Automated accessibility tests](https://github.com/ayeemecee0/Katoptron/actions/runs/40381340984) and [independent acceptance automation](https://github.com/ayeemecee0/Katoptron/actions/runs/40381341050): PASS. Not a substitute for human assistive-technology review.

## Privacy post-test production snapshot
- **0** contributor-submitted reports.
- **0** contributor review-history records.
- **0** private community evidence Storage objects.
- **0** retained anti-abuse rate events.
- **1** existing Auth user and **1** already-authorized editorial reviewer. Live QA user accounts are gone.
- **316** unchanged government-source GIS positions, of which **293** are source-labeled Flock and **23** are manufacturer-unconfirmed generic LPR. No mock report or synthetic camera was published.
- Old two-argument `set_community_review_status(uuid,text)` API absent.
- Anonymous execution of permanent erase is denied.
All counts are from a read-only production query after the live acceptance.

## Explicit launch boundaries (M8/M9 and data work)
- A **real mailbox** must still demonstrate sign-up email delivery, redirect allowlist correctness, email-confirmation link and recovery handling; admin-confirmed temporary QA identities cannot establish deliverability or user-owned verification links.
- Real people should complete opt-in usability, moderation and privacy review with legitimate reports and appropriate photo content, including privacy-policy acceptance and accessible mobile input. Do not seed fabricated real-world sightings.
- Existing Supabase password-protection advisory and other broader project security/operational issues remain M9 tasks. This engineering sign-off is not an assertion that the whole product is production-ready.
- No community submission has independently corroborated any new active Flock camera; original-government and physical-source validation are separate M3/data work.

**Conclusion:** M5 reporting lifecycle **engineering 100%**, independent community camera coverage and real-world beta acceptance **not certified**.
