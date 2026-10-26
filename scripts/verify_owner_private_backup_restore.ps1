# OWNER-ONLY offline restore acceptance; NEVER invoke from GitHub Actions.
# Run only against a NEW, EMPTY, disposable localhost PostgreSQL 17 database.
# The role used here must be a local superuser; the production Supabase project
# must NEVER be targeted. Existing databases are refused rather than modified.
# Actual Storage photo bytes must be restored separately.
param([Parameter(Mandatory=$true)][string]$EncryptedBackupFolder)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
if ($env:GITHUB_ACTIONS -eq 'true') { throw 'Never restore confidential backups in a CI runner.' }
if ($env:KATOPTRON_RESTORE_CONFIRM -cne 'LOCAL_DISPOSABLE_ONLY') {
 throw 'Set KATOPTRON_RESTORE_CONFIRM=LOCAL_DISPOSABLE_ONLY after preparing an isolated local recovery database.'
}
if ($env:PGHOST -notin @('127.0.0.1','localhost','::1')) {
 throw 'Restore destination must be loopback only. Remote and production databases forbidden.'
}
# libpq settings can override PGHOST or redirect a supposedly local restore.
# Fail closed rather than resolve an ambiguous target via a service or address.
foreach ($name in @('PGHOSTADDR','PGSERVICE','PGSERVICEFILE','PGOPTIONS')) {
 $value=[Environment]::GetEnvironmentVariable($name)
 if (-not [string]::IsNullOrWhiteSpace($value)) {
   throw "Unset $name before the local-only restore; implicit connection overrides are forbidden."
 }
}
if ($env:PGDATABASE -notmatch '^katoptron_recovery_[a-z0-9_]{4,50}
 throw 'Recovery database must have unique disposable katoptron_recovery_* name.'
}
if ([string]::IsNullOrWhiteSpace($env:PGUSER) -or [string]::IsNullOrWhiteSpace($env:PGPASSWORD)) {
 throw 'Use private local PGUSER and PGPASSWORD environment settings; do not share credentials.'
}
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
 throw 'PostgreSQL psql client is not installed locally.'
}
$folder=(Resolve-Path -LiteralPath $EncryptedBackupFolder).Path
if (-not (Test-Path -LiteralPath $folder -PathType Container)) { throw 'Private backup folder missing.' }
$paths=@{}
foreach ($name in @('roles.sql','schema.sql','data.sql')) {
 $file=Join-Path $folder $name
 if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw 'Required private backup file missing.' }
 if ((Get-Item -LiteralPath $file).Length -lt 100) { throw 'Backup file empty or implausibly short.' }
 $paths[$name]=$file
 $null=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
}
Write-Output 'INPUT PASS: private roles/schema/data files readable and hashed.'
# Do not restore over an existing database or trust default PostgreSQL grants.
# The guard and ACL reset run in the same atomic transaction as the restore.
# This models the local production-snapshot restore fix found on October 24.
$preflight=@'
DO $guard$
DECLARE object_count integer;
BEGIN
 IF current_database() !~ '^katoptron_recovery_[a-z0-9_]{4,50}
if ($LASTEXITCODE -ne 0) { throw 'LOCAL RESTORE OR ISOLATION PREFLIGHT FAILED: archive is NOT certified. No success claim is valid.' }

$audit=@'
DO $$
DECLARE auth_count bigint; cam_count bigint;
BEGIN
 IF to_regclass('auth.users') IS NULL OR
    to_regclass('public.flock_community_submissions') IS NULL OR
    to_regclass('public.flock_camera_locations') IS NULL THEN
   RAISE EXCEPTION 'Critical Auth, submissions or camera tables missing';
 END IF;
 SELECT count(*) INTO auth_count FROM auth.users;
 IF auth_count < 1 THEN RAISE EXCEPTION 'Auth identities missing';END IF;
 SELECT count(*) INTO cam_count FROM public.flock_camera_locations
   WHERE verification_status='verified' AND location_accuracy='exact';
 IF cam_count < 293 THEN RAISE EXCEPTION 'Restored snapshot predates current verified camera baseline';END IF;
 IF NOT (SELECT relrowsecurity FROM pg_class
   WHERE oid='public.flock_community_submissions'::regclass) OR
   has_table_privilege('anon','public.flock_community_submissions','SELECT') OR
   has_table_privilege('anon','public.flock_community_submissions','INSERT') OR
   has_table_privilege('authenticated','public.editorial_reviewers','SELECT') THEN
   RAISE EXCEPTION 'Restored private reports and reviewer permissions unsafe';
 END IF;
