#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("verify_nebraska_dakota_2025_aggregate.py")
s=importlib.util.spec_from_file_location("ne_original_aggregate",P)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
D=json.loads(M.DATA.read_text(encoding="utf8"))
class OriginalAggregate(unittest.TestCase):
 def test_original_data_and_only_visual_source_receipt(self):
  r=M.validate(D)
  self.assertEqual(r["metrics"]["ncic_confirmed_matches"],43)
  self.assertEqual(r["metrics"]["manual_plate_numbers_entered"],126)
  self.assertEqual(r["metrics"]["manual_entry_confirmed_matches"],19)
  self.assertEqual(r["report_start"],"2025-01-01")
  self.assertEqual(r["report_end"],"2025-12-31")
 def test_no_unreviewed_vendor_camera_and_report_promotion(self):
  for change in [
   lambda x:x["documents"][0].update({"flock_vendor_verified":True}),
   lambda x:x["documents"][0]["metrics"].update({"ncic_confirmed_matches":999}),
   lambda x:x["documents"][0].update({"source_sha256":"0"*64}),
   lambda x:x["documents"][0].update({"camera_coordinates":[1,2]}),
   lambda x:x["held_unverified_originals"][0].update({"can_publish_numeric_findings":True})]:
   c=json.loads(json.dumps(D));change(c)
   with self.assertRaises(ValueError):M.validate(c)
if __name__=="__main__":unittest.main()
