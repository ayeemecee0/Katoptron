# M10 · Original city operating status statements
Reviewed October 27, 2026. These are two verified original **municipal publications**, not vendor telemetry, complete equipment inventories or independent technical audits.

| City / original source | Dated official statement | Strict conclusion |
| --- | --- | --- |
| [Moline, Illinois Police transparency statement](https://www.moline.il.us/1955/License-Plate-Readers), September 15, 2026 | A planned pause of the nine-camera fixed Flock ALPR system, expected full deactivation in about fourteen days and removal later. Also see [the separate city-hosted signed contract pause](https://moline.il.us/DocumentCenter/View/16700/Flock-Safety-Contract-Pause-September-2026). | **Planned deactivation only.** No original completion statement, post-shutdown machine log, or physical removal record was verified. Do not infer that the deadline's passage proved completion or that the cameras are still active. |
| [City of Mill Valley, California statement](https://www.cityofmillvalley.gov/m/newsflash/home/detail/1639), published October 19, 2026 | The city states that its Flock ALPR and live-feed cameras have **been disabled since September 9, 2026** and cites concerns about revised vendor terms and enforceable sharing/privacy safeguards. It reports its earlier seven-day ALPR retention limit. | **City-reported disablement as of October 19.** Stronger than a future plan because the official statement is retrospective, but still not an independent forensic equipment inspection or guarantee of indefinite nonoperation. |

## Source provenance

Both original municipal pages were fetched independently using exact published HTTPS URLs, no redirect, capped body size and dated source-text anchors. Initial independent source inspection [GitHub Actions #40585869956](https://github.com/ayeemecee0/Katoptron/actions/runs/40585869956) produced:

- Moline original HTML SHA-256 `7dadb1a974f8021faa4e196ffb8b0a19d6641202bf47089cff41f7dc60fc3048` (112,024 bytes).
- Mill Valley original HTML SHA-256 `6cb358755f107c9e424ff2f352932bf22513ed0b98145d5012e7a5dff8f4c20b` (103,714 bytes).

The baseline HTML byte hashes are retained as *review-time receipts*, rather than blindly failing on unrelated menu/site changes. The recurring [original-city source checker](../scripts/verify_city_alpr_operational_statements.py) fails closed if the material dated source text disappears or is changed, tracks whether the full HTML changed, and always binds the status to the exact municipal source and original publication date. Changes in the underlying source **do not automatically promote Moline to 'off' or Mill Valley to 'on'**. The public [national evidence library](../national-audits.html) displays the two statements separately, with distinctions among planned changes, agency-reported completed actions, and uncertain present status.

No personal license plate reads, camera GPS coordinates, publisher-unverified facts, network sharing edges, paid services, Supabase migrations or current operational claims were produced.
