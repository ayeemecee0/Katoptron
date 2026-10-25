# Katoptron — Free-plan private-data backup and recovery

Last reviewed 2026-10-24. **The owner created and content-checked three private local application export files on an encrypted Windows drive. A complete Auth/Storage backup and an actual restore test of those files remain unfinished.**

## What the existing automated snapshots cover

GitHub's `snapshot_public_evidence.yml` copies **anonymous-public** government evidence only. It does **not** preserve private submissions, private Storage photos, reviewer notes, user accounts or full Supabase policies. It must never be repurposed to ship private account data into GitHub Actions artifacts.

Supabase recommends that Free-plan projects perform regular offline database exports using `supabase db dump`; managed downloadable daily backups are not included on Free. Database dumps do **not** include file contents from Supabase Storage.

Sources: [Supabase Database Backups](https://supabase.com/docs/guides/platform/backups); [Supabase CLI database dump](https://supabase.com/docs/reference/cli/supabase-db-dump); [Supabase Production Checklist](https://supabase.com/docs/guides/deployment/going-into-prod).

## Privacy-first, $0 ongoing-cost process

1. On your own trusted computer, enable full-disk encryption (Windows BitLocker or equivalent) and prepare an encrypted external drive or a separate encrypted vault. **Never store unencrypted database dumps, Storage evidence, connection strings or private reviewer files in the Katoptron GitHub repository or its Actions artifacts.**
2. Install the current Supabase CLI and Docker and check the supported flags with `supabase db dump --help`. Review official CLI documentation before executing commands.
3. In your project dashboard, use **Connect** to obtain the database connection information directly. Keep the database password on your machine; do **not** paste connection strings or passwords into this chat, GitHub Issues, CI logs or the frontend.
4. Make three independent logical exports on the trusted machine: roles, schema, and data. Reference commands below use PowerShell's already-defined local environment variable `KATOPTRON_DB_URL` and a private output directory. Database URL passwords may be visible to local operating-system process inspection; perform the export only on your own trusted computer. Keep the output location on an encrypted volume and do not display the URL in logs.
5. Move the three files into an independently encrypted archive, backed up offline. Restore-test the archive in a **local disposable** database before relying on it for production recovery. Ensure any test database cannot deliver outbound mail or publish cameras.
6. Back up **actual private Storage object content separately**, through authorized Supabase Storage API access into the same encrypted private archive. Storage SQL metadata alone cannot restore photo bytes, and direct SQL deletion of Storage objects is prohibited. Do not copy user photographs into the source repository.
7. Retain only as long as your privacy policy and recovery requirements justify, rotate encrypted archives, and restrict access to authorized operators. Test both DB restore and Storage file recovery after schema changes.

### Example local commands (PowerShell)

Run in a trusted local PowerShell terminal with a secure local `KATOPTRON_DB_URL` already set and an existing `D:\\PrivateEncryptedBackups\\Katoptron` folder on an encrypted drive. Do not include literal passwords in these commands.

```powershell
supabase db dump --help
supabase db dump --db-url "$env:KATOPTRON_DB_URL" -f "D:\PrivateEncryptedBackups\Katoptron\roles.sql" --role-only
supabase db dump --db-url "$env:KATOPTRON_DB_URL" -f "D:\PrivateEncryptedBackups\Katoptron\schema.sql"
supabase db dump --db-url "$env:KATOPTRON_DB_URL" -f "D:\PrivateEncryptedBackups\Katoptron\data.sql" --use-copy --data-only
```

The example assumes Docker/CLI support, working database access and adequate protected local storage. These commands are **not yet executed or certified**. The schema/data/roles trio follows Supabase's [restore-from-platform guidance](https://supabase.com/docs/guides/self-hosting/restore-from-platform).

## Restore acceptance checklist

- A disposable local PostgreSQL/Supabase-compatible environment accepts role, schema and data restores in the required order and preserves source-review permissions, triggers and RLS.
- An unauthenticated session cannot read private community submissions, review history, screening or private photo metadata.
- An ordinary authenticated user can access only their own reports and is denied reviewer capabilities. The reviewer's allowlist remains restricted.
- Community withdrawals still revoke linked tiered evidence; public camera verification counts reconcile with original government sources.
- One sample private Storage object can be restored into a private local bucket, opened only by its authorized owner or reviewer, and deleted by the permitted Storage API path.
- Encryption recovery keys/passphrases are independently stored; losing a backup key must not require public disclosure of private data.
- Document test date, observed pass/fail checks and a realistic recovery point objective; do **not** mark restore verified on the basis of a file existing.

## Owners and status

Current state: owner generated non-empty roles, schema and data SQL files locally and verified basic content checks; no encrypted off-device archive, complete Auth/Storage backup or restore drill of those files. [CI application restore rehearsal #454](https://github.com/ayeemecee0/Katoptron/actions/runs/40112397254) passed against a disposable synthetic database, not the owner files. These operations require the project owner to handle credentials, access-controlled Storage evidence, encrypted retention and local capacity. Do not create a paid Supabase branch to run restore tests merely for convenience.


## October 24, 2026: synthetic recovery evidence and owner-held backup

**Private Storage restore passed:** [Real Auth + Storage acceptance #6](https://github.com/ayeemecee0/Katoptron/actions/runs/40139404172) used two disposable Auth users, an explicitly non-public synthetic report and a 1-by-1 PNG. It uploaded private data through the real Storage API, downloaded it as its authenticated owner, deleted the image, restored the same bytes and verified byte equality. It also tested restricted reviewer access and withdrawal. The run confirmed deletion of its temporary users, reviewer grant, report and image.

**Synthetic database recovery previously passed:** [CI recovery rehearsal #454](https://github.com/ayeemecee0/Katoptron/actions/runs/40112397254) exercised a disposable PostgreSQL database dump/restore, synthetic Auth foreign keys and RLS. It does **not** restore any real owner backup.

The new [owner-local recovery verifier](../scripts/verify_owner_private_backup_restore.ps1) provides a guarded PowerShell acceptance procedure. Its **syntax only** was verified by [check #1](https://github.com/ayeemecee0/Katoptron/actions/runs/40139635738), with no private file access.

To finish the confidential backup gate, the project owner must use an already encrypted Windows drive containing roles.sql, schema.sql and data.sql; prepare a clean disposable local PostgreSQL 17 or compatible self-hosted Supabase recovery database; set locally held PGHOST=127.0.0.1, PGDATABASE=katoptron_recovery_<unique>, PGUSER, PGPASSWORD and KATOPTRON_RESTORE_CONFIRM=LOCAL_DISPOSABLE_ONLY; then run the PowerShell verifier with -EncryptedBackupFolder. The script refuses remote/production hosts, verifies non-empty SHA-256-readable files, imports with official roles/schema/data order, and tests recovered Auth rows, minimum 293 verified camera records and private RLS grants. A failed restore cannot pass.

Real Storage photographs are not in Supabase DB dumps, so the owner must additionally export encrypted real Storage bytes if any exist, restore a sample only into a private isolated test Storage instance, and validate owner/reviewer access and deletion. Keep archival encryption keys apart from the archive and set recovery point/time goals.

**This final owner backup gate remains NOT VERIFIED.** The three private Windows exports, encrypted offsite archive, and actual isolated restore instance are not accessible through the connected services. Never copy private files or credentials to GitHub Actions or chat. Testing a synthetic 1-pixel image and a synthetic DB is not proof that the owner's original Auth, schema, data, or Storage backups recover.

Official references: [Supabase platform restore](https://supabase.com/docs/guides/self-hosting/restore-from-platform) and [Supabase backup guidance](https://supabase.com/docs/guides/platform/backups). The official platform restore guide specifies that Storage bytes, Auth provider configuration, SMTP settings and JWT secrets require separate setup.


## October 24: owner-conducted local restore acceptance — updated result

**The earlier "never restore-tested" statements above are historical and superseded for the database portion by this section.** The project owner used Windows PowerShell and Docker Desktop to start a local-only Supabase PostgreSQL 17.11 instance, binding all published ports to IPv4 127.0.0.1 and IPv6 ::1. Both the earlier 275-point SQL snapshot and a freshly exported production snapshot were restored with the roles/schema/data order prescribed by Supabase, through the verified local Docker database container. No production database restoration or mutation was performed.

**Important recovery defect found and reproduced:** importing with the local `postgres` account failed on `log_min_messages` (not superuser). Importing as local `supabase_admin` superuser succeeded, but the first restore inherited default public table privileges granting anonymous users inappropriate access to private reports and reviewer tables. The disposable database was RESET; before the second restore, the owner revoked automatic default table privileges for `anon, authenticated` from `postgres` and `supabase_admin` **in schema public**. Then the SQL dump was restored in one transaction with `ON_ERROR_STOP=1` and `SET session_replication_role=replica`. Direct post-restore permission checks passed.

**Fresh production snapshot:**
- `roles.sql` 370 bytes; `schema.sql` 328,855 bytes; `data.sql` 16,093,373 bytes, stored only in the owner's `C:\Users\ayeem\KatoptronFreshExport` folder (NEVER publish the files or contents).
- A second clean, default-grant-restricted local PostgreSQL 17 database accepted the roles/schema/data snapshot and reported `FRESH RESTORE SUCCESS`.
- Verification: 293/293 independently source-verified exact camera locations, one Auth user, 48/48 public tables with RLS, no anonymous report SELECT or INSERT privilege, and no authenticated direct reviewer-table SELECT privilege.
- An ephemeral fictional report with the restored Auth owner was visible to that owner but hidden from a different `authenticated` database principal. The transaction rolled back; subsequent read-only query found zero remaining fictional reports.
- These are **owner-reported local command results**, not CI access to the owner's private backup; no actual email confirmation or Storage binary backup occurred in this drill.

**Remaining before a confidential-data-resilient production service:** verify the Windows disk's BitLocker protection status; create a separately encrypted off-device archive/copy when accepting user-submitted private materials at scale; independently back up any real Storage blob bytes (SQL metadata does not preserve photographs); and test actual email-confirmation delivery/redirect. As of this checkpoint, production had zero community reports and zero private community photo objects. For an explicitly read-only public beta, lack of off-device redundancy may be a time-bounded accepted risk, not grounds to claim it is safely backed up.

**Do not blindly run the legacy `scripts/verify_owner_private_backup_restore.ps1` on the already restored `postgres` database.** That script was only syntax-tested, expects a separately named `katoptron_recovery_*` database and locally installed `psql`; it does not yet model the successful Docker-based recovery or the prerequisite default-grant hardening. Prepare and verify an isolated target, then follow the proven owner-local procedure with administrator credentials, no network-exposed ports and explicit privilege checks.

**Business-priority change:** the public map/source-validation MVP is prioritized over mature off-device archival infrastructure, but account signup, user privacy and consent/deletion protections remain mandatory when opening confidential public submissions. See [MVP acceptance and human test protocol](./mvp-beta-user-acceptance.md).


**Owner encryption check (October 24):** An elevated Windows `manage-bde -status C:` command reported `Used Space Only Encrypted`, `100.0%`, `XTS-AES 128`, `Protection On`, `TPM` and `Numerical Password` key protectors. This confirms the current fresh SQL backups under `C:\Users\ayeem\KatoptronFreshExport` reside on a BitLocker-protected OS volume while the computer is powered off/locked. The owner did not share, and must not share, the recovery key. BitLocker is **whole-volume encryption at rest**, not an independently encrypted portable archive: when Windows is unlocked, local processes with permission can read the files. Physical off-device copies, a separately secured decryption key, the actual Storage object bytes and a recovery drill remain outstanding for a mature confidential-data service. These are not blockers for the explicitly source-backed **read-only** MVP acceptance tier.