# M10 · Original-government agency evidence comparison

Date: 2026-10-27. Depends on 17 individually source-page-reviewed agency dossiers / 21 documents released in #64.

## User problem

The original PDF library made source references discoverable, but readers could not inspect the same evidence topic across agencies without opening each independently. This feature adds a direct comparison at `agency-compare.html`, linked from Agency X-Ray. It supports two or three exact, independently verified agency identities and a shareable `?a=&b=&c=&topic=` URL.

## Strict evidence boundaries

- Reuses the existing original-source verifier catalogs, original PDF SHA-256, source dates and page-review references; no user-defined agencies or externally inferred entities.
- Categories on already-reviewed original-page findings are used for topical filters. A category match is **not** a statutory compliance evaluation, verified effective policy or cross-agency grade.
- Every displayed finding preserves its original statement and exact PDF page link. Source date basis explicitly distinguishes imprints, registration dates, draft dates, report periods and effective dates.
- No match means **no finding in the currently reviewed originals**, never absence of an agency policy, surveillance, sharing, equipment or legal requirement.
- Kittitas is DRAFT; Mukilteo's AGO registration date is not a policy effective date; Federal Way's two additional cameras are only proposed; Moline's signed removal obligations do not prove work was done; the Sultan wrong-publisher source is held.
- No live or inferred device coordinates, operating statuses, sharing network links, personal records, plate reads or compliance scores.
- If the Washington exact-source cross-index cannot validate, comparison fails closed to the six independently verified non-WA dossiers. Never display partially verified original pages.

## Controls and QA

`original-evidence-comparison.js` is a pure review model. Unit regressions require two or three distinct indexed agencies, verified page/source identity and SHA-256, and reject unreviewed or spoofed references. Mobile Chromium acceptance checks original links, topic filtering, deep links, 17-agency options, missing topic evidence and duplicate rejection. Source verification itself remains owned by the existing M10 original-document verifiers, and is not replaced by this presentation layer.

## Continuing M10 priorities

1. Extend original page reviews of high-value nationwide contracts, policies and monthly government reports where source and adoption status are independently establishable.
2. Add explicit agency policy change timelines only when separate published versions and their effective status are verified. No draft-to-adopted inference.
3. Link agency watch alerts and cross-agency comparisons to source-version changes without publishing unknown locations.
4. Validate accessibility, release and private-production restore gates against deployed behavior; do not equate passing static checks with complete M8/M9 assurance.
