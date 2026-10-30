# Katoptron product-capability, workflow and redundancy audit
**Evidence observation:** 2026-10-30. **System:** `ayeemecee0/Katoptron` main repository, connected Supabase `bpvkapswslmgfazbzpsv` (aggregate count queries only). This audit is not an independent user-study result.

## Existing capabilities: do not pitch as unbuilt milestones

| Capability | Existing implementation | Maturity and limits |
| --- | --- | --- |
| National community camera map, exact government GIS tier and route simulator | `index.html`, `community-map.html`, `nearby.html`, mapping scripts | Existing; community marks do not prove devices active or manufacturer identity |
| Agency X-Ray, spending/policy timeline, sharing explorer and source-cited agency comparisons | `agency-xray.html`, `agency-intelligence-hub.html`, `agency-compare.html`, `sharing-explorer.html` | Existing; some access-network evidence is secondary rather than first-party |
| Investigative lead engine and discrepancy/gap finder | `professional-intelligence.js`, `professional-intelligence-app.js`, `nationwide-research-leads.html` | Existing; reviewed published events are not inferred from raw source changes |
| Source-qualified Government Watch and opt-in research feeds | `government-watch.html`, `research-email.js`, `scripts/send_personalized_research_emails.py`, `research_intelligence_follows` | Existing; **0 enabled research emails / 0 research follows** at audit; live delivery/retention thresholds unproven |
| Original-government acquisition, version review and immutable archive | `scripts/watch_nationwide_government_originals.py`, `scripts/archive_government_original_versions.py`, `scripts/private_original_archive.py` | Existing; on October 30 full cold-cache restore verified 223 original versions, not proof that all sources are reachable |
| Source-linked investigation packs and exports | `professional-intelligence.html`, `agency-government-brief.html`, `research-workspace.html` | Existing; human legal / factual sign-off not automatic |
| Private team investigations, request drafts, dates, history, evidence and deletion | `research-workspace.js`, Supabase migrations 150–164 | Existing and RLS-tested; **0 user cases / 0 private workspaces / 0 saved requests** at audit |
| Role-specific professional request templates | `research-templates.js` | Existing |
| Research pilot sign-up and time-saved measurement | `research-pilot.js`, `research_pilot_interest`, `research_pilot_task_measurements` | Existing instrumentation; **0 pilot signups / 0 measurements** in database at audit |
| Original Naperville policy comparisons | `data/naperville-paired-policy-clause-revisions-2026-10-29.json` | Ten prepared; independent reviewer approvals still **0** |

Current public database has **29 Government Watch events**, not 29 newly discovered or human-accepted investigations. Counts are observations, not usage guarantees.

## Gaps closed by this change

1. **Request lifecycle closure:** `records-copilot.js` adds five specific original-record categories (contracts/spend, policy, audits, access/sharing, termination), requested date limits, explicit fee limit, format preferences and original-source context. Nothing is silently submitted.
2. **Evidence-grounded response follow-up:** nine researcher-selected agency reply categories produce narrow, editable reply drafts and a checklist of what is still unknown. The user supplies the response interpretation; no private attachment is sent to an AI model.
3. **Actual private workflow reuse:** draft/copy/save uses existing RLS-protected `research_case_requests` and immutable request activity logs. Follow-up date and request state remain manual/verified inputs. No database tables, key material or speculative legal deadlines were added.
4. **Fixed source-lead handoff:** Professional Intelligence's existing `agency`, `title` and `source` link inputs now prefill a preview in Research Workspace. The user must still validate and explicitly create the private case.
5. **Simplified first encounter:** homepage main navigation reduced from **26** primary links to **7** task-oriented links. All 21 specialist/historical links are retained under an expandable archive. No evidence document, table, page or URL was deleted.

## Actual complexity and unnecessary duplication candidates

### P0: Duplicate visible research entry points — mitigated, not deleted
`professional-intelligence.html`, `pilot-research.html`, `pilot-dossiers.html`, `nationwide-research-leads.html`, `research-acquisition.html` and `research-workspace.html` contain overlapping research discovery or records request flows. The public-facing path should be **Investigate -> choose cited lead -> private case -> request -> response -> documented finding**. Old URLs must remain because citations and external bookmarks may depend on them. Do not create another standalone copilot page.

