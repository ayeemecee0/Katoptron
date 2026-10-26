# Agency Intelligence build checkpoint — October 25/26, 2026

## Four requested deliverables
**Status:** source import and directional evidence explorer functioning; first-pass Agency X-Ray and source changes active. **Actual outbound email delivery held** for owner-controlled encrypted SMTP credential, confirmed subscriber testing and mailbox reception. Never call this a fully operational alert service until then.

### P0 · Licensed national disclosures
- Publisher/normalizer: EyesOnFlock aggregation, processed by [deflock-data network source](https://github.com/flockhopper3/deflock-data/tree/main/eyesonflock), CC BY-SA 4.0.
- Live production: **6,893 source agency identities**, **1,601 reporter portals**, original R2 snapshot **October 19, 2026**.
- [migration 117](../supabase/migrations/117_secondary_portal_agency_directory.sql), [agency importer](../scripts/import_licensed_agency_network.py), [weekly workflow](../.github/workflows/import_agency_network.yml), [import tests](../scripts/test_import_licensed_agency_network.py).
- Source identities carry exact provider source IDs and source tier, not invented municipality camera sites. The secondary agency directory has **no latitude or longitude columns**. Source-reported mixed camera counts do NOT create Flock camera pins or enlarge the approved 316 government-source-mapped GIS positions.
- Original first-party vendor snapshots (14) remain completely separate and more directly source-attributed than this aggregation.

### P0 · Documented sharing explorer
- The original network adjacency contains **490,214 directed source links** for the 6,893 identities (Oct 19 snapshot). A → B means A's transparency portal SOURCE-REPORTED list permits data sharing with B. Does not establish B actually made a search, reciprocal access, or current permissions.
- [Agency network JS](../agency-network.js) validates source identities, counts and edge endpoints. [Full sharing explorer](../sharing-explorer.html) presents distinct outgoing and incoming lists and original source snapshot, not agency center map pins.
- CORS on the public upstream prevented Chrome client direct fetch. A dedicated [weekly source-validation & sanitized mirror](../.github/workflows/mirror_licensed_agency_network.yml) now publishes same-origin `data/agency-intelligence/{nodes.json,adjacency.json,manifest.json}`. It retains agency IDs and directions, STRIPS all geographic coordinates, and includes CC BY-SA attribution. The mirror and full browser test passed.
- [migration 119](../supabase/migrations/119_sharing_fingerprints_and_contract_end_dates.sql) and importer record a per-source SHA of *outbound* listed recipients. New→existing and nonempty→empty changes can generate source-dated `sharing_list_changed` events, but a new source without a previous known list cannot be mislabeled a change.
- This is a secondary portal network, **NOT** 490,214 independently verified government-hosted sharing contracts. Future first-party confirmation work should preserve this tier separately and may need explicit government/vendor current-policy receipts.

### P1 · Government Watch
- [migration 118](../supabase/migrations/118_opt_in_government_watch_alerts.sql) and [120](../supabase/migrations/120_watch_delivery_post_opt_in_boundaries.sql) add **owner-only RLS subscriptions**, default email opt-out, preferences for decisions/vendor disclosures/sharing/contract events; **private service-only** delivery receipt table and service-role-only recipient RPC joining *confirmed* Supabase Auth mailboxes. No anonymous account access or mailer recipient enumeration.
- [source event sync](../scripts/sync_agency_watch_events.py) regularly extracts independently published government decisions, signed Flock documents, 14 directly sourced Flock vendor disclosures, two-snapshot retention changes and approaching ORIGINAL documented signed contract end dates. Expiring does NOT imply renewal; a signed agreement does NOT imply a renewal unless original source says so.
- Live baseline **21 source evidence events**, 7 government, 14 first-party vendor. Zero additional fabricated legislative decisions or executed contracts. Original-event dates and first-observed event timestamps retained separately.
- [licensed secondary directory importer](../scripts/import_licensed_agency_network.py) uses outbound recipient SHA to watch **genuine cross-snapshot changes**. Empty recipient lists have stable SHA so removal of last edge / addition of first edge is detected. No site/user query logs or plate read history collected.
- [email sender](../scripts/send_government_watch_alerts.py) checks explicit user preferences, signup date threshold, identity-bound delivery receipts, HTTPS-only sources, TLS-encrypted SMTP 465/587, and no private details in logs. [daily workflow](../.github/workflows/send_government_watch_alerts.yml) already passed source synchronization.
- [Watch UI](../government-watch.html) plus [watch-email.js](../watch-email.js) supports optional confirmed-account signup/sign-in, per-locality opt-in, category selection, unsubscribe, and existing offline browser follows. Opt-in must come from an actual user; not registered on their behalf.
- **Delivery blocker**: GitHub Actions WATCH_SMTP_HOST, WATCH_SMTP_PORT, WATCH_SMTP_USER, WATCH_SMTP_PASSWORD, WATCH_SMTP_FROM currently unset. No external mail delivered, **zero subscribers** and **zero delivery receipts** confirmed in live Supabase as of this checkpoint. Real mailbox signup/confirmation/send/unsubscribe acceptance also open. Do not claim email alerts are live until the operator configures a sender and confirms an opt-in mailbox end-to-end.

### P1 · Agency X-Ray: spending, retention, transparency gaps
- [X-Ray](../agency-xray.html) joins locality-scoped original government records, trusted source-mapped GIS, direct Flock portal snapshots, and the licensed secondary portal directory. Locality grouping is **not proof distinct agencies are identical**; no autogenerated hardware position.
- Reviewed **signed Flock contracts** list original source and price when documented. If none, display *unknown*, not "$0". Source end dates come from [security-invoker view](../supabase/migrations/119_sharing_fingerprints_and_contract_end_dates.sql).
- Direct Flock portal retention reports and independently sourced **secondary aggregator retention history** are kept in separate tiers. [migration 121](../supabase/migrations/121_secondary_retention_history.sql), [source importer](../scripts/import_licensed_retention.py), [weekly workflow](../.github/workflows/import_licensed_retention.yml) verified in production: **1,601 dated secondary retention observations; 1,525 numeric, 76 unknown**, no camera coordinates. Historical changes only flagged when two nonempty dated readings disagree.
- [migration 122](../supabase/migrations/122_bounded_agency_retention_public_view.sql) shows latest three observations per agency so weekly growth never silently truncates frontend API history. Original append-only history retained in protected RLS source table.
- Missing first-party GIS, missing reviewed contracts, missing source-date evidence, missing recorded legislative decisions and missing retention time series explicitly labeled as *missing in Katoptron*, not evidence a government agency never published the information.
- No user travel/plate data, undisclosed agency queries or raw source account history added.

## Releases and boundary testing
- RLS/privacy gate [SQL tests](../scripts/test_agency_watch_security.sql) passed live against Supabase for protected subscriber data, public secondary directory, and service-only recipient RPC.
- [GitHub disposable database & script validation](../.github/workflows/validate.yml) runs migrations 117–122, Python import/email tests, provenance guard checks and frontend syntax.
- [Browser smoke](../scripts/smoke_agency_intelligence.cjs) covers X-Ray, local follows and full directional network, and existing map/pan protections continue to run.
- Source-bot network mirror is only published after complete count/identity checks. It now creates ordinary deployable commits (without `[skip ci]`), so site assets update on weekly refresh.

## Known remaining external and independent acceptance
1. Owner set **encrypted SMTP sender GitHub Actions secrets** and verify actual recipient mailbox in an authorized test: ensure one notice received on new source event, preferences respected, link opens original evidence, unsubscribe blocks future sends and no duplicate once receipt recorded. Existing workflow explicitly reports "NOT ACTIVE" when sender absent.
2. Agency-source **identity matching** is based on canonical IDs within the licensed network and agency/city/state names across independent Katoptron data categories. Dossiers show the join as a browsing convenience; an individual agency ownership claim needs separate first-party corroboration to resolve multiple municipal agencies.
3. This network still reflects the source's most recent reported data, not currently guaranteed sharing. Status changes require a later verified snapshot; unavailable sources are unknown, not withdrawn.
4. Independently confirm publisher rights/attribution terms for any additional data used and avoid upstream invalid reliance.
5. Human Auth/email confirmation, external routing quota, encrypted off-device recovery, original-camera source expansion and accessibility assessments remain separate whole-product beta/production gates.

## Follow-on briefs
Once agency identity and source-specific ownership are more reliably linked, generate one-click, citation-driven HTML/PDF briefs with as-of dates, evidence-tier labels, contract amount/term, policy snapshots, and documented unknowns. No generative assertions from a city name, no unsupported agency votes or camera coordinates.