END $$;
'@
& psql -X --set=ON_ERROR_STOP=1 --command $audit | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'RESTORED SECURITY ACCEPTANCE FAILED.' }
Write-Output 'LOCAL AUTH/DATABASE RESTORE PASS: identities, source camera baseline and private RLS verified.'
Write-Output 'NOT COVERED: actual Storage bytes, email delivery, OAuth secrets, encryption and offsite retention.'
Write-Output 'Never publish backup contents, restore credentials, or private reports in CI.'
) {
 throw 'Recovery database must have unique disposable katoptron_recovery_* name.'
}
if ([string]::IsNullOrWhiteSpace($env:PGUSER) -or [string]::IsNullOrWhiteSpace($env:PGPASSWORD)) {
 throw 'Use private local PGUSER and PGPASSWORD environment settings; do not share credentials.'
}
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
 throw 'PostgreSQL psql client is not installed locally.'
}
$folder=(Resolve-Path -LiteralPath $EncryptedBackupFolder).Path
if (-not (Test-Path -LiteralPath $folder -PathType Container)) { throw 'Private backup folder missing.' }
$paths=@{}
foreach ($name in @('roles.sql','schema.sql','data.sql')) {
 $file=Join-Path $folder $name
 if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw 'Required private backup file missing.' }
 if ((Get-Item -LiteralPath $file).Length -lt 100) { throw 'Backup file empty or implausibly short.' }
 $paths[$name]=$file
 $null=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
}
Write-Output 'INPUT PASS: private roles/schema/data files readable and hashed.'
& psql -X --single-transaction --set=ON_ERROR_STOP=1 --file $paths['roles.sql'] --file $paths['schema.sql'] --command 'SET session_replication_role = replica' --file $paths['data.sql'] | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'LOCAL RESTORE FAILED: archive is NOT certified.' }

$audit=@'
DO $$
DECLARE auth_count bigint; cam_count bigint;
BEGIN
 IF to_regclass('auth.users') IS NULL OR
    to_regclass('public.flock_community_submissions') IS NULL OR
    to_regclass('public.flock_camera_locations') IS NULL THEN
   RAISE EXCEPTION 'Critical Auth, submissions or camera tables missing';
 END IF;
 SELECT count(*) INTO auth_count FROM auth.users;
 IF auth_count < 1 THEN RAISE EXCEPTION 'Auth identities missing';END IF;
 SELECT count(*) INTO cam_count FROM public.flock_camera_locations
   WHERE verification_status='verified' AND location_accuracy='exact';
 IF cam_count < 293 THEN RAISE EXCEPTION 'Restored snapshot predates current verified camera baseline';END IF;
 IF NOT (SELECT relrowsecurity FROM pg_class
   WHERE oid='public.flock_community_submissions'::regclass) OR
   has_table_privilege('anon','public.flock_community_submissions','SELECT') OR
   has_table_privilege('anon','public.flock_community_submissions','INSERT') OR
   has_table_privilege('authenticated','public.editorial_reviewers','SELECT') THEN
   RAISE EXCEPTION 'Restored private reports and reviewer permissions unsafe';
 END IF;
END $$;
'@
& psql -X --set=ON_ERROR_STOP=1 --command $audit | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'RESTORED SECURITY ACCEPTANCE FAILED.' }
Write-Output 'LOCAL AUTH/DATABASE RESTORE PASS: identities, source camera baseline and private RLS verified.'
Write-Output 'NOT COVERED: actual Storage bytes, email delivery, OAuth secrets, encryption and offsite retention.'
Write-Output 'Never publish backup contents, restore credentials, or private reports in CI.'
 THEN
   RAISE EXCEPTION 'Not an explicitly named disposable recovery database';
 END IF;
 IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
   RAISE EXCEPTION 'Restore requires a local database superuser to prepare default ACLs';
 END IF;
 SELECT count(*) INTO object_count
 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE c.relkind IN ('r','p','v','m','f','S')
   AND n.nspname NOT IN ('pg_catalog','information_schema')
   AND n.nspname NOT LIKE 'pg_toast%';
 IF object_count<>0 THEN
   RAISE EXCEPTION 'Recovery target is not EMPTY. Do not overwrite or merge any existing records';
 END IF;
END $guard$;
DO $revoke$
DECLARE owner_role text;
BEGIN
 FOREACH owner_role IN ARRAY ARRAY['postgres','supabase_admin',current_user] LOOP
   IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname=owner_role) THEN
     EXECUTE format(
       'ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated',
       owner_role
     );
   END IF;
 END LOOP;
END $revoke$;
'@
& psql -X --single-transaction --set=ON_ERROR_STOP=1 --command $preflight --file $paths['roles.sql'] --file $paths['schema.sql'] --command 'SET session_replication_role = replica' --file $paths['data.sql'] | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'LOCAL RESTORE FAILED: archive is NOT certified.' }

