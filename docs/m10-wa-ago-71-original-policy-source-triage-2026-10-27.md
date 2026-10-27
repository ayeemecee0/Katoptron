# M10 · Washington AGO original policy source acquisition and verified Flock-policy review

**As inspected:** October 27, 2026. **Jurisdiction:** Washington State. **Original state index:** [Washington Attorney General ALPR registration list](https://www.atg.wa.gov/ALPR), whose agency registrations are expressly self-certified, not independently checked by the AG.

## Observed source pipeline

Katoptron checked the **71 versioned PDF URLs hosted on the Attorney General's S3 policy archive** that appear in its 97-registration source snapshot. The PDFs were independently fetched using an exact URL and preserved `VersionId`, no redirects, bounded file sizes, page-count limits, and SHA-256 receipts. Each result is in [the source-receipt catalog](../data/wa-ago-original-policy-source-inspection.json).

| Outcome | Actual original PDFs |
| --- | ---: |
| Exact original PDF parsed with searchable text | **63** |
| Exact original PDF parsed as an image-based scan | **1** |
| Non-PDF response held | **1** |
| Unreadable PDF held | **6** |
| Total version-pinned state-hosted policy links | **71** |

There are also approximately 25 other registrations with policy links or references on city, third-party policy, school, public-transport, and other hosts. A link in this category does not qualify as a verified original by analogy. This acquisition count is not an inventory of installed devices or operating vendors.

**Ten original PDFs contained the text “Flock Safety”:** Arlington, Des Moines, Federal Way, Mukilteo, Normandy Park, Prosser, Sedro-Woolley, Sultan, Walla Walla, and Whitman County. Text occurrence is a **triage candidate** for individual page review; it is not a Flock installation, equipment count, agency access edge, or manufacturer confirmation. These leads remain separate from independently page-reviewed findings.

Source verification runs: [first complete batch #40589148483](https://github.com/ayeemecee0/Katoptron/actions/runs/40589148483), [rerun with source-byte metadata #40589670920](https://github.com/ayeemecee0/Katoptron/actions/runs/40589670920). The [weekly acquisition workflow](../.github/workflows/triage_wa_ago_policy_origins.yml) checks the same exact original sources, compares successful receipts against their previously pinned hashes, reports temporary holds without treating them as changed content, and fails closed on confirmed document hash or reviewed keyword page changes. No raw extracted text or individual license plate data are published.

## First independently reviewed original from the Flock-text candidate queue

[Normandy Park Police Department Policy 467](https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Normandy%20Park%20PD%20Policy.pdf?VersionId=18O0TMpqPRPGCuXKIAFSRKWNSwGnRuaY), manual imprint **June 30, 2026**, appears in the Attorney General registration snapshot dated **July 7, 2026**. It is a five-page original with exact SHA-256 `b4b26800bc0d3966b83df83abd8ccd9eeb7485e61b4057f724adad2352e4e935`.

Its original pages 1, 3, 4, and 5 have been individually visually reviewed and anchored by [the original-document verifier](../scripts/verify_wa_original_policies.py):

- **Page 1:** Policy definitions explicitly identify the Flock Safety camera system and personnel roles named Flock Safety Camera Administrators and Flock Safety Camera Users.
- **Page 3:** The agency-published policy prohibits listed uses and gives a general **21-day ALPR data retention rule**, with statutory and case-related exceptions.
- **Page 4:** Written requirements specify at-least-annual internal ALPR auditing and **two-year audit-trail retention**.
- **Page 5:** Written external data-release procedures include written requests and supervisory approval.

This verifies what the city's own submitted policy says. It **does not** prove cameras were installed, count active Flock cameras, measure actual retention, independently audit implementation, or establish real-world sharing access. The policy language references Flock, unlike the other reviewed Auburn and Black Diamond policies that do not provide a direct page-verified manufacturer reference in their published Katoptron findings.

## Remaining priority

Individually inspect the other nine Flock-term candidate documents and convert only page-supported findings, resolve the seven held state-hosted PDFs, expand safe acquisition to agency/third-party-hosted originals using per-source qualification, and continue working to obtain the current San Bruno original plus evidence of Moline's realized rather than merely announced shutdown status. The existing original-government-source protections and all map privacy limitations remain unchanged.
