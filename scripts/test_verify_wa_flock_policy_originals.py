#!/usr/bin/env python3
import hashlib,importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("verify_wa_flock_policy_originals.py")
spec=importlib.util.spec_from_file_location("flock_original_evidence",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
C,A,T=M.originals()
class Pg:
 def __init__(self,txt=""):self.txt=txt
 def extract_text(self):return self.txt
class Tests(unittest.TestCase):
 def test_complete_registry_tied_and_eight_original_policies(self):
  docs=M.validate(C,A,T)
  self.assertEqual(len(docs),8)
  self.assertEqual(sum(d["policy_kind"]=="agency_training_bulletin" for d in docs),1)
  self.assertTrue(all(d["state"]=="WA" for d in docs))
  self.assertTrue(all(not any(k in d for k in ("camera_coordinates","operational_status","verified_deployed_camera_count")) for d in docs))
 def test_bad_source_identity_and_sha_fail_closed(self):
  rows=M.validate(C,A,T)
  for row in rows:
   for key,new in (("source_url","https://evil.example/a.pdf"),("content_sha256","0"*64),
    ("agency_name","Someone Else"),("page_count",999)):
    altered={**C,"documents":[({**x,key:new} if x["id"]==row["id"] else x) for x in rows]}
    with self.assertRaisesRegex(ValueError,"provenance"):M.validate(altered,A,T)
 def test_no_inference_from_unreviewed_claims(self):
  row=M.validate(C,A,T)[0]
  for extra in ("verified_deployed_camera_count","camera_coordinates","operational_status","sharing_edges"):
   altered={**C,"documents":[{**row,extra:4}]+C["documents"][1:]}
   with self.assertRaisesRegex(ValueError,"unsupported"):M.validate(altered,A,T)
 def test_sha_and_page_anchor_integrity(self):
  row=next(d for d in M.validate(C,A,T) if d["id"].startswith("federal-way"))
  raw=b"%PDF-1.7 synthetic test fixture"+b"x"*300
  class Doc:
   def __init__(self,*args,**kw):
    self.is_encrypted=False
    self.pages=[Pg() for _ in range(row["page_count"])]
    for p,terms in M.EXPECTED[row["id"]][3].items():
     self.pages[p-1]=Pg(" ".join(terms))
  revised={**row,"content_sha256":hashlib.sha256(raw).hexdigest()}
  self.assertEqual(M.verify(revised,raw,Doc),4)
  with self.assertRaisesRegex(ValueError,"content changed"):M.verify(row,raw,Doc)
  class Altered(Doc):
   def __init__(self,*args,**kw):
    super().__init__(*args,**kw)
    self.pages[1]=Pg("Four cameras have become eighty cameras")
  with self.assertRaisesRegex(ValueError,"page anchor changed"):M.verify(revised,raw,Altered)
 def test_conflict_disclosure_and_proposal_limits_enforced(self):
  rows=M.validate(C,A,T)
  for slug,category in (("sedro-woolley","policy_internal_retention_language_conflict"),
    ("federal-way","agency_proposal_distinct_from_installation")):
   bad=json.loads(json.dumps(C))
   row=next(r for r in bad["documents"] if r["id"].startswith(slug))
   row["findings"]=[f for f in row["findings"] if f["category"]!=category]
   with self.assertRaises(ValueError):M.validate(bad,A,T)
 def test_sultan_training_not_registered_as_approved_agency_policy(self):
  names={x["agency_name"] for x in M.validate(C,A,T)}
  self.assertNotIn("Sultan Police Department",names)
if __name__=="__main__":unittest.main()
