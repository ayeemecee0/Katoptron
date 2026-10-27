#!/usr/bin/env python3
"""Nationwide source acquisition must never masquerade as nationwide Flock coverage."""
import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("watch_nationwide_government_originals.py")
spec=importlib.util.spec_from_file_location("nationwide_original_watch",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
R=json.loads(M.REGISTRY.read_text(encoding="utf8"))
OLD=json.loads(M.EXISTING.read_text(encoding="utf8"))
class StateSources(unittest.TestCase):
 def test_every_state_and_dc_research_queue_distinct(self):
  j,seeds,p=M.catalog(R,OLD)
  self.assertEqual(len(j),51)
  self.assertEqual(len({s["state"] for s in j}),51)
  self.assertIn("DC",{s["state"] for s in j})
  self.assertEqual(len(seeds),43)
  self.assertEqual(len(p),8)
  self.assertEqual(len({s["state"] for s in seeds}|p),51)
 def test_ssrf_origins_and_path_escape_rejected(self):
  approved="https://www.okc.gov/Services/Public-Safety/Police/Flock-Safety-license-plate-reader-LPR-usage-in-Oklahoma-City"
  self.assertTrue(M.exact(approved))
  for url in ["http://www.okc.gov/test",
   "https://evil.example/Flock", "https://www.okc.gov.evil.example/path",
   "https://www.okc.gov:8443/path","https://127.0.0.1/admin",
   "https://www.okc.gov/../internal","https://www.okc.gov/%2e%2e/private",
   "https://www.okc.gov/path#fragment","https://www.okc.gov\\@evil.example/path"]:
   self.assertFalse(M.exact(url),url)
 def test_html_source_is_receipt_not_agency_fact(self):
  row=next(x for x in R["official_seed_sources"] if x["kind"]=="html")
  text=b"<html><body>Flock Safety ALPR transparency document</body></html>"*5
  receipt=M.inspect(row,fetcher=lambda _:text)
  self.assertEqual(receipt["status"],"original_government_html_accessible")
  self.assertTrue(receipt["publisher_flock_keyword_seen"])
  self.assertIsNotNone(receipt["original_sha256"])
  for f in ("published_facts_verified","device_status_verified","camera_coordinates_published"):
   self.assertIs(receipt[f],False)
 def test_pdf_original_and_wrong_format(self):
  p=next(x for x in R["official_seed_sources"] if x["kind"]=="pdf")
  bad=M.inspect(p,fetcher=lambda _:b"<html><body>Flock</body></html>"*9)
  self.assertEqual(bad["status"],"held_wrong_format")
  self.assertIsNone(bad["original_sha256"])
 def test_transient_unavailable_never_counts_as_source_or_cameras(self):
  def denied(x):raise ValueError("original_redirect")
  result=M.watch(R,OLD,fetcher=denied,workers=3)
  self.assertEqual(result["jurisdictions_total"],51)
  self.assertEqual(result["states_with_existing_or_new_official_seed_sources"],51)
  self.assertEqual(len(result["seed_receipts"]),len(R["official_seed_sources"]))
  self.assertTrue(all(x["status"]=="held_redirect" for x in result["seed_receipts"]))
  self.assertTrue(all(x["camera_coverage_claimed"] is False and x["agency_inventory_complete"] is False for x in result["jurisdictions"]))
  self.assertEqual(result["states_without_official_sources_seeded"],[])
  self.assertTrue(all(x["source_gap"]=="publisher_monitoring_started_not_statewide_evidence_complete" for x in result["jurisdictions"]))
 def test_source_change_and_missing_state_fail_closed(self):
  altered=json.loads(json.dumps(R));altered["jurisdictions"].pop()
  with self.assertRaisesRegex(ValueError,"complete"):M.catalog(altered,OLD)
  altered=json.loads(json.dumps(R));altered["official_seed_sources"][0]["source_url"]="https://private.example/path"
  with self.assertRaisesRegex(ValueError,"Ungrounded"):M.catalog(altered,OLD)
  altered=json.loads(json.dumps(R));altered["official_seed_sources"][0]["origin_role"]="verified_operational_flock"
  with self.assertRaisesRegex(ValueError,"Ungrounded"):M.catalog(altered,OLD)
if __name__=="__main__":unittest.main()
