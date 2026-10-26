"""Offline M9 acceptance for the owner-only local recovery safety envelope.

These tests never run psql or touch a real database/backup. The CI PowerShell
parser separately verifies syntax; owner-private data never enters CI.
"""
from pathlib import Path
import unittest

SCRIPT=(Path(__file__).resolve().parent/"verify_owner_private_backup_restore.ps1").read_text(encoding="utf-8")

class OwnerRestoreSafety(unittest.TestCase):
 def test_no_duplicated_script_or_truncated_powershell_strings(self):
  self.assertEqual(SCRIPT.count("param("),1)
  self.assertEqual(SCRIPT.count("$preflight=@'"),1)
  self.assertEqual(SCRIPT.count("$audit=@'"),1)
  self.assertEqual(SCRIPT.count("--single-transaction"),1)
  self.assertEqual(SCRIPT.count("LOCAL AUTH/DATABASE RESTORE PASS"),1)
  self.assertLess(len(SCRIPT),9000)
  self.assertIn("if ($env:PGDATABASE -notmatch '^katoptron_recovery_[a-z0-9_]{4,50}$') {",SCRIPT)
 def test_never_run_in_ci(self):
  self.assertIn("$env:GITHUB_ACTIONS -eq 'true'",SCRIPT)
  self.assertIn("LOCAL_DISPOSABLE_ONLY",SCRIPT)
 def test_disallow_nonlocal_connection_redirect(self):
  for setting in ("PGHOST","PGHOSTADDR","PGSERVICE","PGSERVICEFILE","PGOPTIONS"):
   with self.subTest(setting=setting):
    self.assertIn(setting,SCRIPT)
  self.assertIn("katoptron_recovery_",SCRIPT)
 def test_preflight_must_precede_import_atomically(self):
  self.assertIn("current_database() !~",SCRIPT)
  self.assertIn("rolsuper",SCRIPT)
  self.assertIn("object_count<>0",SCRIPT)
  self.assertIn("Recovery destination is not EMPTY",SCRIPT)
  self.assertIn("--single-transaction",SCRIPT)
  self.assertLess(SCRIPT.index("$preflight=@'"),SCRIPT.index("--file $paths['roles.sql']"))
  self.assertIn("--command $preflight --file $paths['roles.sql']",SCRIPT)
 def test_default_acl_prepared_and_private_grants_checked(self):
  self.assertIn("ALTER DEFAULT PRIVILEGES FOR ROLE",SCRIPT)
  self.assertIn("REVOKE ALL ON TABLES FROM anon, authenticated",SCRIPT)
  self.assertIn("has_table_privilege('anon','public.flock_community_submissions','SELECT')",SCRIPT)
  self.assertIn("has_table_privilege('anon','public.flock_community_submissions','INSERT')",SCRIPT)
  self.assertIn("has_table_privilege('authenticated','public.editorial_reviewers','SELECT')",SCRIPT)
  self.assertIn("relrowsecurity",SCRIPT)
 def test_private_files_not_uploaded_or_logged(self):
  self.assertIn("Get-FileHash",SCRIPT)
  self.assertIn("GITHUB_ACTIONS",SCRIPT)
  self.assertNotIn("Set-Content -Path $env:GITHUB",SCRIPT)
  self.assertIn("actual Storage bytes",SCRIPT)

if __name__=="__main__":
 unittest.main()
