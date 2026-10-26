# OWNER-ONLY offline restore acceptance; NEVER invoke from GitHub Actions.
# Only a NEW EMPTY disposable localhost PostgreSQL 17 recovery database.
# Requires local superuser and prevents unsafe restored report-table grants.
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
# Reject libpq overrides that can silently redirect a local restore elsewhere.
foreach ($name in @('PGHOSTADDR','PGSERVICE','PGSERVICEFILE','PGOPTIONS')) {
 $value=[Environment]::GetEnvironmentVariable($name)
 if (-not [string]::IsNullOrWhiteSpace($value)) {
  throw "Unset $name before the owner-local restore."
 }
}
if ($env:PGDATABASE -notmatch '^katoptron_recovery_[a-z0-9_]{4,50}$') {
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
# Atomic preflight: fail before import on any nonempty database; prepare safe
# default privileges in the SAME transaction as the three-file restore.
$preflight=@'
DO $guard$
DECLARE object_count integer;
BEGIN
 IF current_database() !~ '^katoptron_recovery_[a-z0-9_]{4,50}$' THEN
  RAISE EXCEPTION 'Not an explicitly named disposable recovery database';
 END IF;
 IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
  RAISE EXCEPTION 'Recovery importer must be a local superuser';
 END IF;
 SELECT count(*) INTO object_count
 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE c.relkind IN ('r','p','v','m','f','S')
   AND n.nspname NOT IN ('pg_catalog','information_schema')
   AND n.nspname NOT LIKE 'pg_toast%';
 IF object_count<>0 THEN
  RAISE EXCEPTION 'Recovery destination is not EMPTY';
 END IF;
END $guard$;
DO $acl$
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
END $acl$;
'@
& psql -X --single-transaction --set=ON_ERROR_STOP=1 --command $preflight --file $paths['roles.sql'] --file $paths['schema.sql'] --command 'SET session_replication_role = replica' --file $paths['data.sql'] | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'LOCAL RESTORE OR PREFLIGHT FAILED: archive is NOT certified.' }

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