$audit=@'
DO $$
DECLARE auth_count bigint; cam_count bigint;
BEGIN
 IF to_regclass('auth.users') IS NULL OR
    to_regclass('public.flock_community_submissions') IS NULL OR
    to_regclass('public.flock_camera_locations') IS NULL THEN
   RAISE EXCEPTION 'Critical Auth, submissions or camera tables missing';
 END IF;
 SELECT count(*) INTO auth_count FROM auth.users;
 IF auth_count < 1 THEN RAISE EXCEPTION 'Auth identities missing';END IF;
 SELECT count(*) INTO cam_count FROM public.flock_camera_locations
   WHERE verification_status='verified' AND location_accuracy='exact';
 IF cam_count < 293 THEN RAISE EXCEPTION 'Restored snapshot predates current verified camera baseline';END IF;
 IF NOT (SELECT relrowsecurity FROM pg_class
   WHERE oid='public.flock_community_submissions'::regclass) OR
   has_table_privilege('anon','public.flock_community_submissions','SELECT') OR
   has_table_privilege('anon','public.flock_community_submissions','INSERT') OR
   has_table_privilege('authenticated','public.editorial_reviewers','SELECT') THEN
   RAISE EXCEPTION 'Restored private reports and reviewer permissions unsafe';
 END IF;
END $$;
'@
& psql -X --set=ON_ERROR_STOP=1 --command $audit | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'RESTORED SECURITY ACCEPTANCE FAILED.' }
Write-Output 'LOCAL AUTH/DATABASE RESTORE PASS: identities, source camera baseline and private RLS verified.'
Write-Output 'NOT COVERED: actual Storage bytes, email delivery, OAuth secrets, encryption and offsite retention.'
Write-Output 'Never publish backup contents, restore credentials, or private reports in CI.'
) {
 throw 'Recovery database must have unique disposable katoptron_recovery_* name.'
}
if ([string]::IsNullOrWhiteSpace($env:PGUSER) -or [string]::IsNullOrWhiteSpace($env:PGPASSWORD)) {
 throw 'Use private local PGUSER and PGPASSWORD environment settings; do not share credentials.'
}
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
 throw 'PostgreSQL psql client is not installed locally.'
}
$folder=(Resolve-Path -LiteralPath $EncryptedBackupFolder).Path
if (-not (Test-Path -LiteralPath $folder -PathType Container)) { throw 'Private backup folder missing.' }
$paths=@{}
foreach ($name in @('roles.sql','schema.sql','data.sql')) {
 $file=Join-Path $folder $name
 if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw 'Required private backup file missing.' }
 if ((Get-Item -LiteralPath $file).Length -lt 100) { throw 'Backup file empty or implausibly short.' }
 $paths[$name]=$file
 $null=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
}
Write-Output 'INPUT PASS: private roles/schema/data files readable and hashed.'
& psql -X --single-transaction --set=ON_ERROR_STOP=1 --file $paths['roles.sql'] --file $paths['schema.sql'] --command 'SET session_replication_role = replica' --file $paths['data.sql'] | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'LOCAL RESTORE FAILED: archive is NOT certified.' }

$audit=@'
DO $$
DECLARE auth_count bigint; cam_count bigint;
BEGIN
 IF to_regclass('auth.users') IS NULL OR
    to_regclass('public.flock_community_submissions') IS NULL OR
    to_regclass('public.flock_camera_locations') IS NULL THEN
   RAISE EXCEPTION 'Critical Auth, submissions or camera tables missing';
 END IF;
 SELECT count(*) INTO auth_count FROM auth.users;
 IF auth_count < 1 THEN RAISE EXCEPTION 'Auth identities missing';END IF;
 SELECT count(*) INTO cam_count FROM public.flock_camera_locations
   WHERE verification_status='verified' AND location_accuracy='exact';
 IF cam_count < 293 THEN RAISE EXCEPTION 'Restored snapshot predates current verified camera baseline';END IF;
 IF NOT (SELECT relrowsecurity FROM pg_class
   WHERE oid='public.flock_community_submissions'::regclass) OR
   has_table_privilege('anon','public.flock_community_submissions','SELECT') OR
   has_table_privilege('anon','public.flock_community_submissions','INSERT') OR
   has_table_privilege('authenticated','public.editorial_reviewers','SELECT') THEN
   RAISE EXCEPTION 'Restored private reports and reviewer permissions unsafe';
 END IF;
END $$;
'@
& psql -X --set=ON_ERROR_STOP=1 --command $audit | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'RESTORED SECURITY ACCEPTANCE FAILED.' }
Write-Output 'LOCAL AUTH/DATABASE RESTORE PASS: identities, source camera baseline and private RLS verified.'
Write-Output 'NOT COVERED: actual Storage bytes, email delivery, OAuth secrets, encryption and offsite retention.'
Write-Output 'Never publish backup contents, restore credentials, or private reports in CI.'
