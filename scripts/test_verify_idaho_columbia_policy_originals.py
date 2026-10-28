#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("verify_idaho_columbia_policy_originals.py")
sp=importlib.util.spec_from_file_location("verify_two_state_original",P)
M=importlib.util.module_from_spec(sp)
sp.loader.exec_module(M)
class TestOriginalGovernmentSourcePages(unittest.TestCase):
 def setUp(self):self.record=json.loads(M.LEDGER.read_text(encoding="utf8"))
 def test_two_unambiguous_originals(self):
  docs=M.manifest(self.record)
  self.assertEqual({x["state"] for x in docs},{"ID","MO"})
  self.assertEqual([x["pages"] for x in docs],[2,9])
  self.assertEqual([len(x["findings"]) for x in docs],[4,7])
  self.assertEqual(self.record["exact_camera_points_added"],0)
  self.assertEqual(self.record["active_sharing_edges_added"],0)
 def test_original_digest_guard(self):
  with self.assertRaisesRegex(ValueError,"hash drift"):
   M.verify(fetcher=lambda url:b"%PDF-FORGED"*40,ledger=self.record)
 def test_denies_unsupported_evidence_upgrade(self):
  cases=[
   lambda d:d.update(exact_camera_points_added=1),
   lambda d:d["documents"][0].update(verified_exact_camera_points=1),
   lambda d:d["documents"][0].update(verified_current_camera_count=1),
   lambda d:d["documents"][1].update(verified_live_sharing_edges=1),
   lambda d:d["documents"][0].update(sha256="f"*64),
   lambda d:d["documents"][1].update(state="AZ"),
   lambda d:d["documents"][1].update(reviewed_pages=[1,2]),
   lambda d:d["documents"][1]["findings"][0].update(page=3),
   lambda d:d["documents"][0]["findings"][2].update(category="enacted_ordinance")
  ]
  for change in cases:
   d=json.loads(json.dumps(self.record));change(d)
   with self.assertRaisesRegex(ValueError,"original|Original|page|scope|SHA|source|Claim|Flock"):
    M.manifest(d)
if __name__=="__main__":unittest.main()
