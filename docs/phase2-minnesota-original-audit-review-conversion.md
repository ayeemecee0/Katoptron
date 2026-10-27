# Minnesota Flock-named audit conversion — original PDF receipts and reviewed pages

**October 27, 2026 current coverage:** This document preserves earlier October 26 review snapshots for provenance. The current pinned manifest now includes **22** original auditor reports, including page-level checks for **all 16 of 16 state titles explicitly mentioning Flock**. The two previously machine-only West Saint Paul and Wyoming originals have been reviewed. See the [current source-linked historical comparison and five new original audit receipts](./m10-cross-period-original-audit-history-2026-10-27.md). The original machine scanner and current public registry remain separate from independently reviewed content.

**Development snapshot:** October 26, 2026 (America/Los_Angeles). This release **does not** independently certify a police department's legal compliance or current camera inventory.

## What is newly useful

- The official Minnesota state legislative ALPR audit registry identifies **16** reports whose titles explicitly name Flock (of **137** original state-indexed reports). Earlier counts refer to *index entries*, not audited PDF text.
- All 16 Flock-titled PDFs were fetched directly from the original `www.lrl.mn.gov/docs/YYYY/mandated/NNNNNN.pdf` archive, each with **five pages** and extractable text, and assigned a **SHA-256 byte-level receipt**. This is automatic *machine-only provenance/triage*: the remaining reports are not independently reviewed for detailed claims.
- Machine receipts (hash, byte count, page count, read-only Boolean topic flags) live in the RLS-protected `flock_private_mn_flock_audit_pdf_receipts` table. Service-role-only INSERT/UPDATE, no anon or authenticated access, no DELETE; no prose, plate reads, current camera positions, signature claims, model-generated findings, or names of individual drivers are saved.
- A free GitHub Actions workflow checks the official registry and original PDFs weekly and writes only private receipts on `main`. If **any** archive file is missing or unreadable, the machine scan fails closed. An outage is not proof an audit was withdrawn. Previously reviewed documents have a **separate**, stricter, pinned digest and source-page verifier.

## Newly page-reviewed source reports

Two original published reports were inspected on their relevant original pages and then pinned to hashes from the exact downloaded source PDFs.

