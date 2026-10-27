import importlib.util
import hashlib
from pathlib import Path
import unittest

S=Path(__file__).with_name("fingerprint_mn_flock_audits.py")
spec=importlib.util.spec_from_file_location("mn_original_receipts",S)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

GOOD={"source_url":"https://www.lrl.mn.gov/docs/2026/mandated/261351.pdf",
      "title_scope":"flock_named_in_title",
      "report_id":"26-1351.pdf",
      "report_title":"Stillwater Police Department 2026 ALPR Audit (Flock System) Executive Summary"}
BYTES=b"%PDF-1.7\n"+b"x"*210
class Page:
 def extract_text(self):return "Flock 30 day retention, sharing access control audit"
class Reader:
 def __init__(self,*args,**kwargs):
  self.pages=[Page(),Page(),Page()]
  self.is_encrypted=False

class Tests(unittest.TestCase):
 def test_receipt_only_has_minimal_private_metadata(self):
  r=M.receipt(GOOD,BYTES,Reader)
  self.assertEqual(r["source_sha256"],hashlib.sha256(BYTES).hexdigest())
  self.assertEqual(r["pages"],3)
  self.assertTrue(r["machine_flags"]["mentions_flock"])
  self.assertTrue(r["machine_flags"]["retention_topic_present"])
  self.assertEqual(r["examination_status"],"machine_receipt_only_needs_independent_review")
  self.assertNotIn("30 day",str(r))
  self.assertNotIn("executed",str(r))
  self.assertNotIn("compliance",str(r))
 def test_only_index_flock_title_not_other_vendor(self):
  with self.assertRaises(ValueError):
   M.receipt({**GOOD,"title_scope":"other_vendor_named_in_title"},BYTES,Reader)
  self.assertFalse(M.pdf_url_allowed("https://evil.example/docs/2026/mandated/261351.pdf"))
  self.assertFalse(M.pdf_url_allowed("https://www.lrl.mn.gov/docs/2026/mandated/261351.pdf?x=1"))
  self.assertTrue(M.pdf_url_allowed(GOOD["source_url"]))
 def test_fail_closed_if_one_original_unavailable(self):
  second={**GOOD,"source_url":"https://www.lrl.mn.gov/docs/2025/mandated/251683.pdf",
          "report_id":"25-1683.pdf"}
  calls=[]
  def fetch(url):
   calls.append(url)
   if url==second["source_url"]:raise OSError("source temporarily offline")
   return BYTES
  with self.assertRaisesRegex(ValueError,"no data written"):
   M.observe([GOOD,second],fetch,Reader)
  self.assertEqual(len(calls),2)
 def test_no_independent_pdf_claim_from_keywords(self):
  r=M.receipt(GOOD,BYTES,Reader)
  self.assertEqual(set(r["machine_flags"]),{
   "mentions_flock","retention_topic_present","sharing_topic_present",
   "auditing_topic_present","access_topic_present","machine_text_readable"})
 def test_reject_short_or_invalid_pdf(self):
  with self.assertRaisesRegex(ValueError,"unbounded"):
   M.receipt(GOOD,b"%PDF-1.4",Reader)
 def test_scan_bound(self):
  with self.assertRaisesRegex(ValueError,"Unbounded"):
   M.pick([GOOD]*41)

if __name__=="__main__":unittest.main()
