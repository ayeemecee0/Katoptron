#!/usr/bin/env python3
import copy,importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("verify_okc_2026_original_contracts.py")
spec=importlib.util.spec_from_file_location("okc_signed",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
D=json.loads(M.DATA.read_text(encoding="utf8"))
class OKCOriginals(unittest.TestCase):
 def test_four_separately_typed_source_pinned_legal_documents(self):
  rows=M.validate(D)
  self.assertEqual(len(rows),4)
  self.assertEqual(sum(r["status"].startswith("signed_city_and_vendor") for r in rows),1)
  self.assertEqual(sum(r["status"]=="original_staff_recommendation_not_vote_record" for r in rows),1)
  self.assertEqual(len(set(r["source_sha256"] for r in rows)),4)
  self.assertEqual(D["city_self_report"]["city_2026_flock_readers_reported"],90)
  self.assertEqual(D["city_self_report"]["partner_agencies_reported_as_of_2026_08_18"],109)
 def test_forge_execution_hardware_or_signed_funds_rejected(self):
  for update in [
   lambda d:d["documents"][0].update(status="unsigned_draft"),
   lambda d:d["documents"][0].update(source_sha256="0"*64),
   lambda d:d["documents"][0].update(verified_camera_coordinates=[[1,2]]),
   lambda d:d["documents"][2].update(status="executed_city_council_order"),
   lambda d:d["documents"][1]["png_sha256_by_page"].update({"1":"a"*64}),
   lambda d:d["city_self_report"].update(partner_agencies_reported_as_of_2026_08_18=999),
   lambda d:d["documents"].pop()]:
   c=copy.deepcopy(D);update(c)
   with self.assertRaises(ValueError):M.validate(c)
if __name__=="__main__":unittest.main()
