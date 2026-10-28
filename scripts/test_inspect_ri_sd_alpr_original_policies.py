#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
P=Path(__file__).with_name("inspect_ri_sd_alpr_original_policies.py")
spec=importlib.util.spec_from_file_location("ri_sd",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class SourceOriginal(unittest.TestCase):
 def test_two_exact_official_hosts(self):
  self.assertEqual(len(M.SOURCES),2)
  self.assertTrue(all(r["source_url"].startswith("https://") and r["page_count"] in (6,10) for r in M.SOURCES.values()))
 def test_unknown_id_not_fetched(self):
  with self.assertRaises(ValueError):M.fetch("fake-external")
  with self.assertRaises(ValueError):M.inspect("fake-external",b"%PDF-1.7")
if __name__=="__main__":unittest.main()
