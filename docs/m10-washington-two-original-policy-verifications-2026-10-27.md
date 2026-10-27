# M10: individually reviewed Washington AGO-linked original policy texts

Source review date: October 27, 2026.

Washington's Attorney General publicly lists agency-submitted ALPR registrations and linked policies, **without independently verifying agency attestations**. Katoptron's separate [two-record verified policy catalog](../data/verified-wa-agency-policies.json) is a first, narrow content review of *policy text*, not a legal compliance audit.

| Source and policy imprint | Review method | Substantive, page-limited observations |
| --- | --- | --- |
| [Auburn Police Department Policy 425](https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Auburn%20PD%20ALPR%20Policy.pdf?VersionId=bPOrBG6TYUmkpHt6dVALLEcyhx2utLnH), manual imprint July 2, 2026 | Eight-page original text PDF, byte SHA-256 `484830933e46300a5471d3fccc4354f33ae1b683bc8401fa938b8a4d3f53863f`; original pages 2, 5, 6, 7 examined and checked by page-text anchors | Default 21-day retention with exceptions; limited external sharing provisions; annual internal audits and public reporting as written requirements, not verified outcomes |
| [Black Diamond Police Department Policy 434](https://blackdiamondwa.gov/DocumentCenter/View/4324/BDPD-ALPR-Policy), manual imprint June 23, 2026 | Seven-page city-hosted raster original; original SHA-256 `8ccf182125bf61bc624be72cb389f5ce218d36cf60f9db62d5ba8d58418f2446`; page images 1 and 4 visually reviewed and verified by exact hash/page receipt. No OCR anchors fabricated | Section 434.6 specifies default 21-day deletion with listed exceptions; document assigns registration/certification duties to commander. No conclusion about actual retention configuration |

Initial read-only original inspection: [GitHub Actions #40584493194](https://github.com/ayeemecee0/Katoptron/actions/runs/40584493194).

New recurring [policy verifier](../scripts/verify_wa_original_policies.py) requires exact source URL as submitted in [state registry snapshot](../data/wa-original-agency-alpr-registrations.json), immutable SHA-256 original, PDF page-count guard, and the appropriately selected text or image integrity review. If source bytes, approved link, or reviewed page changes, **verification fails closed** and findings must be individually re-reviewed.

The [Washington public registration page](../wa-alpr-registrations.html) now includes the two source-reviewed policy summaries and direct page links, and agency listings for Auburn/Black Diamond link to their original-policy analysis.

**Limits:** These records do not establish camera inventory, Flock hardware, individual plate movements, live agency access relationships, deployment/operational status or compliance. A Lexipol date imprint is not proof of the policy's legal adoption date. Washington's future statutory reporting deadlines do not establish present violations. Unreviewed policies in the 97-registration snapshot remain linked metadata only.

## Remaining priority evidence gaps

1. The city-linked [San Bruno current ALPR policy](https://www.sanbruno.ca.gov/DocumentCenter/View/9522/San-Bruno-PD---ALPR-Policy) redirects in the strict original-source verifier; a historical 2023 manual is not an acceptable stand-in for current terms. Hold the new PDF source as unverified until accessible under authoritative government origin.
2. Moline's September 2026 signed pause and city announcement establish a **planned** operational shutdown, not completed deactivation or removal. Obtain a subsequent original completion record before publishing a concluded status.
3. Review more Washington policies *individually*, including vendor identity only if the original actually specifies the manufacturer. Do not transform universal ALPR registrations into Flock installations.
