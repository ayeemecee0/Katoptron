#!/usr/bin/env python3
import hashlib,importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("verify_national_primary_documents.py")
s=importlib.util.spec_from_file_location("original_gov_policy",P)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
DATA=json.loads(M.PATH.read_text(encoding="utf-8"))
class Page:
 def __init__(self,t):self.t=t
 def extract_text(self):return self.t
class TestPageBoundGovernmentDocuments(unittest.TestCase):
 def test_nine_source_distinct_roles_and_one_held(self):
  rows=M.valid(DATA)
  self.assertEqual(len(rows),9)
  self.assertEqual(len(DATA["source_review_held"]),1)
  self.assertEqual(sum(x["kind"]=="draft_policy_unadopted" for x in rows),1)
  self.assertEqual(sum(x["kind"]=="advisory_recommendation_not_binding_action" for x in rows),1)
  self.assertEqual(sum(x["kind"]=="government_published_vendor_order_form" for x in rows),1)
  self.assertEqual(sum(x["kind"]=="agency_monthly_aggregate_report" for x in rows),1)
  self.assertEqual(len(set(x["source_url"] for x in rows)),9)
 def test_original_byte_and_page_anchors_change_fail_closed(self):
  raw=b"%PDF-1.7 synthetic original reviewed public report"+b"a"*250
  for row in M.valid(DATA):
   if row["id"]==M.MOLINE_ID:continue
   anchors=M.ANCHORS[row["id"]]
   class Reader:
    def __init__(self,*_args,**_kwargs):
     self.is_encrypted=False
     self.pages=[Page("cover") for _ in range(row["page_count"])]
     for p,terms in anchors.items():self.pages[p-1]=Page(" ".join(terms))
   fixture={**row,"content_sha256":hashlib.sha256(raw).hexdigest()}
   self.assertEqual(M.verify(fixture,raw,Reader),row["page_count"])
   with self.assertRaisesRegex(ValueError,"hash drift"):M.verify(row,raw,Reader)
   class Drift(Reader):
    def __init__(self,*args,**kwargs):
     super().__init__(*args,**kwargs)
     self.pages[next(iter(anchors))-1]=Page("Completely unrelated contents")
   with self.assertRaisesRegex(ValueError,"anchor drift"):M.verify(fixture,raw,Drift)
 def test_scanned_moline_original_uses_visual_receipts_not_fake_text(self):
  row=next(x for x in M.valid(DATA) if x["id"]==M.MOLINE_ID)
  self.assertEqual(row["source_date"],"2024-12-04")
  self.assertEqual(set(row["pages_reviewed"]),{2,3,5})
  self.assertEqual(row["verification_method"],"visual_page_review_sha256_pinned_scanned_pdf")
  raw=b"%PDF-1.7 synthetic scanned city original"+b"z"*350
  class RasterPage:
   images=[object()]
  class RasterDocument:
   def __init__(self,*args,**kwargs):
    self.is_encrypted=False
    self.pages=[RasterPage() for _ in range(6)]
  testrow={**row,"content_sha256":hashlib.sha256(raw).hexdigest()}
  self.assertEqual(M.verify(testrow,raw,RasterDocument),6)
  with self.assertRaisesRegex(ValueError,"hash drift"):M.verify(row,raw,RasterDocument)
  class MissingImage(RasterDocument):
   def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    class Blank:images=[]
    self.pages[1]=Blank()
  with self.assertRaisesRegex(ValueError,"scanned page images unavailable"):
   M.verify(testrow,raw,MissingImage)
  changed={**row,"verification_method":"text_anchors_verified_by_ocr"}
  with self.assertRaisesRegex(ValueError,"Visual review scope"):
   M.valid({**DATA,"documents":[changed if x["id"]==row["id"] else x for x in DATA["documents"]]})
 def test_2026_draft_and_2025_advisory_can_never_claim_adoption(self):
  originals=DATA["documents"]
  draft=next(r for r in originals if r["kind"]=="draft_policy_unadopted")
  resolution=next(r for r in originals if r["kind"]=="advisory_recommendation_not_binding_action")
  order=next(r for r in originals if r["kind"]=="government_published_vendor_order_form")
  for row,new in [
   (draft,{**draft,"status":"current_final_adopted"}),
   (resolution,{**resolution,"status":"city_council_ordered_shutdown"}),
   (order,{**order,"status":"contract_fully_executed_and_paid"}),
   (draft,{**draft,"kind":"published_department_policy"}),
   (order,{**order,"source_url":"https://evil.example/fake.pdf"})]:
   catalog={**DATA,"documents":[new if r["id"]==row["id"] else r for r in originals]}
   with self.assertRaisesRegex(ValueError,"Never promote|cannot become|Execution|source or document status"):M.valid(catalog)
 def test_unreviewed_redirect_remains_explicitly_held(self):
  with self.assertRaisesRegex(ValueError,"Held San Bruno"):
   M.valid({**DATA,"source_review_held":[]})
  self.assertTrue(all(r["id"]!="san-bruno-ca-alpr-policy" for r in M.valid(DATA)))
if __name__=="__main__":unittest.main()
