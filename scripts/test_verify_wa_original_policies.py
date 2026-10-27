#!/usr/bin/env python3
import hashlib,importlib.util,json,unittest
from pathlib import Path
name=Path(__file__).with_name("verify_wa_original_policies.py")
spec=importlib.util.spec_from_file_location("wa_original_policies",name)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
DATA=json.loads(M.PATH.read_text(encoding="utf8"))
AGO=json.loads(M.AGO_PATH.read_text(encoding="utf8"))
class Pg:
 def __init__(self,txt="",images=None):self.txt=txt;self.images=images or []
 def extract_text(self):return self.txt
class TestOriginalWashingtonPolicies(unittest.TestCase):
 def test_exact_ag_link_and_typed_source(self):
  rows=M.validate(DATA,AGO)
  self.assertEqual(len(rows),2)
  self.assertEqual(set(r["agency_name"] for r in rows),{"Auburn Police Department","Black Diamond Police Department"})
  self.assertTrue(all(r["state"]=="WA" for r in rows))
  self.assertTrue(all("flock_vendor" not in r for r in rows))
 def test_reject_fake_vendor_and_source_swap(self):
  rows=M.validate(DATA,AGO)
  for row in rows:
   for key,val in (("source_url","https://evil.example/policy"),("content_sha256","0"*64),
      ("source_tier","vendor-confirmed"),("page_count",90),("policy_manual_imprint","2026-01-01")):
    m={**row,key:val}
    altered={**DATA,"documents":[m if r["id"]==row["id"] else r for r in rows]}
    with self.assertRaisesRegex(ValueError,"identity|provenance"):M.validate(altered,AGO)
   changed={**row,"ago_registration_date":"2026-01-01"}
   with self.assertRaisesRegex(ValueError,"exactly linked"):
    M.validate({**DATA,"documents":[changed if r["id"]==row["id"] else r for r in rows]},AGO)
 def test_page_text_anchor_and_byte_integrity(self):
  row=next(x for x in M.validate(DATA,AGO) if x["id"].startswith("auburn"))
  raw=b"%PDF-1.7 synthetic WA text source"+b"x"*500
  phrases=M.EXPECTED[row["id"]]["anchors"]
  class Doc:
   def __init__(self,*args,**kwargs):
    self.is_encrypted=False
    self.pages=[Pg() for _ in range(row["page_count"])]
    for n,need in phrases.items():self.pages[n-1]=Pg(" ".join(need))
  m={**row,"content_sha256":hashlib.sha256(raw).hexdigest()}
  self.assertEqual(M.verify(m,raw,Doc),8)
  with self.assertRaisesRegex(ValueError,"byte hash drift"):M.verify(row,raw,Doc)
  class Changed(Doc):
   def __init__(self,*args,**kw):
    super().__init__(*args,**kw)
    self.pages[4]=Pg("incorrect page")
  with self.assertRaisesRegex(ValueError,"anchor drift"):M.verify(m,raw,Changed)
 def test_scanned_page_image_not_fabricated_ocr(self):
  row=next(x for x in M.validate(DATA,AGO) if x["id"].startswith("black-diamond"))
  raw=b"%PDF-1.7 synthetic black diamond scan"+b"z"*600
  class Scan:
   def __init__(self,*args,**kwargs):
    self.is_encrypted=False
    self.pages=[Pg(images=[object()]) for _ in range(7)]
  m={**row,"content_sha256":hashlib.sha256(raw).hexdigest()}
  self.assertEqual(M.verify(m,raw,Scan),7)
  class Missing(Scan):
   def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self.pages[3]=Pg()
  with self.assertRaisesRegex(ValueError,"image missing"):M.verify(m,raw,Missing)
 def test_reject_registry_link_substitution(self):
  rows=M.validate(DATA,AGO)
  changed=json.loads(json.dumps(AGO))
  x=next(r for r in changed["registrations"] if r["agency_name"]=="Auburn Police Department")
  x["policy_links_from_official_ago_page"]=["https://example.invalid/auburn.pdf"]
  with self.assertRaisesRegex(ValueError,"exactly linked"):M.validate(DATA,changed)
if __name__=="__main__":unittest.main()