### Stillwater Police Department — September 6, 2026
- [Official five-page Minnesota report](https://www.lrl.mn.gov/docs/2026/mandated/261351.pdf), SHA-256 `6315eeb3b9061ff97098c850a712a7509a20d898724cbff08a96da8576bed1f9`.
- **Page 2:** Independent Minnesota Security Consortium auditor says the agency had **17 stationary Flock ALPR units at the time of its audit** and reports manufacturer-default **30-day Flock retention**, citing a Flock Vehicle Reads report. These are historical auditor statements, not present-day hardware counts or independently tested settings.
- **Page 3:** The auditor says its Flock console did not show out-of-state sharing in the Shared Network section at the time. This is *not* proof no other agencies ever accessed its records, nor an exhaustive recipient list.
- Source period: August 1, 2024–July 31, 2026. No new camera coordinates or network-sharing edges are created.

### Hennepin County Sheriff's Office — October 21, 2025
- [Official five-page Minnesota report](https://www.lrl.mn.gov/docs/2025/mandated/251683.pdf), SHA-256 `e131a79aaf5c59a1477e30a47edbdf2b15ed9226c274a4e446e427b0383dfc70`.
- **Page 2:** Auditor says **four active stationary Flock ALPR units** within the county and describes **30-day manufacturer-default retention** confirmed during its review.
- **Page 3:** Auditor describes interagency ALPR requests being made/reviewed through agency command. This statement does **not** identify current recipients or prove ongoing network permissions.
- Source period: June 1, 2023–July 31, 2025. No current compliance rating is implied.

The already-reviewed Shakopee June 2026 audit remains its separate source-level record. Together the previous curated manifest contained **three** original page-reviewed independent audit reports, compared with one before this release. They are linked from the [state archive library](../mn-alpr-audits.html) and assigned exact original-source identity dossier links in the [Accountability Engine](../agency-audit.html). Source-only dossiers include their exact reviewed original record and show remaining civic/contract gaps as **unknown**, not inferred violations or equipment absence.

## Why report trends are not automatically contradictions

Stillwater's 17 units and Hennepin's four units describe **different agencies in different years**. They are not a year-over-year difference and should never become a manufacturer migration or a policy contradiction. To establish a historical change for one operator, Katoptron needs two independently page-reviewed, source-dated, same-agency reports about the same measurement and unit, plus attention to collection dates. Existing audit PDFs may contain historical statements; they cannot substitute for live console access or audit logs.


### Three additional original audit reviews — October 26, 2026

The following original state-hosted five-page audit summaries were checked on PDF pages 2–3 and pinned to SHA-256 hashes. They have separate exact-agency dossier keys and do not establish current equipment, unauthorized sharing, or legal wrongdoing.

- **Richfield Police Department (May 21, 2026)** — [Original audit](https://www.lrl.mn.gov/docs/2026/mandated/260900.pdf), SHA-256 `d13ceb556b08015e2ca751734eff29349eb8f9fa9a44866cc560c02ffe24ee10`. P.2: auditor-reported **8 stationary Flock ALPR units** at audit time and **30-day manufacturer-default data retention**. P.3: auditor sampled March 2026 requests documented with agency and justification. Historic sampling, not a current recipient list.
- **Woodbury Public Safety (Feb 5, 2026)** — [Original audit](https://www.lrl.mn.gov/docs/2026/mandated/260248.pdf), SHA-256 `523876118f3e7da5b2754bd6695e7386e3967874543710a2b645834955723852`. P.2: auditor-reported **17 active stationary Flock ALPR units and no mobile Flock units**, plus **default 30-day retention**. P.3: describes documented interagency requests and case-number justification, not a permission graph.
- **Brooklyn Center Police Department (Oct 28, 2025)** — [Original audit](https://www.lrl.mn.gov/docs/2025/mandated/251737.pdf), SHA-256 `6318fee178da621398a0a0c977b9852991638d707dbf39f7d0df5e9da6b1e28f`. P.2: auditor reported **9 active stationary ALPR units and no Flock mobile units** in its review of a Flock ALPR system, with **default 30-day retention**. P.3: documented interagency requests; no current sharing partner identities established.

**Previous reviewed coverage: 5/16 Flock-named audit reports, plus Shakopee's independently reviewed report (whose official archive title does not name Flock).** All 16 Flock-named documents have machine fingerprints, but prior to the next expansion only five had page-reviewed citations. Other vendor-unspecified and non-Flock titles remain metadata only. The count must not be treated as 6 new agency live-camera inventories or 6 completed surveillance audits by Katoptron.


## Additional reviewed audit reports — October 26, 2026

Nine additional original public auditor executive summaries were examined on their named original state-archive pages. Each has a fixed original PDF SHA-256 digest, strict page-text anchor verifier, source date, historical inventory observation, source-attributed 30-day default retention observation and a separate policy recommendation or sampled sharing-process observation. Every finding is historical, attributed to its original auditor, and **is not a present-day camera location, sharing permission or Katoptron legal determination**.

| Agency | Source date | Historical auditor-reported devices | Additional observation (original PDF page) |
|---|---|---|---|
| [Champlin Police Department](https://www.lrl.mn.gov/docs/2025/mandated/251685.pdf) | 2025-10-22 | six active stationary/flex Flock ALPR devices and no mobile Flock units (p.2) | Breach-notification policy recommendation (p.4) |
| [Corcoran Police Department](https://www.lrl.mn.gov/docs/2026/mandated/261008.pdf) | 2026-05-30 | nine active stationary Flock ALPR units and no squad-mounted mobile units (p.2) | Historical interagency sharing-request documentation (p.3) |
| [Edina Police Department](https://www.lrl.mn.gov/docs/2025/mandated/251619.pdf) | 2025-10-15 | 18 active stationary Flock ALPR units and no mobile Flock units (p.2) | Historical interagency sharing-request documentation (p.3) |
| [Hopkins Police Department](https://www.lrl.mn.gov/docs/2026/mandated/260144.pdf) | 2026-01-20 | 14 stationary Flock ALPR devices, comprising 13 fixed and one flex, and no mobile Flock units (p.2) | Historical interagency sharing-request documentation (p.3) |
| [Minnetrista Police Department](https://www.lrl.mn.gov/docs/2026/mandated/260987.pdf) | 2026-06-08 | four stationary Flock ALPR units during the audited period (p.2) | Historical interagency sharing-request documentation (p.3) |
| [Orono Police Department](https://www.lrl.mn.gov/docs/2025/mandated/251707.pdf) | 2025-10-29 | three active stationary/flex ALPR devices and no squad-mobile Flock units in its Flock-system audit (p.2) | Breach-notification policy recommendation (p.4) |
| [Robbinsdale Police Department](https://www.lrl.mn.gov/docs/2025/mandated/251675.pdf) | 2025-10-23 | two active stationary Flock ALPR units and no mobile Flock units (p.2) | Historical interagency sharing-request documentation (p.3) |
| [South Lake Minnetonka Police Department](https://www.lrl.mn.gov/docs/2026/mandated/260679.pdf) | 2026-04-10 | four stationary Flock ALPR units and no mobile Flock units (p.2) | Historical interagency sharing-request documentation (p.3) |
| [University of Minnesota Police Department](https://www.lrl.mn.gov/docs/2025/mandated/251639.pdf) | 2025-10-15 | ten active stationary ALPR units in its Flock-system audit, with no mobile Flock units reported (p.2) | Historical interagency sharing-request documentation (p.3) |

**October 26, 2026 checkpoint (superseded on October 27): independently page-reviewed Flock-named audit titles were 14 of 16 (87.5%).** The catalog separately also includes Shakopee, whose title does not mention Flock, so **15 total reports have curated original-source review entries**. The two remaining Flock-titled reports (West Saint Paul and Wyoming) remain *machine-fingerprinted-only*, because their original PDF pages were not independently accessible for review in this pass. They are not approved for source-specific public findings. Do not count 15/16 or misclassify Shakopee's title. All 16 continue to have private ingestion-level PDF hash receipts.

The automated source verifier must fetch and validate all 15 reviewed PDFs and match exact relevant page strings before publication. Any missing or revised original source fails closed. It does not independently confirm statutory compliance or current manufacturer identity.

## Testing and release

- `python -m unittest discover -s scripts -p 'test_fingerprint_mn_flock_audits.py' -v`
- `python -m unittest discover -s scripts -p 'test_verify_independent_audit_source.py' -v`
- `python scripts/fingerprint_mn_flock_audits.py --preflight` for source-only dry-run, zero DB writes.
- `.github/workflows/fingerprint_mn_flock_audits.yml` for all Flock-title byte fingerprints, optionally recurring main writes.
- `.github/workflows/verify_original_independent_audits.yml` for the 15 specifically reviewed PDF fingerprints and page assertions.
- `node scripts/smoke_agency_audit.cjs` validates exact-identity dossiers and original page receipts.
- `node scripts/smoke_mn_alpr_audit_registry.cjs` checks state archive search and title-level identity labels.

**Next:** Independently review West Saint Paul and Wyoming when original PDFs are accessible; then prioritize comparable *same-agency* multi-period audits rather than treating two agencies as a time series. When comparable observations exist, only then generate source-dated change timelines; never a violation score.
