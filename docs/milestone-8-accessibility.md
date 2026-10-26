# Milestone 8 — Public experience and accessibility improvements

> **October 26 update:** M8 autonomous engineering preparation is now estimated **95%** (previously 85%) after actual Chromium high-contrast/forced-colors, 320px 400%-zoom-equivalent reflow, expanded text spacing, 24px target checks, and painted keyboard-focus assertions **passed independently across all 11 public pages**. Automated axe-core WCAG A/AA scans now also pass at **320, 390 and 1280 CSS pixels** and all full browser map/route/mobile checks passed. Read [M8 acceptance evidence and remaining real assistive-technology gates](./m8-autonomous-accessibility-acceptance-2026-10-26.md). This is NOT a full manual WCAG 2.2 AA certification or 100% milestone sign-off.

Implemented engineering work October 23, 2026.

## Scope delivered
- `a11y.css` supplies visible keyboard focus cues, offscreen-until-focused skip-navigation links, motion reduction and narrow-screen touch targets.
- Eight core pages now have one explicit `main#main-content` landmark, an operable skip link, English page language, shared keyboard style and unique element IDs.
- The government accountability tab interface supports Arrow Left/Right plus Home/End; the selected tab controls keyboard focus and accessible selection state.
- The evidence analytics page provides labeled headings, a real table with numeric cells rather than color-only bars, text equivalents for each timeline bar, screen-reader status announcements, small-screen layouts and clear data-coverage uncertainty.
- `scripts/test_public_accessibility.py` performs no-dependency markup and uncertainty-label regressions.
- `scripts/smoke_accessibility.cjs` adds Chromium keyboard and viewport tests to the existing release workflow.

## Verification performed
Static repository checks confirm all eight relevant pages have matching skip links, correct main landmarks, linked accessible stylesheets, English language and no duplicate IDs. The keyboard/mobile browser regression completed successfully in [Browser release smoke #91](https://github.com/ayeemecee0/Katoptron/actions/runs/40063928164), following the documented desktop navigation overflow repair. [Validation #407](https://github.com/ayeemecee0/Katoptron/actions/runs/40063928191) also passed. These automated checks do not substitute for real assistive-technology tests.

## Independent acceptance gates
Static checks and browser smoke tests cannot establish full WCAG 2.2 AA conformance. Before calling the complete public experience accessible: conduct voice navigation and screen-reader reviews (NVDA/JAWS/VoiceOver), 200% zoom, touch interaction, color contrast checks, external Leaflet/map keyboard use, form error flows and actual mobile-browser observations. Fix any confirmed defects. Do not claim these tests passed without observation.

## October 23 release extension

- `scripts/smoke_zoom_accessibility.cjs` checks keyboard bypass, labeled community forms, and zoom-equivalent reflow at a 640 CSS-pixel viewport. The failed initial attempt used a CSS zoom property that does **not** reproduce a real browser zoom's responsive breakpoints; the corrected test passed in [Browser smoke #106](https://github.com/ayeemecee0/Katoptron/actions/runs/40066397323).
- Exact-version browser Supabase SDK pinning and public-asset credential checks run in [Validation #436](https://github.com/ayeemecee0/Katoptron/actions/runs/40066347410).
- Manual NVDA/VoiceOver, 200% browser zoom using a real browser, high-contrast modes and touch devices remain independent signoff requirements.

## October 24 keyboard map update

The interactive map is tabbable with `tabindex=0`; its ARIA description points to visible instructions explaining arrow-key pan and +/- zoom. Source records remain available in a separate accessible page for non-map users. The public footer now identifies Geoapify as the configured provider rather than inaccurately presenting the shared OSRM/Photon demos as the current routing source. Keyboard-focus and link bypass were exercised by [Browser release smoke #114](https://github.com/ayeemecee0/Katoptron/actions/runs/40108637053), which passed. This does not establish full accessibility, screen-reader interaction quality or WCAG 2.2 AA conformance.


## October 24: new automated WCAG A/AA test and remediation

The new [axe-core WCAG 2.2 acceptance workflow](../.github/workflows/audit_wcag_accessibility.yml) audits eight anonymous public screens at 390- and 1280-pixel viewport widths. Its initial test reported 13 rule findings across both widths (inline links indistinguishable except by color; main page brand's accessible name did not include visible text; and horizontally scrollable analytics table lacked keyboard access). These are now corrected in map.css, index.html and analytics.html. The final [axe test #6](https://github.com/ayeemecee0/Katoptron/actions/runs/40139222366) showed **zero violations on all 16 combinations**, and the independent [release acceptance test #1](https://github.com/ayeemecee0/Katoptron/actions/runs/40139603794) passed. The regular [Chromium browser smoke #122](https://github.com/ayeemecee0/Katoptron/actions/runs/40139222394) also passed for map, route, keyboard, mobile layouts and zoom-equivalent reflow.

Automated success is NOT a WCAG 2.2 AA certification. Signoff still needs real NVDA/VoiceOver/JAWS screen-reader tests, actual browser 200% zoom, high contrast, touch devices and tabbing through rendered Leaflet map interactions by a human tester. None of those require a paid platform, but they cannot be honestly marked complete from browser automation alone.
