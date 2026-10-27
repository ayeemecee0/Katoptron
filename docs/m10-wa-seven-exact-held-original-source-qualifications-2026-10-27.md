# M10 · Seven held Washington AGO originals: final source-quality classification

Reviewed October 27, 2026. Source: [Washington Attorney General agency ALPR registration index](https://www.atg.wa.gov/ALPR), joined to the exact original `VersionId` links in [Katoptron's state-source snapshot](../data/wa-original-agency-alpr-registrations.json).

The public [held-original diagnostics catalog](../data/wa-held-original-policy-diagnostics.json) records only source identity, bounded file SHA-256 where a complete original was obtained, structural page counts, and explicit reasons no policy facts were published. [Diagnostic CI #40594954737](https://github.com/ayeemecee0/Katoptron/actions/runs/40594954737) fingerprinted six complete original PDFs and documented the seventh source's more-than-16MB lower bound.

| Government agency listed by AGO | Source failure | Interpretation |
| --- | --- | --- |
| Kelso PD | Original 1,343,224-byte PDF opens, but both pages have empty content streams, no text/images/annotations | **Not extractable policy evidence**; retry only with a corrected publisher original |
| Kirkland PD | Exact PDF returns at least 16,000,001 bytes, above current hard cap | **Large PDF held**, not genuinely non-PDF; separate bounded streaming needed |
| Kittitas PD | 2,987,409-byte original; strict reader error but lenient parser detects 4 image-based pages | **Separate visual-review candidate**, not a text-verified policy |
| Northwest Seaport Alliance | 286,691-byte PDF triggers reader dependency errors in strict and lenient modes | Determine needed library/format dependency; **content unread** |
| Puyallup PD | 1,266,733-byte original has 2 structurally valid but entirely empty pages | **Not usable policy content** |
| Wapato PD | 2,570,228-byte original has 4 structurally valid but entirely empty pages | **Not usable policy content** |
| Yakima PD | 3,920,685-byte original opens to **738 pages**, above 160-page intake guard | Identify exact ALPR policy pages with bounded manual-specific qualification |

Each complete-byte diagnostic (all except the over-limit Kirkland file) is SHA-256-pinned in the data file. Full source bytes and policy text are not redistributed. A valid `%PDF-` header, structural pages or extracted images alone cannot establish adopted policy, equipment manufacturer, camera count, location, retention compliance or live agency sharing.

A [weekly source-drift workflow](../.github/workflows/inspect_wa_held_originals.yml) now rechecks these exact publicly state-listed versions and fails closed if the original qualification changes. Changed documents must be reviewed before their source tier is updated. These seven remain held in the general acquisition counts rather than being incorrectly promoted to seven more verified agency policies.

**Next highest-yield effort:** Independently visually review the four-page Kittitas original if an image-rendering path with original-URL provenance is available, then add per-agency qualification for oversized real manuals and valid third-party-hosted police policies, without automatically publishing camera coordinates.
