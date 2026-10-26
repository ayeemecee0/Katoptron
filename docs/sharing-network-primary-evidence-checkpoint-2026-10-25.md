# Sharing-network original-source verification checkpoint
Date: 2026-10-25 America/Los_Angeles. CI jobs use UTC.

## Separate evidence tiers

The licensed EyesOnFlock-derived secondary graph contains 490,214 reported directed links from an October 19, 2026 snapshot. It is research-grade source attribution, not independent current proof of 490,214 permissions, physical cameras, reciprocal access, or actual searches.

The new original-publisher evidence tier contains 195 outward recipient names reproduced from six original government and vendor portal pages. Exactly 184 of those publisher labels uniquely matched a canonical agency name; 11 remain explicitly unresolved. Matching an agency ID never assumes a reversed sharing link.

Sources:
- City of Elk Grove: https://elkgrove.gov/traffic/automated-license-plate-readers-alpr — 65 names on a government original Flock-specific outward access list.
- City of Woodland: https://www.cityofwoodland.gov/1704/Automated-License-Plate-Readers-ALPR — 69 original-government outward names captured as an explicitly partial excerpt. Additional names are visible on its original page but not silently assumed in the evidence table.
- Mill Valley Flock vendor portal: https://transparency.flocksafety.com/mill-valley-ca-pd — 6 named access recipients.
- Los Altos Flock vendor portal: https://transparency.flocksafety.com/los-altos-ca-pd — 39 names. Two ambiguously line-wrapped name fragments deliberately not promoted to separate agencies.
- Snohomish County Sheriff Flock portal: https://transparency.flocksafety.com/snohomish-county-wa-so- — 10 names.
- Las Vegas DPS Flock portal: https://transparency.flocksafety.com/city-of-las-vegas-nv-department-of-public-safety — 6 names.

These are dated observations of what the original publisher listed, NOT independently confirmed live active permission. Neither a named source grant nor a network graph can establish whether an officer searched anyone.

## Honest automated freshness test

The first protected GitHub original-source recheck returned HTTP 403 for five original publishers (Elk Grove and four Flock portals). Woodland returned HTTP 200 but not the published sharing-list section in HTML exposed to the automated client. Therefore zero of six publishers passed a complete automatic fresh-source recheck. HTTP denial, unavailable content and an incomplete page are NEVER converted to no-sharing or a revoked grant. The site shows this recheck outcome, retains original historical source dates, and does not promote links to verified currently active.

## Shipped engineering

- SQL migrations 125-127: RLS public read-only original publisher source and recipient tables, source-excerpt scope, exact unique agency match crosswalk, RLS-invoker evidence views, bounded source recheck audit and health view.
- Source collection seed: migration 126, original publisher names linked to their true URL, publisher category and date, no camera geocodes.
- Source health process: scripts/recheck_original_sharing_sources.py and weekly GitHub Action source rechecks, strict source-host allowlist and HTTPS-only fetch, digest, matched-name count, safe blocked/unavailable classification. No inferred access revocation.
- Frontend: agency-original-sharing.js, sharing-explorer.html, agency-xray.html, agency-brief.html. Original government/Flock source links and exact outward and inward recipients remain separate from the larger secondary-source graph, with availability and confidence notices.
- Acceptance: scripts/test_original_sharing_provenance.sql, scripts/test_original_sharing_evidence.cjs, scripts/test_recheck_original_sharing_sources.py, plus live browser source/agency checks.

## What prevents full 100% independent verification

Only 195 original publisher-named observations are recorded versus 490,214 original-source-derived secondary reported relationships (about 0.04% by simple counts). Most agency sharing sources are not directly and currently retrievable through our open automated clients. Some agencies publish incomplete recipient lists; others require original agency-side SharedNetworks.csv exports or public-records responses. A source dated July or October 2026 cannot establish permissions currently enabled or actual historical searches. Additional original government/vendor time-stamped exports and exact directed agency identity proof are needed before upgrading another relationship.

Do not report 490,214 independently authenticated, currently active grants. Network exploration engineering may be mature while independent first-party coverage remains low. Source provenance and uncertainty are maintained per relationship.
