#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
P=Path(__file__).with_name("preflight_ny_wv_original_flock_records.py")
s=importlib.util.spec_from_file_location("ny_wv_originals",P)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
class TestOriginalPublications(unittest.TestCase):
 def test_government_originals_and_evidence_boundaries(self):
  self.assertEqual(len(M.SOURCES),4)
  self.assertEqual({r["state"] for r in M.SOURCES.values()},{"NY","WV"})
  self.assertTrue(all(r["source_url"].startswith("https://") for r in M.SOURCES.values()))
 def test_unapproved_original_fails(self):
  with self.assertRaises(ValueError):M.retrieve("https://evil.test")
 def test_html_original_substantive_content(self):
  k="wv-august2026-legislature-flock-hearing"
  original=b"<html><body>August 10, 2026 Flock Committee 2027</body></html>"*4
  row=M.inspect(k,original)
  self.assertFalse(row["equipment_current"])
  self.assertFalse(row["policy_adopted"])
  self.assertEqual(row["source_type"],"html")
  with self.assertRaises(ValueError):M.inspect(k,b"<html><body>unrelated page</body></html>"*7)
if __name__=="__main__":unittest.main()
