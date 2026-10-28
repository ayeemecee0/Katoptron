# M10 · Separately consented original-policy Watch email events

## Existing recipient safety

The Watch sender enumerates only authenticated subscribers with a confirmed email via the protected `flock_watch_delivery_candidates` RPC, and uses encrypted SMTP when sender secrets are configured. Existing government/vendor/sharing/renewal categories remain unchanged.

This release adds a **separate policy-source category, default OFF**, to the same owner-RLS-protected subscription. The migration stamps `policy_opted_in_at` using database time when the category is enabled or email is re-enabled. The sender reads that private per-subscription timestamp with a service-role connection. Policy-source events first observed before that timestamp are never replayed to a person who opted into policy notices later. The stamp cannot be backdated through the browser API.

## What qualifies

Five individually original-page-reviewed existing source documents have pinned IDs and original SHA-256, publisher URLs, permitted review pages, typed source dates and document lifecycle:
- Green Bay May 2026 published policy and separately held September 2026 **UNADOPTED DRAFT**
- Providence General Order 350.05, effective September 4, 2026
- Brookings Policy 13D1, dated September 22, 2026
- Kittitas original four-page **UNADOPTED DRAFT**

These are **newly reviewed source-document** event types, not `policy_changed`, not an enacted seven-day reduction, not actual compliance or installed Flock camera verification. Source drift or changed lifecycle fails closed. New eligible docs require an explicit addition to the vetted allowlist, rather than automatic manufacturer or policy inference.

`policy_original_reviewed` and `policy_draft_reviewed` live in the existing public event table as read-only events; only the owner service-role source synchronizer may create them. A source-only policy locality can be watched even if its city has no camera map points or vendor portal. Existing email alerts do not require policy opt-in.

## Operational boundaries

- Schema file: `supabase/migrations/144_explicit_policy_original_watch_opt_in.sql`. The original project uses numbered migration source files; remote migration metadata must be reconciled if applied through the Supabase integration.
- Email delivery still **requires working SMTP secrets**. No secret keys or subscriber addresses are exposed to static HTML, logs or GitHub review artifacts.
- Public original policy source dates can predate discovery; `observed_at` is the time the new verified source was first indexed, not policy enactment. Existing historical sources already in the index are not replayed to later opt-ins.
- The sender has idempotent per-recipient event receipts, preserves unsubscribes, and does not treat a new review as an operational policy change.
- No exact Flock camera coordinates, vehicle plate records, private travel routes, read logs or agency compliance ratings are produced.

## Tests

Python unit tests cover source-hash/role drift, immutable source classification, prior-event exclusion, separately consented policy events and duplicate delivery. Browser acceptance checks explicit policy opt-in off by default, confirmed-account signup, category save and unsubscribe. Full accountability/source CI includes these tests. Live migration grants and RLS should be checked after applying migration. SMTP still needs a controlled end-to-end live send before claiming emails have been delivered.
