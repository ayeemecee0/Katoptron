# M10 · Agency X-Ray expands to 17 exact original-source publishers

Reviewed original governmental source integration: October 27, 2026.

The existing six-publisher [Agency X-Ray original-source interface](../agency-xray.html) now adds **11 independent Washington police and sheriff agency original-policy/bulletin sources**, yielding **17 exactly identified source publishers and 21 individually page-reviewed original documents**.

## Eleven newly searchable Washington agency records

| Exact Washington government publisher | Original document type | Source-date meaning and limitation |
| --- | --- | --- |
| Arlington Police Department | Original ALPR policy | Refers to multiple vendors; not independent evidence of installed Flock equipment |
| Des Moines Police Department | Original agency policy | Flock query accountability instructions, not verified searches or compliance |
| Federal Way Police Department | Dated training bulletin | Historical one Flock location with four fixed cameras **at the bulletin date**; two cameras for another site **proposed**, not installed |
| Mukilteo Police Department | Original policy | Has no independently established original manual imprint date; displayed AGO registration date is **not** policy effective date |
| Prosser Police Department | Original policy | Describes intended transparency publication, not independently verified portal operation |
| Sedro-Woolley Police Department | Original policy | Policy states contradictory retention text “thirty (21) days”; this is a document discrepancy, not verified runtime deletion behavior |
| Walla Walla Police Department | Original policy | Written reporting and transparency commitments do not prove delivery |
| Whitman County Sheriff's Office | Original Flock-specific policy | Written equipment/retention/sharing rules, not separately measured actual deployment |
| Auburn Police Department | Original agency-published policy | Strict original policy text and state-linked version, no independent live device status |
| Black Diamond Police Department | Original agency-published scanned policy | Visually reviewed page evidence, not independent Flock manufacturer/active-camera verification |
| Normandy Park Police Department | Original agency-published policy | Source-specific references do not establish today's equipment or sharing state |

Every document retains its precise original government or AGO-versioned PDF URL, SHA-256, original reviewed pages and statement type. The first eight documents are independently verified through the typed [WA Flock-text review](../wa-reviewed-flock-sources.js) and the AGO-linked [version-pinned source receipts](../data/wa-ago-original-policy-source-inspection.json); the final three use the separate [original state-policy validator](../wa-original-policies.js).

**Sultan Police Department is deliberately not shown as a reviewed original-policy agency.** The original state-linked file instead identifies itself as training from a different publisher, Snohomish County Sheriff's Office. A registration listing by itself cannot resolve attribution or authorize publication of sensitive training text.

## Operational product change

Agency X-Ray provides a searchable agency-source section even if a locality has no individually geolocated cameras. The 17 agency source identities are **not appended to Flock portal identities, sharing graph nodes, verified camera coordinates or locality-assessed source totals** based solely on a similar city name.

New [Washington adapter](../wa-original-agency-dossiers.js) validates the original eight Flock-text PDFs and three additional agency ALPR policies using their previously published source validators. It then checks collisions with the already verified six-agency dossier index. A missing or malformed Washington source leaves the six existing reviewed dossiers intact with a visible warning instead of silently publishing guessed facts.

The public interface distinguishes:

- source/manual imprint vs AGO registration (no presumption of policy adoption);
- Federal Way's historical equipment statement vs a proposed future installation;
- document requirements vs audited actual compliance;
- agency-specific reviewed originals vs the still-unfinished 50-state and D.C. original government research queue.

[Negative source tests](../scripts/test_wa_original_agency_dossiers.cjs) reject forged URLs, camera-current-status fields, changed page anchors, missing originals and source misattribution. [Mobile Chromium coverage](../scripts/smoke_verified_agency_dossiers.cjs) now checks exact Federal Way, Mukilteo, Black Diamond and Sultan statuses, plus original six-agent searches and deep links.

## Next evidence bottleneck

The integrated agency dossiers are now more useful to researchers and journalists, but **17 agencies are not an adequate nationwide verified Flock agency census**. The next acquisition effort should convert the most relevant source-linked government files in the remaining states into individually original-page-reviewed government records with exact agency identification, and connect repeated dated records to true policy/contract change comparisons without misrepresenting signed contract coverage as camera coverage.