### P1: Request generator fragmentation — still merits internal refactor
`professional-intelligence.js` builds document-gap drafts, `research-templates.js` has role templates and the new `records-copilot.js` produces narrowly scoped records and agency-response follow-ups. Their use cases differ but broad draft-copy logic overlaps. Eventually route all through a single bounded request schema while preserving context-specific questions; first run snapshot regression tests so prior verified citations and template output are not lost. New UI should not fork a fourth generator.

### P1: Several date-frozen evidence pages and competing counters
`research-acquisition.html`, historical recovery JSON and several other pages explicitly display 2026-10-29 dated workplans while newer 2026-10-30 snapshots and live source-health counters also exist. This creates an *apparent contradiction* unless each display is clearly labeled historical versus live. Preserve evidence and URLs. Next safe consolidation: central provenance/read-model with “as-of”, run SHA, retrieved/held/ever-recovered distinction. Never delete historic reference files to reduce visual clutter.

### P1: Multiple government source watcher workflows — confirm scope before consolidating
`watch_original_government_versions.yml`, `watch_sacramento_county_original_sources.yml` and `watch_nationwide_government_originals.yml` scan related evidence but serve different editorial, local and national functions. Audit source IDs, acquisition cost, event deduplication and publication gates before merging any schedules. Unverified deletions risk silently dropping monitored jurisdictions.

### P2: Specialized one-off HTML views — keep as read-only archive
Agency/dataset-specific audit pages overlap the central Agency X-Ray and professional research UI. Freeze legacy pages as labeled historic/citation pages and direct new task entry to canonical consoles. Do not remove publisher evidence, human-review status or permanent reference links.

### Not unnecessary and **must retain**
- Private RLS, audit logs, source hashes and the exact-original archive.
- Human publication gates that prevent false changes and camera-identity inferences.
- Source revision and publisher-outage history.
- Community versus government GIS confidence distinctions.
- Export/privacy/deletion safeguards, including consented opt-in email boundaries.

## Where NOT to invest next
Building generic FOIA request drafting, request-status tracking, map layers, standalone dashboards, lead lists, or another Agency X-Ray screen as if absent. Those exist. Competing head-on with [MuckRock](https://help.muckrock.com/How-MuckRock-Works-19ef889269638140b169c8224a4c7c05), which already handles filing/tracking/sharing and public record archives, is not a meaningful differentiation. Federal [FOIA.gov](https://www.foia.gov/how-to.html) already helps locate agencies and records; state and local laws differ and must be verified rather than inferred.

## Genuinely different high-value bets (proposal, not yet implemented)
1. **Proof-of-outcome ledger (P0):** connect government promise -> approved budget -> executed vendor contract -> invoice/payment -> actual documented installation, removal, access cutoff and deletion. Label every missing link. Today's agency timeline is not a complete independent outcome chain.
2. **Public-release reuse network (P0 pilot):** with explicit researcher consent and redaction review, publish government-produced source originals and request outcomes into reusable, hash-cited public collections. Check existing records *before* filing a duplicate request; keep private workspaces default-private and never auto-publish response attachments.
3. **Pre-decision civic windows (P1):** authenticate agenda dates, renewals and public comment processes; deliver a concise referenced brief while a local government decision is still pending. Distinct from the existing historical Government Watch event feed. Do not fabricate deadlines.
4. **Records-office service evidence (P1):** aggregate voluntarily shared, privacy-sanitized actual acknowledgment dates, fee quotes, response categories and completion times, with per-agency minimum sample sizes and uncertainty. No user tracking or accusation from a single denial.
5. **Public finding challenge and correction protocol (P1):** structured source-backed rebuttals, an editorial decision history and versioned public corrections. Stronger trust and accountability than an unreviewable "verified" badge.

## Next measured completion gates

- Five independent researchers successfully follow lead -> private case -> original-record request -> actual reply classification -> saved follow-up. Zero cross-account disclosures in RLS acceptance.
- Ten independent authentic document or agency-response evidence resolutions, with proof of government action versus mere proposal and external editorial approval before publication.
- At least three validated completed tasks with recorded researcher time saved, separate from synthetic test successes.
- Three users explicitly request the same *new* differentiated workflow before building a seventh dashboard.
