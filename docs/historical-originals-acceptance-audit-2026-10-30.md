# Historical government originals: acceptance audit (2026-10-30)

## Verified achievements

- **Durable private evidence archive: PASSED.** [Main-branch run 41091225295](https://github.com/ayeemecee0/Katoptron/actions/runs/41091225295) completed successfully. Its backup stage reported 130 current archived government originals and 223 uniquely indexed source versions; a separate restoration into an empty temporary directory restored and SHA-256 verified all 223 stored original versions. The original bytes and recovery manifest reside in the nonpublic Supabase bucket `katoptron-original-archive`. Private access is mediated by the source-restricted GitHub OIDC gateway, not public storage policies or checked-in service-role credentials.
- The earlier production attempt [41090425059](https://github.com/ayeemecee0/Katoptron/actions/runs/41090425059) failed after its GitHub OIDC token expired. The successful run used parallel transfers; a subsequent merged change enables token renewal on HTTP 401, without bypassing 403. The new token-renewal run is independent of the successful preceding archive restore.
- **Historical URLs: not all recovered.** The successful archive run retrieved 12 of 19 historical originals in that specific scan; 7 were held that run. A separate fixed dated evidence snapshot records 13 distinct historically authenticated originals, with six that have never been authentic original-byte recovered. Do not confuse current reachability (fluctuates) with cumulative prior SHA-verified acquisitions.
- **Ohio original signed contract DPS020262: pending.** The Controlling Board [request DPS0105268](https://controllingboard.obm.ohio.gov/Print/PrintCBRequest?id=511a4ceb-9a1e-420f-b949-2257330dbf4a) names the signed attachment. An October 30 public-records request was already sent to Ohio Office of Budget and Management, with an automatic acknowledgment received, but no substantive answer or contract PDF yet.
- **Naperville ten clauses: prepared, not externally approved.** The [2025](https://www.naperville.il.us/DocumentCenter/View/1305/Automated-License-Plate-Reader-Policy---10-08-2025-PDF) and [2026](https://www.naperville.il.us/DocumentCenter/View/1304/Automated-License-Plate-Reader-Policy---09-08-2026-PDF) original publisher PDFs anchor ten draft comparisons. Independent reviewers have been invited; zero approvals and zero rejections have been authenticated. The city records-request acknowledgment does not establish effective dates beyond publication text.
- **Investigative dossiers: ten prepared, zero independently reviewed.** See [the source-attributed review ledger](../data/ten-original-issuer-investigation-review-dossiers-2026-10-30.json). None may trigger a Watch notification or be described as a verified original-version change or finding of misconduct.

## Six never-authenticated historical original identities and requirements

1. **CO, Lafayette:** official redirect now lands on a related Police Transparency index, not proven equivalent to original Flock program page. Require an actual archived original or issuer attestation identifying the replacement and historical version.
2. **MI, State Administrative Board:** original June 3 2025 minutes PDF returned HTTP 403. An issuer-indexed revised URL is a lead, not an authenticated identical original.
3. **OH, Controlling Board:** original procurement request HTML failed at network transport; signed DPS020262 attachment remains outstanding.
4. **NY, MPTC:** archived March 2021 model policy URL returned 404 to the automated monitor; 2022 model policy is explicitly a different edition.
5. **IL, Naperville:** historical transparency URL returned 404; a separate current publisher transparency page cannot retroactively prove old URL text.
6. **WI, Sheboygan:** original August 25 municipal announcement returned HTTP 403 to the monitor; publication content is discoverable but automated exact-source bytes remain unauthenticated.

## Remaining completion gates

- **P0 issuer originals:** six verified original-byte receipts or issuer-confirmed replacements, with exact historical identity and content version, without inventing success on 403/404/redirects.
- **P0 Ohio:** obtain and archive exact signed contract DPS020262 with original publisher URL, SHA-256, signature/term/payment analysis and explicit evidence limitations. Until received, the procurement approval proves only spending authorization.
- **P1 editorial:** ten genuine external decisions for Naperville, each with reviewer attribution, exact before/after text, page anchors and dated source limits. Pending invitations are not approvals.
- **P1 investigation:** ten independently reviewed source-dated investigative findings, each proving a bounded original text claim and giving unresolved questions, with no implicit camera coordinates or Watch notifications.
- **P1 reliability:** seven consecutive successful nationwide monitoring runs and one subsequent independent cold-cache restore after the first successful private archive acceptance.

The durable archive milestone is operationally complete. Government-original retrieval, external editorial sign-off and independently verified investigation publication are not.
