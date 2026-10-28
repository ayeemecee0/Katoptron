# M10 · Apache Junction original Chapter 17, Ordinance 1579 and public Flock source diagram

Date reviewed: October 27, 2026. Original public source PDFs were retrieved from city and official Legistar publishers in CI October 28 UTC.

## New independently authenticated source files

| Original document | SHA-256 | Pages | Evidence status |
|---|---|---|---|
| Chapter 17, October 6 City Council ALPR *agenda attachment* | `ed2411b178181c2bca37e71fcb7c5678ba77f51e7363a6d9f155dc266ac5d724` | 3 | Page text verified; **not independently authenticated final enacted chapter** |
| Ordinance 1579, October 6 City Council *agenda attachment* | `11cbba99aafd376b194c112368988c4073acebbd0726abb218d806b27eb11244` | 3 | Original pages verified, **unsigned template**; page 3 has blank date/signature placeholders |
| **Separate City Clerk Ordinance 1579 original** | `9d4f0ff58b906c65112abd3cf725b00d95e3418a843cd5df0c9e30e9ea9a7e93` | 3 | Retrieved, SHA-pinned and **visually reviewed on all 3 scanned pages**; mayor signature and Clerk attestation visible on page 3; handwritten October 6, 2026 adoption date |

The first two files are accessible through the municipality's [October 6 City Council Legistar file 26-497](https://apachejunction.legistar.com/LegislationDetail.aspx?GUID=45E70F1A-8804-4C72-84F4-318419B76F61&ID=8252178&Options=&Search=). The third is the [City Clerk's distinct signed official document](https://www.apachejunctionaz.gov/DocumentCenter/View/33565/ORD1579). Its scanned original was directly rendered and independently inspected: pages 1–2 identify Ordinance 1579 and adoption by reference; page 3 has handwritten October 6, 2026 passage/signing dates and the mayor's and clerk's signatures. The city clerk [public notice registry](https://www.apachejunctionaz.gov/999/Public-Notices) independently confirms October 6 Council adoption while leaving legal effective date unfilled.

These are **not interchangeable documents**. The signed City Clerk ordinance **is now independently verified as the executed adopted instrument**. The council agenda Chapter 17 attachment is **still not verified identical to the final separately filed chapter** and the legal-effective date remains unestablished.

## Page-cited Chapter 17 attachment facts

- p2: §17-1-3 lists ALPR general-operation conditions.
- p3: §17-1-4(C) says the enumerated collected vehicle data are stored **30 consecutive calendar days**.
- p3: §17-1-4(D) describes sharing with other municipalities/counties subject to supervisor preapproval and access-control requirements.
- p3: §17-1-5 calls for monthly ALPR usage audits and review by an employee outside the police department.

All are **provisions as worded in the official source-page-reviewed Council agenda attachment**. None demonstrates actual data retention, sharing grants, audits, legal effective date, or police compliance. The final enacted chapter has not been compared to the City's separately scanned ordinance original. No independent camera location is established.

## New source-attributed municipal map

The department's [official public safety technology page](https://apachejunctionaz.gov/1241/Public-Safety-Technology) states **30 Flock ALPR cameras, a 30-day ordinary retention period, and sharing only with Arizona state/county/local agencies**. Those are attributed government statements as of this review, not independently verified current software settings or deployment counts.

The city's [Flock Camera Locations graphic](https://apachejunctionaz.gov/DocumentCenter/View/33429) is labeled **August 24, 2026** and distinguishes directional active-facing symbols, offline equipment, relocation points and proposed sites. It is a **schematic government disclosure, not survey-grade point geometry**. We link it as an original visual source without synthesizing latitude/longitude, camera count per symbol, or exact coverage simulation. Zero map pins were added.

## Implementation and verification

- `scripts/inspect_apache_junction_originals.py` downloads at most 8 MB each from four exact allowlisted government URLs, refuses redirects and non-PDF responses, parses page preview, and emits bounded read-only review receipts. The graphic fails its PDF gate and remains a separately linked official diagram.
- `scripts/verify_apache_junction_primary_sources.py` rechecks 2 exact original PDF SHA-256 strings and page-text anchors, and the separately visually reviewed signed scanned Clerk PDF's exact SHA/page count and image-backed pages. The visual signature/date finding is bound only to that reviewed hash.
- `.github/workflows/inspect_apache_junction_originals.yml` runs both verification and acquisition with artifacts retained 7 days.
- `data/apache-junction-original-chapter-and-map-receipts-2026-10-27.json` stores explicit source/date/status limits and the completed signed City Clerk original visual-page review.
- `apache-junction-original-chapter.js` validates the two council attachments, 1 held scanned original, government schematic, and 0 independently verified coordinates, then creates original-page citations.
- `policy-history.html` displays original Council agenda text, signed original City Clerk ordinance and a separate government schematic map, without inflating the existing Agency X-Ray dossier count.
- `scripts/test_apache_junction_original_chapter.cjs` and the mobile browser acceptance workflow reject fake coordinate counts, false enacted statuses and changed original hashes.

**Remaining original-text blocker:** the full, final adopted-by-reference Chapter 17 filed with the City Clerk has not yet been independently matched to the 3-page October 6 Council agenda code attachment. The scanned signed Ordinance 1579 itself **has** been visually verified, but it does not contain the full chapter language or separately specify a legal-effective date.
