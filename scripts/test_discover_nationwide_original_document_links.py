#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("discover_nationwide_original_document_links.py")
spec=importlib.util.spec_from_file_location("nationwide_government_links",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
R=json.loads(M.REGISTRY.read_text(encoding="utf8"))
B=json.loads(M.PREVIOUS.read_text(encoding="utf8"))
HTML=b'''<!doctype html><html><body>
<a href="/DocumentCenter/View/22/Flock-Safety-Contract.pdf">Flock Safety signed contract</a>
<a href="/p/alpr-audit-report">ALPR independent audit report</a>
<a href="/p/raw-alpr-search-logs">Raw ALPR search logs</a>
<a href="https://evil.example/contract.pdf">Flock Safety contract</a>
<a href="https://www.siloamsprings.gov.evil.example/contract.pdf">Flock policy</a>
<a href="../secrets/flock-contract.pdf">Flock contract</a>
<a href="/about">City government home page</a>
<a href="/DocumentCenter/View/22/Flock-Safety-Contract.pdf">duplicate link</a>
</body></html>'''
class AllStatesOriginalLinkTests(unittest.TestCase):
 def test_registered_source_page_original_link_provenance(self):
  src=next(s for s in R["official_seed_sources"] if s["kind"]=="html" and s["state"]=="AR")
  rows=M.extract(src,HTML)
  self.assertEqual(len(rows),2)
  self.assertTrue(all(x["candidate_url"].startswith("https://www.siloamsprings.gov/") for x in rows))
  self.assertTrue(all(x["original_document_fetched"] is False and x["flock_installed"] is False for x in rows))
  self.assertTrue(all(x["publication_status"]=="unverified_link_needs_individual_original_content_review" for x in rows))
  self.assertTrue(all("raw-alpr-search-logs" not in x["candidate_url"] for x in rows))
 def test_offhost_private_sensitive_and_traversal_rejected(self):
  src=next(s for s in R["official_seed_sources"] if s["state"]=="AR")
  for u in ["http://rva.gov/test","https://www.siloamsprings.gov.evil.example/bad",
    "https://www.siloamsprings.gov/../sensitive","https://www.siloamsprings.gov/%2e%2e/sensitive",
    "https://www.siloamsprings.gov/private-search-logs","https://evil.example/flock"]:
   self.assertIsNone(M.exact_related(u,src),u)
 def test_51_jurisdiction_link_scanner_only_unverified_metadata(self):
  rows=M.scan(R,B,fetcher=lambda s:HTML,workers=3)
  self.assertEqual(rows["jurisdictions_enrolled"],51)
  self.assertEqual(rows["original_government_seeds_checked"],45)
  self.assertEqual(sum(x["status"]=="new_publisher_original_receipt_required"
    for x in rows["source_checks"]),2)
  self.assertGreaterEqual(rows["html_originals_link_scanned"],25)
  self.assertTrue(all(x["flock_installed"] is False and x["policy_adopted"] is False and x["original_document_fetched"] is False for x in rows["candidate_links"]))
 def test_original_upstream_unavailable_does_not_infer_no_flock(self):
  result=M.scan(R,B,fetcher=lambda s:(_ for _ in ()).throw(ValueError("unreachable")),workers=4)
  self.assertEqual(len(result["candidate_links"]),0)
  self.assertEqual(result["html_originals_link_scanned"],0)
  self.assertTrue(all(x["status"]!="read_only_official_html_links_examined" for x in result["source_checks"]))
 def test_corrupted_original_registry_fails_closed(self):
  broken=json.loads(json.dumps(B));broken["receipts"][0]["source_url"]="https://evil.example/a"
  with self.assertRaisesRegex(ValueError,"provenance mismatch"):M.scan(R,broken,fetcher=lambda _:HTML)
 def test_topic_limited_no_inferred_vendor_document(self):
  src=next(s for s in R["official_seed_sources"] if s["state"]=="AR")
  html=b'<html><a href="/files/1.pdf">Financial report</a><a href="/police/flock-privacy-policy">Flock privacy policy</a></html>'
  result=M.extract(src,html)
  self.assertEqual(len(result),1)
  self.assertIn("flock-privacy-policy",result[0]["candidate_url"])
if __name__=="__main__":unittest.main()
