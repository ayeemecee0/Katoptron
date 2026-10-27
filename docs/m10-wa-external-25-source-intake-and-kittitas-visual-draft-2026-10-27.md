# M10 · Washington outside-archive ALPR sources and visually reviewed Kittitas draft

Source acquisition and visual review date: October 27, 2026.

## External original policy links from the Washington Attorney General register

The [state agency ALPR registration index](https://www.atg.wa.gov/ALPR) contains 97 agency registrations: 71 registrations link to exact versioned policy PDFs on the AGO's policy archive, while **25 registrations point to other original policy locations on 24 distinct URLs**. King County Sheriff's Office and Maple Valley Police Department point to an identical PowerDMS document link; this is **link aliasing, not independent evidence that two agencies use the same hardware or systems**.

The [new government-linked external source receipt catalog](../data/wa-ag-external-policy-source-inspection.json) derives from a read-only state-link scan run: [Actions #40596765566](https://github.com/ayeemecee0/Katoptron/actions/runs/40596765566). Exact links from the state snapshot are queried individually, with no redirect following, bounded response size and allowed original hosts only. No discovery crawler, camera points or agency-vendor assumptions.

| Acquired source category | Count of registration links |
| --- | ---: |
| Original PDF with machine-readable text | 3 |
| Original scanned PDF (non-text) | 1 |
| External HTML page with available source text | 10 |
| Original URL redirect held | 2 |
| URL response too large for bounded intake | 3 |
| HTTP error held | 1 |
| Empty/unusable original page held | 5 |
| **Total** | **25** |

Original retrieved PDFs include exact state-listed policies for **Enumclaw Police Department (6 pages)**, **Pasco Police Department (8 pages)** and **Sound Transit Police Department (1 page)**, plus the already separately reviewed **Black Diamond Police Department scan (7 pages)**. Their source byte hashes and page counts are pinned, but this acquisition result **does not constitute individual page verification or policy-adoption proof**. The ten HTML pages may include general policy navigation, not a specific current ALPR policy. Neither a page containing a Flock phrase nor a shared document link independently proves any Flock devices.

An [external source intake verifier](../scripts/triage_wa_ag_external_originals.py) and [recurring workflow](../.github/workflows/triage_wa_ag_external_originals.yml) distinguish changed original PDF bytes/page counts, changing HTML wrappers, transient network holds and newly reachable originals. Material changed PDF content fails closed until re-reviewed. Dynamic HTML changes remain leads for human/source-specific verification, not automatically promoted policy facts.

## Independently visually reviewed original: Kittitas Police Department DRAFT Policy 425

[Exact original linked by Attorney General (PDF)](https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Kittitas%20PD%20Policy.pdf?VersionId=kFMGZo4zqUbzsCu9cSrAdpkD1Ij.PutG)

The original Kittitas PDF had failed strict parsing but opened under a lenient parser as four image-only pages. A separate raster renderer checked original SHA-256 `8b6bb93e69589f7459cb4bc5adbd7991043e59687fa1b91180c149e5fc19368f` and produced all four page images. The page images were **individually inspected visually**, rather than interpreting provisional OCR text as independently verified. Original receipt, pixel hashes and rendered QA pages are in [Actions run #40596859008](https://github.com/ayeemecee0/Katoptron/actions/runs/40596859008) (time-limited artifact).

**Every original page is prominently marked `***DRAFT***`**, with a manual imprint of June 30, 2026. Consequently, the correct verified finding is an **original-page-reviewed draft**, not an effective, adopted or implemented policy.

- **Original page 1:** Policy 425 applies to automated license plate reader records. In section 425.2, training refers to *Flock online training modules*. This is written draft training language, **not evidence Flock cameras were installed**.
- **Original page 2:** Section 425.4 gives a general **21-day retention limit** with listed exceptions and section 425.3.1 sets out prohibited-use categories. This is proposed written language, **not verified retention or system operation**.
- **Original page 3:** Section 425.5 describes annual audits and two-year audit-trail retention; section 425.7 introduces sharing procedures. These are drafted obligations, **not an independent compliance audit or confirmed actual data sharing**.
- **Original page 4:** Completes source-draft procedures governing request identification, purpose, authorization and file retention; no external process implementation is proven.

The typed [Kittitas original-image review manifest](../data/verified-wa-kittitas-scanned-draft-review.json) pins the four page-image SHA-256 digests and source URL. Client-side validation blocks changing `draft_not_proven_adopted` into an approved policy, or injecting device counts, operational status or GPS coordinates. The public [Washington registration page](../wa-alpr-registrations.html) visibly labels it as a draft with exact original-page links.

These additions improve original evidence coverage without falsely claiming more than the records prove. Kittitas draft review is **not counted as an adopted policy or confirmed Flock installation**.

## Next acquisition priorities

1. Independently review the most relevant newly reachable PDFs (Pasco, Enumclaw, Sound Transit) for dated policy facts without arbitrarily attributing them to Flock.
2. Qualify the eleven held external URLs individually, preserving redirects and large manual constraints.
3. Resolve the original-document adoption status for Kittitas; do not infer adoption from registration alone.
4. Extend the bounded source-acquisition and dated-finding pipeline to high-value government accountability records outside Washington.
