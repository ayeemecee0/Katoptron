#!/usr/bin/env python3
import copy,importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("verify_ri_sd_original_policies.py")
s=importlib.util.spec_from_file_location("ri_sd_verifier",P)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
D=json.loads(M.DATA.read_text(encoding="utf8"))
class OriginalPolicies(unittest.TestCase):
 def test_two_source_pinned_public_approved_policy_versions(self):
  docs=M.validate(D)
  self.assertEqual({r["state"] for r in docs},{"RI","SD"})
  self.assertEqual(docs[0]["source_effective_date"],"2026-09-04")
  self.assertEqual(docs[1]["source_effective_date"],"2026-09-22")
 def test_reject_unreviewed_active_flock_or_location_claims(self):
  for change in [
   lambda d:d["documents"][0].update(camera_count=21),
   lambda d:d["documents"][1].update(actual_data_sharing_verified=True),
   lambda d:d["documents"][1].update(original_sha256="0"*64),
   lambda d:d["documents"][1]["original_png_sha256"].update({"5":"0"*64}),
   lambda d:d["documents"][0].update(source_effective_date="2027-01-01"),
   lambda d:d["documents"].pop()]:
   test=copy.deepcopy(D);change(test)
   with self.assertRaises(ValueError):M.validate(test)
if __name__=="__main__":unittest.main()
