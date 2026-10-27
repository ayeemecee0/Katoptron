import importlib.util
import hashlib
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
  self.assertEqual(len(M.manifest_rows(CATALOG)),15)
  raw=b"%PDF-1.7"+b" synthetic test only "
  fixture={**RECORD,"content_sha256":hashlib.sha256(raw).hexdigest()}
  self.assertEqual(M.verify_pdf(fixture,raw,Reader),5)
  with self.assertRaisesRegex(ValueError,"version changed"):
   M.verify_pdf(RECORD,raw,Reader)
  class Missing(Reader):
   def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self.pages[1]=Page("No retention statement")
  with self.assertRaisesRegex(ValueError,"page text differs"):
   M.verify_pdf(fixture,raw,Missing)
 def test_three_additional_audits_require_exact_checked_page_anchors(self):
  raw=b"%PDF-1.7 curated synthetic input"
  examples={
   "richfield-mn-independent-flock-alpr-audit-2026":(
    "Richfield Police Department had 8 stationary Flock ALPR units. The default 30-day retention period.",
    "A sample of the whole month of March 2026 was documented in the Flock system by agency and justification."),
   "woodbury-mn-independent-flock-alpr-audit-2026":(
    "Woodbury Public Safety had 17 active stationary Flock ALPR units and no mobile Flock units, default 30-day retention.",
    "Interagency requests documented by agency name, requesting party and case number."),
   "brooklyn-center-mn-independent-flock-alpr-audit-2025":(
    "Brooklyn Center Police Department had 9 active stationary ALPR units and no Flock mobile units, default 30-day retention period.",
    "Interagency requests documented by agency name, requesting party and case number."),
  }
  for audit_id,(second,third) in examples.items():
   record=next(r for r in CATALOG["reports"] if r["id"]==audit_id)
   class Match:
    def __init__(self,*args,**kwargs):
     self.is_encrypted=False
     self.pages=[Page("title"),Page(second),Page(third),Page("summary"),Page("signature")]
   fixture={**record,"content_sha256":hashlib.sha256(raw).hexdigest()}
   self.assertEqual(M.verify_pdf(fixture,raw,Match),5)
   class Changed(Match):
    def __init__(self,*args,**kwargs):
     super().__init__(*args,**kwargs)
     self.pages[2]=Page("Unrelated audit material")
   with self.assertRaisesRegex(ValueError,"page changed"):
    M.verify_pdf(fixture,raw,Changed)
 def test_nine_more_original_audits_fail_closed_on_page_drift(self):
  raw=b"%PDF-1.7 synthetic reviewed-page provenance"
  self.assertEqual(len(M.ADDITIONAL_REVIEWED_PAGE_ANCHORS),9)
  for audit_id,anchors in M.ADDITIONAL_REVIEWED_PAGE_ANCHORS.items():
   record=next(r for r in CATALOG["reports"] if r["id"]==audit_id)
   original=next(i for i in (2,3,4) if i in (int(p) for p in anchors))
   class Match:
    def __init__(self,*args,**kwargs):
     self.is_encrypted=False
     self.pages=[Page("title") for _ in range(5)]
     for page,phrases in anchors.items():
      self.pages[int(page)-1]=Page(" ".join(phrases))
   fixture={**record,"content_sha256":hashlib.sha256(raw).hexdigest()}
   self.assertEqual(M.verify_pdf(fixture,raw,Match),5,audit_id)
   class Changed(Match):
    def __init__(self,*args,**kwargs):
     super().__init__(*args,**kwargs)
     self.pages[original-1]=Page("Unrelated changed archive content")
   with self.assertRaisesRegex(ValueError,"page text changed"):
    M.verify_pdf(fixture,raw,Changed)

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
