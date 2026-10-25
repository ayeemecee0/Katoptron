# Katoptron MVP — user and privacy acceptance (October 24, 2026)

**Release tier:** evidence-limited, read-only public beta first. This is NOT a full production SLA or proof of nationwide camera coverage. The primary user promise is to show credible source-documented Flock camera positions on a route, state the limitations, and distinguish hypothetical surveillance replay from observed events.

## Recorded engineering evidence (not human testing)
- The original-government crawler now follows bounded generic municipality GIS/map navigation but only queues privately after an independently re-fetched Flock-specific disclosure; unendorsed Esri datasets cannot become canonical.
- Current independently checked baseline: 293 exact source-backed camera point locations in seven trusted original-government GIS datasets. A route with zero published points is **unknown coverage**, not a surveillance-free route.
- Automated browser tests cover route alternatives, map displays, keyboard and mobile layouts, UI signup/report/withdrawal mocks; an authenticated production Auth/Storage synthetic smoke previously tested APIs. **These are not observations by real outside users**.
- Local owner-led PostgreSQL 17 restore of updated roles/schema/data succeeded, retaining 293 verified points, one Auth user and RLS for 48 public tables. Private-report ownership and anonymous table grants were checked. An initial restore showed overbroad inherited grants, corrected by revoking local default table grants BEFORE import. Auth email delivery and off-device backup were not proven by this exercise.
- The current production database inspection showed zero private community submissions and zero private photo objects. There is therefore no existing private photo corpus to recover today, but newly accepted photos require retention/deletion and future backup coverage.

## Human usability pilot: five volunteers (NOT YET RUN)
Recruit at least five people who have not developed Katoptron; aim for a mix of desktop/mobile and at least one keyboard-only tester. Ask them to narrate their interpretation, not disclose any private travel information. **Do not tell the tester the correct response before they attempt each task**.

Give each tester the public URL: https://ayeemecee0.github.io/Katoptron/. In a 10–15 minute session:
1. Find how many camera locations are *source-verified* and understand that other places may be unmapped. Ask: “If a place has no pin, does that mean there are no cameras?” Mark PASS only if they say no.
2. Use the built-in **Sacramento → Folsom sample** route. Do not use their home, work, school, habitual travel or any individual's route.
3. Compare two offered routes, if the provider presents alternatives. Ask whether the route showing fewer **documented** points is guaranteed to mean fewer functioning cameras. PASS requires no.
4. Open one published camera or official records page and locate its original government source. Ask what that source proves: documented coordinates, not current uptime or any actual plate reading.
5. Find the simulation toggle and explain why its observations are hypothetical. Ask whether this app saw their car, plate, or Flock account data. PASS requires no.
6. Optional: navigate without a mouse, or on phone at zoom/high-contrast settings. Do not claim WCAG compliance from this small exercise.

Record only anonymized completion/difficulty scores and product wording problems, not routes, personal addresses, plates, screenshots containing private data, raw session recordings or user identifiers. Offer this [public, privacy-checked issue form](https://github.com/ayeemecee0/Katoptron/issues/new?template=mvp_usability_feedback.yml).

**Pilot pass criteria (predeclared):** at least 4/5 can plan a sample trip and find the official source without assistance; 5/5 distinguish a zero published count from “camera-free”; 5/5 distinguish modeled sightings from actual ALPR reads; no confirmed leak of personal data or private camera reports. If anyone misreads the distinction, fix the wording and retest; do not lower the passing rule to declare success.

## Contributor flow: explicitly separate limited from public launch
Automated tests exercise real production Auth and Storage APIs with ephemeral admin-confirmed synthetic accounts, plus browser mocks for sign-in, private report, image sanitation/upload, reviewer decisions, withdrawal and retry deletion. **The real signup confirmation email has NOT been observed in a real mailbox.** Actual human participants must verify the signup-link arrival and return URL before the contributor intake is treated as generally released. The UI now explains new-account password requirements and distinguishes pending confirmation from an immediately authenticated session.

For one account they control (no password shared with maintainers): create an account, open a confirmation link from the email inbox and return to submit.html, sign in, sign out. Never create a fictional sighting in the publicly accessible production report workflow. To test report deletion, use a distinct authorized QA setup with clearly synthetic report/photo data, not the live public evidence queue. Record pass/fail and zero synthetic debris after cleanup. Review account email/redirect allowlists, rate limits and Auth abuse protection in the Supabase owner dashboard.

## Recovery minimum for public read-only beta
The newly exported owner-only SQL files are restorable, but source exports may include Auth and private database content and must not be uploaded into GitHub or public logs. Verify the current Windows volume is encrypted before relying on a local copy. A second **encrypted** copy on a separate physical device is prudent and should precede any substantial real-user private evidence intake; do not mislabel a single local copy as resilience against laptop loss, ransomware or disk failure. Storage object content is not in SQL dumps. The project cannot certify physical off-device replication or Windows encryption remotely.

## MVP research & release decisions
- Spend most near-term engineering effort verifying additional genuine **first-party** government-owned GIS inventories or documented original-agency links to external Esri layers. Inspect original records and complete point inventories; avoid double-counting. Hold questionable externally hosted, OSM-only or single-source cases private.
- Maintain route-provider monitoring, RLS and immutable government source provenance as nonnegotiable. Public counts are a narrow documented floor, not nationwide total camera prevalence.
- Keep 10% of routine effort for discovery pipeline maintenance, metadata drift and original-source disappearance checks.
- Human pilot, real email-confirmed Auth and owner-local encryption verification are **open gates**, not achievements. Do not report them complete based on mocked or synthetic API tests.
- No paid hosting, broad crowd-source publication or extra private-data collection is required just to run the read-only MVP.
