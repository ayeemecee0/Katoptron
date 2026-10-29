import importlib.util,json,unittest
from pathlib import Path
p=Path(__file__).with_name("verify_new_original_agency_html.py")
spec=importlib.util.spec_from_file_location("verify_new_original_agency_html",p)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class NewOriginals(unittest.TestCase):
 def test_all_ten_distinct_source_candidates_in_seven_states(self):
  doc=json.loads(M.CATALOG.read_text(encoding="utf8"))
  rows=[r for r in doc["sources"] if r["id"] in M.ANCHORS]
  self.assertEqual(len(rows),21)
  self.assertEqual(len({x["locality_key"] for x in rows}),21)
  self.assertEqual(len({x["state"] for x in rows}),13)
  self.assertTrue(all(M.valid(r["source_url"]) for r in rows))
  self.assertTrue(all(r["watch_category"]=="historical_research_only" for r in rows))
 def test_only_original_html_anchor_can_verify_source_statement(self):
  doc=json.loads(M.CATALOG.read_text())
  row=next(r for r in doc["sources"] if r["id"] in M.ANCHORS)
  raw=("<html><body>City official "+M.ANCHORS[row["id"]]+"</body></html>").encode()
  r=M.review(row,lambda url:raw)
  self.assertTrue(r["source_statement_verified"])
  self.assertEqual(len(r["sha256"]),64)
  bad=M.review(row,lambda url:b"<html><body>Mayor's welcome page</body></html>")
  self.assertFalse(bad["source_statement_verified"])
  self.assertEqual(bad["status"],"held_claim_anchor_changed")
 def test_refuse_host_substitution_or_fake_status(self):
  doc=json.loads(M.CATALOG.read_text())
  row=next(r for r in doc["sources"] if r["id"] in M.ANCHORS).copy()
  row["source_url"]="https://gov.example.gov.evil.invalid/flock"
  self.assertFalse(M.review(row,lambda url:b"")["source_statement_verified"])
  row["source_url"]="https://example.gov/flock"
  row["watch_category"]="government_decision"
  self.assertEqual(M.review(row,lambda url:b"")["status"],"held_source_identity")
if __name__=="__main__":unittest.main()
