# M10 · Original government policy/contract evidence and Washington statewide ALPR register
**Source snapshot and review date: 2026-10-27.**

## Eight of nine original government document candidates are reviewed

Following the six-state source-watch pilot, the source watch identified **nine** unreviewed links from original California, Texas and Wisconsin government publishers. A bounded first-party source inspector independently fetched **eight original PDFs**, confirmed each SHA-256 and selected original pages, and left **one blocked San Bruno PD policy URL** held because the publisher repeatedly redirected the exact link.

The new separately classified, strictly page-pinned catalog is [data/verified-national-government-documents.json](../data/verified-national-government-documents.json), with weekly [byte/page source verifier](../.github/workflows/verify_national_primary_documents.yml). Different source types must never be collapsed: original government oversight, older auditor slides, a grand jury press advisory, an agency-authored monthly aggregate, published policy version, *unadopted draft*, vendor order form with unknown execution date, and a *nonbinding commission recommendation*.

### Key concrete, dated findings

| Original source | Verified original page and finding | Evidence limit |
|---|---|---|
| [Green Bay monthly ALPR report, compiled October 1, 2026](https://www.greenbaywi.gov/DocumentCenter/View/18823/Green-Bay-Police-Department-Monthly-ALPR-Report-September-2026#page=1) | Public police report states **443,664 unique plate reads, 9,534 hotlist hits, 522 user search sessions** over the previous 30 days. It lists **four organizations** with data-access permission in that snapshot. | Aggregated agency self-report. No personal plate IDs collected. Four named access recipients are a dated list, **not proof of current, reciprocal or actually used sharing links**. |
| [Green Bay published Policy 424, May 2026](https://www.greenbaywi.gov/DocumentCenter/View/18791/Policy-424-Automated-License-Plate-Readers-ALPR-May-2026#page=2) | Published policy text specifies up to **30 days'** retention of ordinary ALPR data in that system, with exceptions for separately incorporated case files. | Not proof the system was configured accordingly, or that this remains the effective policy now. |
| [Green Bay September 2026 policy revision marked **DRAFT**](https://www.greenbaywi.gov/DocumentCenter/View/19136/DRAFTED-REVISION---Policy-424-Automated-License-Plate-Readers-ALPR-September-2026#page=4) | **Draft** proposes **seven-day** ordinary plate-read retention (p.4), further use restrictions (p.2), and at least **1%** of prior-month searches in monthly audit samples (p.6). | This is a **policy proposal**, NOT an adopted 7-day setting, a policy violation, or a demonstrated auditing practice. Comparison with May's 30 days is **published versus draft**, never a confirmed policy enactment. |
| [Green Bay published Flock order form](https://www.greenbaywi.gov/DocumentCenter/View/19138/Flock-Safety-WI---Green-Bay-PD---DFR-and-ALPR-Law-Enforcement-Agreement-2025#page=2) | Form states **42 LPR units**, **60-month** initial term, **30-day** retention, and a five-year billing schedule totaling **$1,392,000** before tax (p.4). | Published proposed/ordered terms, not proof of successful execution, actual payment, present camera functionality or individual locations. |
| [Austin Office of Police Oversight, March 31, 2023](https://services.austintexas.gov/edims/document.cfm?id=452776#page=1) | Independent municipal oversight memo expressed concerns about the then-proposed APD ALPR policy and community meetings. | A critique of a **2023 proposal**. Does not establish later operational wrongdoing or actual policy adoption. |
| [Austin Public Safety Commission vote, June 2, 2025](https://services.austintexas.gov/edims/document.cfm?id=452847#page=3) | Commission voted **6–0 to recommend** an immediate ALPR program halt and more thorough data-sharing review. | **Advisory recommendation**, not an order by City Council and not proof that APD shut down its program. |
| [Austin auditor presentation, May 2025](https://services.austintexas.gov/edims/document.cfm?id=452702#page=5) | Auditor's slides summarize earlier audits, metrics and contractual risks. | A **derivative presentation**, not a newly executed independent audit. |
| [San Mateo Civil Grand Jury press release, August 3, 2026](https://sanmateo.courts.ca.gov/system/files/grand-jury/alpr-press-release.pdf#page=1) | Official announcement summarizes the separately reviewed San Mateo County grand jury report. | A **press summary**, not another independent investigation. |

**Held:** [San Bruno public ALPR policy candidate](https://www.sanbruno.ca.gov/DocumentCenter/View/9522/San-Bruno-PD---ALPR-Policy) is not included in source-pinned findings because the exact URL led to redirects; it is not silently presumed deleted or treated as verified.

No new camera pin, person-level ALPR record, 2026 live device count or automatic directed sharing network fact was produced from this batch.

## Expansion from six states to eight

The weekly [national source monitor](../.github/workflows/scan_national_government_audit_sources.yml) is extended from **10 registered original URLs in six states** to **14 officially registered original source URLs in eight states** (CA, WI, VA, TX, DE, OR, IL, WA). Illinois adds City of Moline, Naperville and Darien official city pages. Washington adds the **Attorney General's statewide ALPR registration list**.

A monitoring URL can be registered before it becomes accessible through the strict no-redirect fetcher. At the first Illinois/WA source check, **Naperville's city page was unavailable to the automated client** and was marked for recheck, not classified as withdrawn. Moline and Darien originals were accessible. The national source queue includes both original policy/audit documents and other government source leads, not all Flock audit findings.

## Washington statewide public agency registration index: 97 entries

The [Washington Attorney General original public ALPR agency registry](https://www.atg.wa.gov/ALPR) was independently checked with an HTML table parser. The first official state snapshot, [data/wa-original-agency-alpr-registrations.json](../data/wa-original-agency-alpr-registrations.json), captured October 27, 2026, has:

- **97** distinct agency registration entries, including police, sheriff, universities and other ALPR categories.
- **96** entries linking to policies from the official AG registration page; many policies reside in a public AWS S3 bucket controlled through the original AG publication workflow.
- **One** source-listed submission date whose format was not confidently normalized; the original text is retained rather than inventing a date.
- Original state page SHA-256 receipt `e0302903b8ad9256f9637b1b33eb1e49f0795cf6ae351cf664193f595d137a05`.

The Attorney General **explicitly states that it has not independently verified the certifications made by agency heads**. The public [searchable Washington registry view](../wa-alpr-registrations.html) repeats that disclaimer prominently; it does not claim any particular system is manufactured by Flock, gives no camera coordinates and never infers compliance or live agency operation. Individual state-linked policies have not been separately read/verified merely because a link exists in the official table.

The [weekly read-only state register workflow](../.github/workflows/build_wa_ag_alpr_registry.yml) re-acquires the original table, checks provenance and emits bounded snapshots. It compares registrations and policy URLs to the published snapshot and reports additions, departures and metadata changes without conflating a missing row with actual ALPR shutdown, Flock removal, or changing manufacturer. The public snapshot has its capture date; new weekly artifacts do **not** silently overwrite it or claim always-live state.

## Engineering and review gates

- Original eight-file source inspection [GitHub Action #40570225649](https://github.com/ayeemecee0/Katoptron/actions/runs/40570225649).
- Eight document SHA-256 / independent original page anchor [verifier](../scripts/verify_national_primary_documents.py) with tests disallowing promotion of **draft** to current policy, **commission vote** to City Council order or **order form** to executed contract.
- [Washington AGO original parser/action](../scripts/build_wa_ag_alpr_registry.py): strictly source-listed self-certified agencies and linked policies, sanitized public URLs, original bytes hash, bounded HTML, no plate movements, and semantic delta detection rather than spurious "camera additions".
- [State registry UI](../wa-alpr-registrations.html) validated in desktop and 390-pixel Chromium smoke tests, with textContent-only DOM and strict policy-source host/query checks.
- [National evidence library](../national-audits.html) includes eight new typed original documents on top of the existing seven source-pinned oversight/agency-audit PDFs, plus a link to the 97-source registration index and a government publisher source directory.
- Source-watch queues exclude the eight newly reviewed primary document URLs and prioritize future unseen original sources. The existing unreviewable San Bruno redirect remains held.
- No Supabase production schema changes or paid services.

**Next priority:** Authentically resolve the held San Bruno policy source, verify Moline's dated official program-pause announcement, and compare selected Washington policy submissions to published state privacy controls *without assuming every registered system is Flock*. Expand government registries systematically beyond eight monitored states, not merely repeated web leads.
