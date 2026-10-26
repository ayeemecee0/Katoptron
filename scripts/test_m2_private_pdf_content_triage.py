import datetime as dt
import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).parent
def module(filename,name):
 p=ROOT/filename;spec=importlib.util.spec_from_file_location(name,p)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

M=module("triage_original_government_pdf_content.py","pdf_triage")
A=module("acquire_original_government_documents.py","acquisition")
NOW=dt.datetime(2026,10,26,12,tzinfo=dt.timezone.utc)
PDF=b"%PDF-1.7\n"+b"0 1 obj\n<</Type /Catalog>>\nendobj\n"+b"%%EOF\n"
SHA=hashlib.sha256(PDF).hexdigest()
LEAD={"document_url":"https://portagein.gov/DocumentCenter/View/6885/FLOCK-CONTRACTpdf",
      "government_page_url":"https://portagein.gov/547/Flock-Information-Center",
      "link_label":"FLOCK CONTRACT.pdf","review_status":"requires_document_review"}
RECEIPT={"document_url":LEAD["document_url"],"content_sha256":SHA}

class FakePage:
 def __init__(self,t):self.t=t
 def extract_text(self):return self.t
class FakeReader:
 def __init__(self,stream,strict=False):
  assert stream.read().startswith(b"%PDF-")
  self.pages=[FakePage("Flock Safety ALPR policy: retention of 30 days.")]

class PDFTriage(unittest.TestCase):
 def test_indicators_are_only_booleans_not_content_or_claims(self):
  x=M.read_metadata(PDF,FakeReader)
  self.assertEqual(x["triage_status"],"readable_document_indicators_only")
  self.assertEqual(x["pages_reported"],1)
  self.assertTrue(x["document_signal_flags"]["flock_word"])
  self.assertTrue(x["document_signal_flags"]["retention_word"])
  self.assertFalse(x["document_signal_flags"]["signature_reference_word"])
  self.assertNotIn("30",str(x))
  self.assertNotIn("policy: retention",str(x))
  self.assertNotIn("signature_date",x)
  self.assertNotIn("executed",x)
 def test_no_text_is_not_promoted(self):
  class EmptyReader:
   def __init__(self,*a,**k):self.pages=[FakePage("")]
  x=M.read_metadata(PDF,EmptyReader)
  self.assertEqual(x["triage_status"],"no_extractable_text")
  self.assertTrue(all(not v for v in x["document_signal_flags"].values()))
 def test_corrupt_pdf_held_and_large_pages_held(self):
  class ErrorReader:
   def __init__(self,*a,**k):raise ValueError("malformed")
  self.assertEqual(M.read_metadata(PDF,ErrorReader)["triage_status"],"held_parse_error")
  class TooMany:
   def __init__(self,*a,**k):self.pages=[FakePage("unknown")]*1001
  self.assertEqual(M.read_metadata(PDF,TooMany)["triage_status"],"held_page_limit")
 def test_outside_agency_original_pdf_is_excluded(self):
  invalid={**LEAD,"document_url":"https://private.example/a.pdf"}
  self.assertEqual(M.select_pending([invalid],[{"document_url":invalid["document_url"],"content_sha256":SHA}],{},NOW),[])
 def test_only_receipted_matching_bytes_are_processed(self):
  def original(url,limit):
   self.assertEqual(url,LEAD["document_url"]);return PDF,"application/pdf"
  result=M.triage([LEAD],[RECEIPT],{},original,FakeReader,NOW)
  self.assertEqual(len(result),1)
  self.assertEqual(result[0]["evidence_tier"],"automated_private_unverified_indicators")
  self.assertEqual(result[0]["content_sha256"],SHA)
  self.assertEqual(result[0]["triage_status"],"readable_document_indicators_only")
  self.assertNotIn("original_pdf_text",result[0])
  self.assertNotIn("document_content_verified",str(result[0]))
  def changed(url,limit):return PDF+b"tampered","application/pdf"
  self.assertEqual(M.triage([LEAD],[RECEIPT],{},changed,FakeReader,NOW),[])
 def test_no_repeat_except_held_after_cooldown(self):
  old={"triage_status":"readable_document_indicators_only","triaged_at":NOW.isoformat()}
  self.assertEqual(M.select_pending([LEAD],[RECEIPT],{(LEAD["document_url"],SHA):old},NOW),[])
  old["triage_status"]="held_parse_error"
  self.assertEqual(M.select_pending([LEAD],[RECEIPT],{(LEAD["document_url"],SHA):old},NOW),[])
  old["triaged_at"]=(NOW-dt.timedelta(days=8)).isoformat()
  self.assertEqual(len(M.select_pending([LEAD],[RECEIPT],{(LEAD["document_url"],SHA):old},NOW)),1)
 def test_discovery_observations_only_after_successful_page_reads(self):
  success_url=A.SEEDS[0][0]
  obs={}
  def fetcher(url,limit):
   if url==success_url:
    return b'<html>Flock Safety ALPR <a href="/policy.pdf">ALPR Policy</a></html>',"text/html"
   raise OSError("source outage")
  rows,names,ok,errors=A.scan(fetcher=fetcher,observed_pages=obs)
  self.assertEqual(ok,1)
  self.assertEqual(set(obs),{success_url})
  self.assertEqual(len(obs[success_url]["urls"]),1)
  self.assertEqual(len(errors),len(A.SEEDS)-1)
  self.assertEqual(len(rows),1)
  self.assertEqual(next(iter(rows.values()))["review_status"],"requires_document_review")
if __name__=="__main__":unittest.main()
