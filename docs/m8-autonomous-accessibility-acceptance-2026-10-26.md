# M8 accessibility — autonomous engineering acceptance
**As of October 26, 2026.** **Engineering and test-infrastructure completion estimate: 95%.** Public beta can use the remediations and continued automated monitoring. **WCAG 2.2 AA conformance is not certified.**

## Scope and source of acceptance

- **33 static anonymous page/viewport WCAG 2.2 A/AA axe-core audits**: eleven public pages × 320, 390, 1280 CSS-pixel viewport widths. Checks include WCAG 2.0, 2.1 and 2.2 tags supported by axe-core; both separately named workflows run the same source code, not independently conducted human audits. Both workflows passed on the M8 release: [automated audit #40394125359](https://github.com/ayeemecee0/Katoptron/actions/runs/40394125359) and [release acceptance #40394125360](https://github.com/ayeemecee0/Katoptron/actions/runs/40394125360). Automated zero violations is **not** proof all WCAG criteria pass.
- **Eleven forced-colors adversarial browser cases**: [M8 independent acceptance #40394594534](https://github.com/ayeemecee0/Katoptron/actions/runs/40394594534) passed on index, government records, accountability, analytics, contributor signup/submission, reviewer sign-in, privacy, methodology, portals, public community map, and nearby evidence. The test uses real Chromium media emulation of Windows forced-colors mode, reduced motion, 320 CSS-pixel viewport and an injected custom letter/word/line/paragraph spacing stylesheet. Asserts no page-wide horizontal reflow, that visible action targets are at least 24×24 CSS pixels (for tested button/summary/select/nav targets), that skip navigation receives first keyboard focus and its outline/geometry is visible after browser rendering.
- **Combined production browser smoke**: [#40394594635](https://github.com/ayeemecee0/Katoptron/actions/runs/40394594635) passed full GIS map, navigation, mobile (390 CSS pixels), provider adapter, responsive map, route and community evidence, reviewer/contributor mock, 640px zoom-equivalent form and navigation checks, and the M8 adversarial suite. The previous combined smoke failed due a transient upstream OSM HTTP 500 **before** the M8 tests were reached. The later successful run resolves the release check but does not promise an external provider will never return errors.
- **Source validation and deployment**: [full validation #40394594443](https://github.com/ayeemecee0/Katoptron/actions/runs/40394594443) passed. [GitHub Pages #40394594056](https://github.com/ayeemecee0/Katoptron/actions/runs/40394594056) deployed the latest tested M8 code successfully.

## Engineering changes delivered

The shared [a11y.css](../a11y.css) now includes:

1. Minimum action heights for button, select, disclosure summary, navigation and Leaflet zoom controls; 28 CSS pixels for specified targets and WCAG 2.2 24 CSS-pixel minimum as the tested threshold, with inline-text/spacing exceptions preserved.
2. Keyboard target focus appearance and reliable skip-link visibility after two browser render frames, including under forced colors and reduced motion. The independent test originally found a false immediate-after-focus failure because the focus was updated before paint; a direct focus CSS guarantee and stable rendered focus test now pass.
3. Use of system `Canvas`, `CanvasText`, `Highlight`, `ButtonText` and `LinkText` colors in forced-colors mode; stronger shape/focus/underline affordances independent of color-only cues.
4. Clearer source link underlines in records and public map attribution, non-drag button access, explicit scroll margins for focused/targeted elements, and wrap-safe narrow-screen button/toolbar labels.
5. Preference-sensitive motion suppression without changing the privacy/evidence map's data eligibility or route logic.

The expanded synthetic form-state scan is checked by the same [axe script](../scripts/audit_wcag_axe.cjs). The [320px high-contrast acceptance script](../scripts/smoke_m8_adversarial_accessibility.cjs) is independently release-triggered through [accept_m8_adversarial_accessibility.yml](../.github/workflows/accept_m8_adversarial_accessibility.yml), **not blocked by unrelated OSRM/OSM or API service failures**. The same script also runs inside combined browser smoke. [WCAG axe automated scan](../scripts/audit_wcag_axe.cjs) now covers three viewport widths rather than two.

## October 26: extended signed-out, recovery, and authenticated-form coverage

- The owner completed a **real** live email confirmation and password-recovery cycle, independently consistent with Supabase production Auth events: signup request HTTP 200, confirmation verification HTTP 303, recovery request HTTP 200, recovery verification HTTP 303, and password update HTTP 200. The owner confirmed signing back in with the new password. This closes the **functional email-link dependency**, not screen-reader accessibility certification.
- The WCAG 2.2 axe script now screens **42 page/state/viewport combinations** (11 anonymous screens plus synthetic visible recovery form, contributor private-report form and reviewer workspace, at 320, 390 and 1280 CSS pixels). These extra three states are **synthetic visual/DOM checks** only; they do not access or create any actual private records, authenticate users, or constitute an independent human accessibility audit.
- The private review rationale textarea is now named programmatically for its report and marked required. An invalid review rationale exposes `aria-invalid`, announces the corrective instruction through the status region, returns keyboard focus to the field, and clears the invalid flag as the text is corrected. The authenticated fake-client browser acceptance asserts all of these behaviors.
- The signup/recovery component now already includes keyboard focus and invalid-field announcements; the live human functional email run validates the links, **not** whether an actual screen reader perceives those announcements.

## October 26 owner acceptance: beta-release waiver (not a test pass)

**Decision:** The project owner explicitly declined to run NVDA manual screen-reader testing and instructed that it not block progress. **Disposition: WAIVED / RISK ACCEPTED FOR LIMITED BETA**, rather than "NVDA PASSED." No human screen-reader results were produced or inferred. This is an acceptance decision, not evidence of WCAG conformance.

**Observed human browser checks on October 26:**
- Chrome 400% zoom: owner could navigate to required forms. This is an observed reachability check, not a complete responsive-layout audit.
- Keyboard skip-to-content: an actual user found that Enter appeared to do nothing; [PR #27](https://github.com/ayeemecee0/Katoptron/pull/27) made all 11 main landmarks programmatically focusable and visibly outlined. Following [PR #28](https://github.com/ayeemecee0/Katoptron/pull/28), painted-focus/forced-colors regression passed. The owner independently re-tested and reported the keyboard fix **PASSED**.
- Real signup, confirmation, password recovery, and subsequent sign-in: owner completed the full email flow; production Auth logs corroborated the events.

**M8 beta disposition: ACCEPTED WITH EXPLICIT ACCESSIBILITY WAIVER.** The engineering milestone can be treated as closed for the limited public beta workflow; do not claim independent NVDA/VoiceOver, real-device touch/high-contrast, accessibility of private report deletion, full user acceptance, or WCAG 2.2 AA conformance. Retain those as a separately tracked, unverified accessibility assurance backlog. If a real user reports a barrier, reopen M8 immediately and prioritize remediation. The prior **~95% full accessibility-assurance estimate** remains an estimate and does not become a 100% verification claim because tests were waived.

## Important limitations and remaining real-world acceptance

This is a **95% planning estimate**, not 95% of WCAG criteria mathematically verified. The remaining scope cannot be completed by unattended CI:

| Independent acceptance | Evidence still required |
|---|---|
| NVDA on Windows + Firefox and/or Chrome | **Waived by project owner for limited beta; NOT TESTED, NOT PASSED.** Still unverified: correct spoken main, heading, link, region, form-error and dialog names, operable map alternative |
| VoiceOver on macOS/iOS and/or TalkBack Android | Human tester navigates all 11 public pages, selects government source records, identifies filters and consent, and can escape/interact with Leaflet map |
| Actual browser 200% and 400% zoom | **Manual 400% zoom reachability check PASSED** on Chrome per owner. Other browser/device combinations and comprehensive reflow remain unverified; proxy 640/320 CSS-pixel tests do not reproduce all magnification behavior |
| Genuine system high-contrast mode and physical touch/keyboard | Confirm Android, iOS and Windows system preferences, hover-independent navigation, small targets, external link discoverability, and map gestures |
| Form error correction, consent and real email links | **Live email signup, confirmation, recovery and new-password sign-in passed October 26.** Still need real assistive-technology observation of error correction, and separately a consented private report submission/withdrawal/erasure test |
| Independent WCAG review and user feedback | Qualitative keyboard/screen-reader observation, actual accessibility bug triage, documented manual pass/fail and remediation |

A verified human-accessibility report with test date, browser/OS, actual assistive technology version, recorded pass/fail by page, evidence of corrective re-tests and named accountable reviewer is necessary before declaring **full** WCAG 2.2 AA conformance or M8 100%.

## Human testing procedure (when authorized participants become available)

1. On each public page: keyboard-only Tab/Shift+Tab, Enter/Space, escape from map or disclosure, skip directly to main, focus indicator never fully clipped, arrow navigation in evidence tab control.
2. Verify actual 200% and 400% browser zoom; no required instructions or source records disappear outside intentionally scrollable data tables/maps.
3. Use real NVDA/VoiceOver to navigate headings and map/source alternative, then inspect government evidence without relying on color or a draggable map.
4. With a consenting test user, request a signup email and complete confirmation, one invalid then corrected report submission, photograph disclosure, optional publication consent and permanent erasure. Avoid fabricating a real-world camera or leaking screenshots of private records.
5. Audit error announcements and state changes after network failure, provider outage and photo deletion failure; record defects, corrections and repeat tests.

## Conclusion

**M8 limited-beta release ACCEPTED WITH WAIVERS; independent accessibility assurance remains ≈95% estimated and unverified.** Developer-controlled static/audited behavior and measurable negative cases are implemented, deployed and passing. No simulated test may be represented as actual NVDA, VoiceOver, touchscreen or independent human certification. **M9 remains separately open** for encrypted recovery backups, provider account controls, actual operational ownership and reliable sender reputation. Functional owner-tested email confirmation and password recovery no longer block it.
