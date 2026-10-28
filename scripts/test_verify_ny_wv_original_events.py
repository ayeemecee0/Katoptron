#!/usr/bin/env python3
import copy,importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("verify_ny_wv_original_events.py")
s=importlib.util.spec_from_file_location("ny_wv_events",P)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
DATA=json.loads(M.DATA.read_text(encoding="utf8"))
class StrictOriginals(unittest.TestCase):
 def test_exact_four_dated_reconciliation_events(self):
  rows=M.validate(DATA)
  self.assertEqual(len(rows),4)
  self.assertEqual(rows[0]["state"],"NY")
  self.assertEqual(rows[0]["visually_reviewed_page"],7)
  self.assertEqual(rows[1]["source_date"],"2026-04-14")
  self.assertEqual(rows[2]["state"],"WV")
  self.assertIn("not_enacted",rows[2]["status"])
 def test_cannot_upgrade_proposals_or_history_into_deactivation_or_law(self):
  for mutation in [
   lambda d:d["records"][0].update(operational_camera_count=20),
   lambda d:d["records"][1].update(finished_camera_removal_verified=True),
   lambda d:d["records"][3].update(enacted_wv_flock_statute=True),
   lambda d:d["records"][0].update(source_page_png_sha256="0"*64),
   lambda d:d["records"][1].update(source_date="2026-04-07"),
   lambda d:d["records"][2].update(status="passed_legislation"),
   lambda d:d["records"].pop()]:
   x=copy.deepcopy(DATA);mutation(x)
   with self.assertRaises(ValueError):M.validate(x)
if __name__=="__main__":unittest.main()
