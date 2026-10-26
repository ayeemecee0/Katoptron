# Katoptron — M1 foundation engineering sign-off

**Date:** 2026-10-25 (America/Los_Angeles)
**Status:** Engineering scope signed off, 100% for M1 foundation. Requested by project owner in ChatGPT; this record is an engineering acceptance checkpoint, **not** an independent penetration-test attestation, a claim of completed production readiness, or a cryptographic user signature.

## Boundaries
- Repository: `ayeemecee0/Katoptron`, GitHub Pages.
- Live Supabase: `bpvkapswslmgfazbzpsv`.
- Scope: database/schema security baseline, RLS and source access permissions, migration repeatability, public-vs-private evidence separation, automated regression, deployment and source-monitor architecture.
- Nationwide source completeness, owner-only Auth dashboard settings, off-device encrypted recovery and human usability/security audits belong to separate M2/M3 acquisition and M9 launch acceptance.

## Acceptance evidence
1. All **62 of 62** public-schema base tables have RLS enabled (live query).
2. Supabase performance advisor reports **zero unindexed foreign keys** after migration 109. Existing unused index hints are informational and not proof of regression.
3. Exactly **two** anonymous executable privileged SQL source predicates remain, both bounded read-only `boolean` lookup helpers used by map RLS. Two other helpers were explicitly restricted in migration 110. Privileged source promotion/publishing RPCs are not anonymous.
4. **13** authenticated privileged function APIs match the documented allowlist. All sensitive authenticated APIs include an `auth.uid()` check; reviewer RPCs enforce active reviewer allowlist, and report deletion verifies submitter ownership. Existing reviewer acceptance tests and source-publishing guards are part of the disposable database CI. `set_community_review_status(uuid,text)` is not exposed.
5. [Full disposable PostgreSQL migration / RLS / Python / JavaScript validation passed](https://github.com/ayeemecee0/Katoptron/actions/runs/40236750949). [Website deployment passed on the last checkpoint](https://github.com/ayeemecee0/Katoptron/actions/runs/40236861216).
6. A production read-only SQL sign-off rechecked sensitive evidence-table privileges, source revocation RLS requirements and exposed helper allowlist on October 25, 2026 without mutations.
7. [Eight-jurisdiction public health passed](https://github.com/ayeemecee0/Katoptron/actions/runs/40236409546). [Production evidence identity/tier audit passed](https://github.com/ayeemecee0/Katoptron/actions/runs/40236682770). These monitor runtime M2/M3 data, rather than defining M1 completion.

## Accepted residual issues / boundaries
- Supabase advisor warns about **two intentionally anonymous `SECURITY DEFINER` read-only boolean predicates** required by present RLS. They expose only verified status of a provided source URL/key; avoid new privilege grants without another review.
- Supabase advisor warns on authenticated `SECURITY DEFINER` APIs intentionally surfaced to authenticated, role-checked editorial/community workflows; these are not public source-promotion APIs. Their code/auth gates remain subject to release regression.
- Supabase Auth leaked-password protection dashboard warning remains outstanding and **must be resolved before claiming full security launch readiness**.
- RLS/no-policy informational notices correspond to protected private tables, not missing anonymous access.
- Actual email confirmation, an externally restored encrypted off-device backup, provider free-tier quotas, real-world accessible usability, and final privacy/legal review are not certified by this sign-off.

## Change control
Reopen M1 if an unexpected anonymous/unauthorized database capability is found, a source-promotion/publication gate regresses, a CI/security acceptance fails, or a material schema change bypasses its release safety test. Do not inflate M2/M3 camera evidence counts or treat camera acquisition as part of M1 engineering.
