# Nationwide government original-source monitoring: continuity and documented gaps

## Scope and strict definition of completion

All 50 states plus D.C. are enrolled in a **state-level original-government source monitoring queue**. The 45 newer government-published source seeds and 14 independently curated original-government publisher URLs are now scheduled for retrieval and status checks: **59 curated URLs across 51 state jurisdictions**. Each state has at least one curated source. This is **not** a complete list of local agencies, Flock contracts, policies, cameras, sharing relationships or legal status in any state.

The prior archived 2026-10-27 registry contains 43 actual retrieval receipts out of the 45 newer seeds; the 14 legacy sources had no shared monitored receipt baseline. Therefore **16 of 59 sources require their first comparable national monitoring observation** relative to this archived file. The new scheduled monitor collects those observations. A monitored URL is not a validated claim about agency Flock use.

## Operational design

- [Daily original-government monitor](../.github/workflows/watch_nationwide_government_originals.yml) examines every curated URL. The job runs at 19:11 UTC and on explicit dispatch, with bounded requests, limited concurrency, prohibited redirects and public-IP origin checks. Cross-host and private-network URLs are rejected.
- [watch_nationwide_government_originals.py](../scripts/watch_nationwide_government_originals.py) generates receipt records containing source ID, exact original source URL, current retrieval status, content SHA-256 (only for successfully parsed originals), and whether same-host links merit further review. Source content is not published as government-verified camera, executed contract or adopted policy.
- [nationwide_source_health.py](../scripts/nationwide_source_health.py) compares that day's fetched receipts to the latest successful monitoring snapshot restored from the GitHub Actions cache. With no prior cache, it falls back to the dated archived 2026-10-27 source receipt baseline. New first observations, changed hashes, previously successful but currently held sources and never-accessible sources all have separate **review-only** categories.
- If a URL is held, the previous successfully observed fingerprint and its date are retained separately; the current URL is *not* marked accessible or unchanged. A changed SHA-256 signals changed bytes only, NOT a contract amendment, enactment, retraction, newly installed camera, or material policy change.
- The monitor produces a 51-row state health report, individual source receipt history and actionable but **unverified** source-change/gap review queue. GitHub Actions stores 30-day audit artifacts and the last successful fingerprint snapshot as a best-effort cache. Neither CI cache nor Actions artifact retention is a permanent database; longer-term archive/object storage and cache-miss monitoring remain future work.
- The [public state source-monitor page](../nationwide-source-monitor.html) displays the **archived baseline only**, labeled with its date, and links to GitHub Actions for newer monitored results. It does not assert that the archived status is the live current state.

## Non-negotiable evidence boundaries

A successful original-government response proves only that Katoptron could retrieve the specified publisher URL and fingerprint the bytes. Even if its text contains “Flock,” source analysis is separately required for agency identity, signed-vs-proposed status, dates and page citations. A scan never publishes new camera coordinates or per-vehicle observations. State-level source access never establishes a comprehensive agency inventory. A review lead is not a validated new Watch event and cannot send an email.

## Reliability validation

- `python -m unittest discover -s scripts -p test_watch_nationwide_government_originals.py -v`
- `python -m unittest discover -s scripts -p test_nationwide_source_health.py -v`
- `node scripts/smoke_nationwide_source_monitor.cjs` after serving the site locally with Playwright
- GitHub Actions report has distinct reachable, held, newly observed and changed-fingerprint counts, 51 individual jurisdiction entries, and state-specific held-source IDs.

## Next value milestones

1. **P0**: daily monitoring success on seven consecutive days; identify and remediate held/corrupt original sources in every state, replace expired original URLs after independent review.
2. **P0**: collect durable archive outside ephemeral CI cache with consent/safety review and weekly snapshot retention; enable published state-health *metadata only*, while original document claims remain review-gated.
3. **P0**: independently review at least 25 *new* original documents from undercovered jurisdictions, including agency identity, exact text and page citation. Publication as verified evidence requires the editorial verifier and separate sources.
4. **P1**: auto-triage document diff leads into validated contract/policy version comparisons: 10 page-cited, human-reviewed changes.
5. **P1**: connect users' chosen jurisdictions to only genuinely new original-government findings; validate 10 opt-in research digests with zero duplicate sends.
6. **P1**: onboard 10 active pilot professionals, test claimed novelty and time saved, and obtain at least three credible paid commitments.
7. **P2**: extend verified source jurisdiction depth beyond one seed per state, build provenance-linked local agency directories with explicit missingness; never call them all-state agency censuses until independently demonstrated.

**Status interpretation:** nationwide source-monitoring enrollment can be complete while nationwide document verification, source reachability, sustained operations and agency coverage are not.
