# Katoptron M9 — Incident response and alert delivery drill

**Version:** October 26, 2026. **Service tier:** evidence-limited public beta. **Status:** operating procedure documented; owner notification delivery and human incident drill still require observation. **No 24/7 on-call or SLA is claimed.**

## What is monitored

- [M9 release heartbeat](../.github/workflows/monitor_release_gates.yml): checks fresh main-branch passes for browser, source/evidence, routing, private data, retention and capacity release gates. It is a scheduled check, not an always-on paging service.
- [Public map](../.github/workflows/monitor_public_health.yml): checks hosted site, public records and anonymous access.
- [Route providers](../.github/workflows/monitor_route_providers.yml): checks routing/geocoding and runs a real browser-origin Geoapify smoke test.
- [Private launch](../.github/workflows/monitor_private_launch_gates.yml): checks private Storage and source-discovery metrics.
- [Free-tier capacity and privacy retention](../.github/workflows/monitor_production_capacity.yml): checks conservative database usage/retention using aggregate-only private RPC. Organization-wide provider storage/billing must still be checked in provider dashboards.

GitHub Actions are not independent of GitHub availability and scheduled runs can be delayed. The owner reports enabling failed-workflow email notifications on October 26. **An email alert has not yet been independently observed from a controlled failed run.**

## Severity and response

| Severity | Examples | Immediate decision |
| --- | --- | --- |
| P0 security/privacy | Private report/photo revealed anonymously, reviewer privilege bypass, secret exposed, public coordinates promoted without evidence | Contain affected access/publication first; protect people and evidence; prevent further submissions if privacy is uncertain |
| P1 critical availability/integrity | Main site inaccessible, public camera evidence materially corrupted, sign-in or private-report erasure broken, restore impossible | Stop unsafe affected functionality, diagnose and restore only after tests |
| P2 partial degradation | Geoapify temporary outage, stale discovery job, rate-limited geocoder, delayed emails without evidence of exposure | Label affected feature degraded, avoid representing missing results as “camera-free,” investigate provider limits |
| P3 routine | Duplicated candidate, documentation error, low-impact delayed publication | Queue issue, verify original source, update audit trail |

**Provisional owner operating target, not a guarantee:** investigate P0 as soon as detected; P1 the same day when available; P2 next review cycle. A full contributor launch needs a real accountable operator and an explicitly agreed response/notification window. Do not imply around-the-clock oversight from daily GitHub scheduled jobs.

## Triage checklist

1. Open [GitHub Actions](https://github.com/ayeemecee0/Katoptron/actions); note workflow, main-branch commit, first affected UTC time, run URL, last known green run, and relevant public symptom. Check [GitHub Status](https://www.githubstatus.com/) and provider status before attributing an outage.
2. Reproduce only with public, non-sensitive samples at [Katoptron](https://ayeemecee0.github.io/Katoptron/). Do not paste user addresses, private camera reports, access tokens, account identifiers, photographs, SQL backups, or connection strings into public issues or CI.
3. Check whether the failure is a false alarm, stale scheduled run, actual website outage, quota issue, source revocation, Auth email issue, or private access problem. Treat “zero published evidence” as unknown coverage rather than absence of cameras.
4. For P0, limit/revoke the affected access path using reviewed configuration or a tested code/migration change. Preserve minimum necessary private evidence locally, never in the public repository. Protect an affected contributor's erasure path. **Do not delete live Storage objects using SQL.**
5. Re-run the affected test(s) and [release heartbeat](../.github/workflows/monitor_release_gates.yml); verify GitHub Pages deployment and public route behavior, private RLS and contributor functions when relevant. A green unit test does not itself prove production impact ended.
6. Record incident start and mitigation time, user-visible scope, verified cause, retained source/PR links, follow-up owner and date. Public issue only if it contains no private data; sensitive incidents require a private owner-controlled channel (still to be defined before unrestricted private contributor launch).

## Specific mitigations

- **Geoapify unreachable or out of free credits:** Treat routes as unavailable/degraded. Never fabricate route coordinates, times or sightings. Check allowed origins and current provider quota/billing in the Geoapify owner dashboard; keep the Free plan unless the owner explicitly authorizes costs.
- **Camera/source evidence invalid:** Hold/retract the affected *publication* with an auditable source-dated explanation. Do not promote approximate/community reports to equipment-verified points. Preserve revision links; re-check camera map and original-source evidence.
- **Auth email delivery outage:** Inspect Supabase Auth logs and SMTP owner dashboard privately. Do not publish credentials or confirmation links. Account recovery and erasure failures are launch blockers for unrestricted private contributions.
- **Private report/Storage exposure:** Treat as P0; limit the exact affected surface, inspect RLS and bucket privacy, validate with anonymous/authenticated negative tests, and assess required contributor notification without posting private records publicly.
- **Database quota or backup failure:** Check Supabase dashboard quota, current encrypted off-device backup, and backup freshness. Do not restore a dump into production without an isolated recovery dry-run and owner authorization.

## Disaster recovery status and hygiene

The owner reported on October 26 a tested AES-256 7z archive copied to restricted Google Drive, re-downloaded and opened without errors; then an actual owner-controlled local **isolated PostgreSQL 17 recovery** with **2 Auth accounts, 316 source-attributed exact GIS camera records, all 82 public tables protected by RLS, anonymous report SELECT/INSERT blocked, ordinary authenticated reviewer SELECT blocked, private Storage bucket not public, 0 private reports and 0 private objects**. SQL archive copies and the disposable recovery database were removed afterward. This demonstrates recovery of the October 26 snapshot, not continuous automated backups, future photo-byte recovery, provider secrets, email configuration or disaster recovery time.

Backups must be renewed after changes and private submissions; private Storage object **bytes** must be separately backed up once photos exist. Store encryption passwords apart from archive and never upload raw SQL or private media to GitHub. Recovery objective and repeat schedule require explicit owner acceptance; no continuous backup coverage is claimed.

## Harmless alert delivery drill

1. In GitHub **Actions**, select **M9 manual notification delivery drill (intentional failure)** and click **Run workflow** on `main`. This workflow has no checkout, no credentials or access to production services. It deliberately executes `exit 1`.
2. Verify the run is marked **Failure**, with log marker `M9 ALERT TEST`. That failure is expected and must **not** be interpreted as a broken production service. It is excluded from the release heartbeat's required workflows.
3. Look for a GitHub Actions failure notification in the owner's configured email inbox, including spam. Record whether email arrived, its receipt delay, and the observed link to the known drill. GitHub's notification behavior depends on per-user settings and triggering context; a red Actions run alone does **not** prove alert delivery.
4. If no email arrives, fix notification preferences or establish an independent monitoring/alert service and repeat the drill. No positive acceptance without an actually received alert.
5. Do **not** repeatedly dispatch this drill, add production secrets, intentionally fail real release monitors, or publicly post private contact addresses.

**Remaining owner actions:** observe alert delivery, accept an incident-response window/private contact channel, and complete outside-user and assistive-technology beta tests. Until then M9 full production remains incomplete.
