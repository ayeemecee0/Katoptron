import importlib.util
import json
from pathlib import Path
import hashlib
import unittest
S=Path(__file__).with_name("scan_mn_historical_queue.py")
spec=importlib.util.spec_from_file_location("historical_mn_review",S)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
ROOT=S.parents[1]
MANIFEST=json.loads((ROOT/"data"/"verified-independent-audits.json").read_text())
ROW={"source_url":"https://www.lrl.mn.gov/docs/2027/mandated/270188.pdf",
 "report_id":"27-0188.pdf","report_title":"Woodbury Public Safety Department Automated License Plate Reader Audit Executive Summary",
 "publication_date":"2027-01-12","title_scope":"unspecified_alpr_title",
 "evidence_tier":"state_legislative_registry_index_metadata_only"}
PDF=b"%PDF-1.7\n"+b"x"*300
class FakeReader:
 def __init__(self,*args,**kwargs):
  self.is_encrypted=False;self.pages=[object(),object(),object()]
class TestPipeline(unittest.TestCase):
 def test_shared_js_candidate_algorithm(self):
  result=M.build([ROW],MANIFEST)
  self.assertEqual(result["candidates"][0]["priority"],"P1")
  self.assertEqual(result["candidates"][0]["jurisdiction_key"],"woodbury|MN")
  self.assertEqual(result["flock_titles_unreviewed"],0)
 def test_bounded_source_byte_receipt_has_no_claims(self):
  result=M.inspect(ROW,fetcher=lambda _:PDF,reader=FakeReader)
  self.assertEqual(result["sha256"],hashlib.sha256(PDF).hexdigest())
  self.assertEqual(result["pages"],3)
  self.assertEqual(result["examination_status"],"machine_original_receipt_only_no_page_facts")
  self.assertNotIn("report_title",result)
  self.assertNotIn("text",result)
 def test_unavailable_is_not_evidence_of_withdrawal(self):
  def fails(_):raise OSError("Original archive temporarily offline")
  result=M.scan([ROW],MANIFEST,fetcher=fails,reader=FakeReader)
  self.assertEqual(result["machine_receipts"][0]["examination_status"],"unavailable_needs_recheck")
  self.assertEqual(result["independently_published_new_facts"],0)
  self.assertEqual(result["machine_receipts"][0]["error_type"],"OSError")
  self.assertNotIn("Original archive temporarily offline",str(result))
 def test_weekly_rotation_reaches_every_lower_ranked_report(self):
  import datetime as dt
  queue={"candidates":[{"report_id":f"P0-{i}","priority":"P0"} for i in range(2)]+
         [{"report_id":f"P1-{i}","priority":"P1"} for i in range(27)]}
  weeks=[M.choose(queue,dt.date.fromisocalendar(2026,w,1)) for w in (1,2,3)]
  self.assertTrue(all(len(w)==12 for w in weeks))
  self.assertTrue(all([c["report_id"] for c in w[:2]]==["P0-0","P0-1"] for w in weeks))
  covered={c["report_id"] for group in weeks for c in group if c["priority"]=="P1"}
  self.assertEqual(len(covered),27,"No candidate must be starved by a permanent failed source")
  self.assertEqual(M.choose({"candidates":[]},dt.date(2026,10,27)),[])
 def test_no_arbitrary_host_and_unbounded_queue(self):
  with self.assertRaises(ValueError):M.inspect({**ROW,"source_url":"https://evil.example/file.pdf"},lambda _:PDF,FakeReader)
  with self.assertRaises(ValueError):M.inspect(ROW,lambda _:PDF*10000,FakeReader)
  with self.assertRaises(ValueError):M.build([ROW],MANIFEST,runner=lambda _:json.dumps({"schema_version":1,"candidates":[{"examination_status":"verified"}]}))
if __name__=="__main__":unittest.main()
