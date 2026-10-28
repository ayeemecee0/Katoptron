import importlib.util,io,json,unittest
from pathlib import Path
from pypdf import PdfWriter
P=Path(__file__).with_name("acquire_remaining_wa_ag_policy_originals.py")
sp=importlib.util.spec_from_file_location("wa_original_pdf_batch",P)
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
REG=json.loads(M.REG.read_text(encoding="utf8"))
REV=[*json.loads(M.REV1.read_text(encoding="utf8"))["documents"],
 *json.loads(M.REV2.read_text(encoding="utf8"))["documents"]]
class TestSourceBatch(unittest.TestCase):
 def test_97_registration_dedup_to_86_unreviewed(self):
  rows=M.select(REG,REV)
  self.assertEqual(len(rows),86)
  self.assertFalse(any(r["agency_name"]=="Arlington Police Department" for r in rows))
 def test_untrusted_wa_originals_rejected(self):
  for u in ["https://example.com/doc.pdf","http://www.atg.wa.gov/doc.pdf",
   "https://127.0.0.1/admin","https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/a.pdf?VersionId=a%26x",
   "https://agportal-s3bucket.s3.us-west-2.amazonaws.com/../../etc/passwd"]:
   self.assertFalse(M.safe(u),u)
  self.assertTrue(M.safe(REV[0]["source_url"]))
 def test_unavailable_publisher_is_review_hold(self):
  result=M.run(REG,REV,fetcher=lambda _:(_ for _ in ()).throw(ValueError("source_redirect")),workers=3)
  self.assertEqual(result["remaining_agencies_checked"],86)
  self.assertEqual(result["original_pdf_receipts_retrieved"],0)
  self.assertEqual(result["original_pdf_held"],86)
  self.assertTrue(all(x["flock_vendor_or_installation_verified"] is False for x in result["receipts"]))
  self.assertTrue(all(x["content_sha256"] is None for x in result["receipts"]))
 def test_pdf_page_receipt_does_not_verify_original_fact(self):
  p=PdfWriter();p.add_blank_page(width=600,height=780);f=io.BytesIO();p.write(f)
  r=M.select(REG,REV)[0]
  out=M.inspect(r,fetcher=lambda _:f.getvalue())
  self.assertEqual(out["status"],"retrieved_unreviewed_original_pdf")
  self.assertEqual(out["pdf_pages"],1)
  self.assertEqual(len(out["content_sha256"]),64)
  self.assertFalse(out["individual_original_policy_pages_verified"])
  self.assertFalse(out["flock_vendor_or_installation_verified"])
  self.assertEqual(out["camera_points_added"],0)
if __name__=="__main__":unittest.main()
