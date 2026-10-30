#!/usr/bin/env python3
"""Deterministic all-state source continuity, gaps and fail-closed regression."""
import hashlib,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 path=ROOT/"scripts"/(name+".py")
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module
M=load("nationwide_source_health");G=load("watch_nationwide_government_originals")
R=json.loads(G.REGISTRY.read_text());OLD=json.loads(G.EXISTING.read_text())
BASE=json.loads(M.BUILTIN.read_text())
j,seeds,_=G.catalog(R,OLD)
all_sources=seeds+G.legacy_sources(OLD)+G.recovery_sources()+G.agency_depth_sources()
def fake(status="original_government_html_accessible"):
 rows=[]
 for i,s in enumerate(all_sources):
  kind=s["kind"];status1=("original_government_pdf_accessible" if kind=="pdf" else status)
  rows.append({"source_id":s["id"],"state":s["state"],"source_url":s["source_url"],"kind":kind,
    "status":status1,"original_sha256":hashlib.sha256(s["id"].encode()).hexdigest(),"pdf_pages":2 if kind=="pdf" else None})
 return {"jurisdictions_total":51,"all_source_receipts":rows}
class Monitor(unittest.TestCase):
 def test_monitor_all_50_states_and_dc_not_just_new_urls(self):
  self.assertEqual(len(all_sources),81)
  run=fake();a,b=M.continuity(run,R,OLD,BASE)
  self.assertEqual(a["jurisdictions_monitored"],51)
  self.assertEqual(b["monitored_urls"],81)
  self.assertEqual(len(b["states"]),51)
  self.assertTrue(all(x["originals_monitored"]>=1 for x in b["states"]))
  self.assertTrue(all(x["statewide_flock_adoption_verified"] is False for x in b["states"]))
  self.assertEqual(b["source_verified_contract_changes"],0)
  self.assertIn("DC",{s["state"] for s in b["states"]})
  self.assertEqual(b["accessible_origins"],81)
  self.assertGreater(b["first_baselines_pending_individual_review"],0)
 def test_changed_source_is_review_lead_not_enacted_policy(self):
  a,b=M.continuity(fake(),R,OLD,BASE)
  follow=fake();follow["all_source_receipts"][0]["original_sha256"]="f"*64
  snap,health=M.continuity(follow,R,OLD,a,day="2026-11-01")
  self.assertEqual(health["source_hash_changes_pending_individual_review"],1)
  self.assertEqual(snap["verified_new_contract_or_policy_claims"],0)
  self.assertEqual(snap["automatic_camera_or_sharing_publications"],0)
  self.assertEqual(snap["receipts"][0]["change"],"source_bytes_changed_review_required")
  self.assertEqual(health["states"][0]["state"],"AL")
 def test_held_preserves_last_success_does_not_falsely_claim_unchanged(self):
  a,_=M.continuity(fake(),R,OLD,BASE,day="2026-10-29")
  run=fake();row=run["all_source_receipts"][0]
  row["status"]="held_timeout_or_network";row["original_sha256"]=None
  out,health=M.continuity(run,R,OLD,a,day="2026-11-01")
  self.assertEqual(out["receipts"][0]["last_usable_sha256"],a["receipts"][0]["last_usable_sha256"])
  self.assertEqual(out["receipts"][0]["last_usable_on"],"2026-10-29")
  self.assertEqual(out["receipts"][0]["change"],"previously_retrieved_source_currently_held")
  self.assertIn("al-city-council-agenda",health["states"][0]["held_original_source_ids"])
  self.assertEqual(health["states"][0]["documented_gap"],"no_accessible_curated_government_original")
 def test_all_sources_held_still_nationally_enrolled_not_coverage_verified(self):
  run=fake()
  for x in run["all_source_receipts"]:
   x["status"]="held_http_error";x["original_sha256"]=None
  s,h=M.continuity(run,R,OLD,BASE)
  self.assertEqual(h["held_origins"],81)
  self.assertTrue(all(x["documented_gap"]=="no_accessible_curated_government_original" for x in h["states"]))
  self.assertTrue(all(x["statewide_camera_locations_verified"] is False for x in h["states"]))
 def test_removed_or_redirected_and_malformed_sources_fail(self):
  r=fake();r["all_source_receipts"].pop()
  with self.assertRaisesRegex(ValueError,"Missing monitored"):M.continuity(r,R,OLD,BASE)
  r=fake();r["all_source_receipts"][0]["source_url"]="https://attacker.example/changed"
  with self.assertRaisesRegex(ValueError,"provenance mismatch"):M.continuity(r,R,OLD,BASE)
  r=fake();r["all_source_receipts"][0]["status"]="newly_verified_contract"
  with self.assertRaisesRegex(ValueError,"classified"):M.continuity(r,R,OLD,BASE)
  r=fake();r["all_source_receipts"][0]["status"]="held_http_error"
  with self.assertRaisesRegex(ValueError,"Held source"):M.continuity(r,R,OLD,BASE)
 def test_legacy_custom_municipal_hosts_are_strictly_approved(self):
  for host in ["https://www.moline.il.us/1955/License-Plate-Readers",
   "https://www.naperville.il.us/services/police",
   "https://www.darien.il.us/reference-desk/news/"]:
   self.assertTrue(G.exact(host))
  for url in ["https://www.moline.il.us.evil.example/policy",
   "https://malicious.il.us/policy","http://www.moline.il.us/test",
   "https://127.0.0.1/admin","https://www.example.gov:4443/test"]:
   self.assertFalse(G.exact(url),url)
if __name__=="__main__":unittest.main()
