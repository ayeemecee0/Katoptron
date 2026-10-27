import importlib.util
import io
import json
from pathlib import Path
import unittest

P=Path(__file__).with_name("verify_independent_audit_source.py")
spec=importlib.util.spec_from_file_location("original_audit_source",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
CATALOG=json.loads(M.MANIFEST.read_text(encoding="utf-8"))
RECORD=CATALOG["reports"][0]
class Page:
 def __init__(self,text):self.text=text
 def extract_text(self):return self.text
class Reader:
 def __init__(self,*args,**kwargs):
  self.is_encrypted=False
  self.pages=[Page("Shakopee Police Department Flock in six permanent locations"),
   Page("Flock ALPR data has a thirty (30) day retention period"),
   Page("Sharing among law enforcement agencies"),
   Page("Authorization to Access Data and audit logging"),
   Page("Dated: June 15, 2026 - Lynn Lembcke Consulting")]
class TestPublicAuditSource(unittest.TestCase):
 def test_strict_public_government_host(self):
  good=RECORD["source_url"]
  self.assertTrue(M.allowed(good))
  for x in ("http://www.lrl.mn.gov/docs/file.pdf",
   "https://evil.example/docs/f.pdf",
   "https://www.lrl.mn.gov.evil.example/docs/file.pdf",
   "https://www.lrl.mn.gov@evil.example/docs/file.pdf",
   "https://www.lrl.mn.gov/docs/a.pdf#private",
   "https://www.lrl.mn.gov/docs/../secrets.pdf",
   "https://www.lrl.mn.gov:444/docs/a.pdf",
   "https://www.lrl.mn.gov/admin"):
   self.assertFalse(M.allowed(x),x)
 def test_no_source_facts_without_exact_page_receipts(self):
  self.assertEqual(len(M.manifest_rows(CATALOG)),1)
  raw=b"%PDF-1.7"+b" synthetic test only "
  self.assertEqual(M.verify_pdf(RECORD,raw,Reader),5)
  class Missing(Reader):
   def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self.pages[1]=Page("No retention statement")
  with self.assertRaisesRegex(ValueError,"page text differs"):
   M.verify_pdf(RECORD,raw,Missing)
 def test_fetch_not_called_for_unapproved_host(self):
  seen=[]
  with self.assertRaises(ValueError):
   M.get_pdf("https://evil.example/private.pdf",lambda url:seen.append(url))
  self.assertEqual(seen,[])
 def test_duplicate_source_rejected(self):
  dupe={"schema_version":1,"reports":[RECORD,RECORD]}
  with self.assertRaisesRegex(ValueError,"Duplicate"):
   M.manifest_rows(dupe)
if __name__=="__main__":unittest.main()
