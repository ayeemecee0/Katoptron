# M10 · Diagnosing seven held version-pinned Washington AGO PDF originals

Inspected October 27, 2026. Original source list: [Washington AGO registry](https://www.atg.wa.gov/ALPR), where agencies have self-certified their ALPR registration. The [bound source receipt catalog](../data/wa-ago-original-policy-source-inspection.json) presently keeps all seven in *held* state; no facts from these sources have been published as reviewed originals.

Original bounded replay: [GitHub Actions #40593424542](https://github.com/ayeemecee0/Katoptron/actions/runs/40593424542) via [read-only diagnostics](../scripts/inspect_wa_unreadable_originals.py). Source URLs are exact versioned AGO-index links, no redirects; no raw personal records or full policy text printed.

| AGO-listed agency | Original-source diagnostic | Appropriate next change |
| --- | --- | --- |
| Kelso Police Department | PDF is 1,343,224 bytes, opens strictly, **2 pages**, unencrypted. Original general triage still held. | Isolate the failure after page opening (possibly image decoding); verify readable text/embedded image type before upgrading |
| Kirkland Police Department | PDF stream exceeded the present **8 MB cap**; source is PDF, not truly non-PDF. | Source-specific size cap with disk streaming and guarded page count; do not simply disable the safety limit |
| Kittitas Police Department | PDF is 2,987,409 bytes; strict reader raises `PdfReadError`, lenient reader obtains **4 pages**, unencrypted. | Separate lenient-recovered provenance tier with exact byte hash, independent page review and security checks |
| Northwest Seaport Alliance | PDF is 286,691 bytes; both strict and lenient readers raise `DependencyError`. | Identify missing PDF format or crypto dependency before considering a source as parseable |
| Puyallup Police Department | PDF is 1,266,733 bytes, strict reader opens **2 pages**, unencrypted. | Diagnose page iteration / embedded images and then review original source |
| Wapato Police Department | PDF is 2,570,228 bytes, strict reader opens **4 pages**, unencrypted. | Diagnose page iteration / embedded images and then review original source |
| Yakima Police Department | PDF is 3,920,685 bytes and **738 pages**, exceeding current 160-page source cap. | Original-only targeted chapter extraction with verified page boundaries; do not label full manual reviewed |

This narrows the backlog. The earlier "six unreadable PDFs plus one non-PDF" status reflected intake failure categories, not the true nature of all source bytes. **Do not automatically promote** any held policy, source hash or agency Flock association solely because a different parser can open it.

## Remaining M10 source work

- Split parser/dependency errors, giant-manual chapter discovery, oversized PDFs and scanned-image handling into explicitly bounded qualifications.
- Keep ten Washington Flock phrase candidates distinct: **Normandy Park plus eight new individually reviewed source documents, and one Sultan attribution hold**.
- Do not misattribute the Sultan-linked `Snohomish County Sheriff's Office ALPR Training` to Sultan Police Department. Its title and handling markings require extra source/applicability review.
- Continue to resolve San Bruno's inaccessible current policy and Moline's deactivation completion independently. Signed contract and future announcement are not completion proof.
