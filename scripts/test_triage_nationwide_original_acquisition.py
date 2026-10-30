#!/usr/bin/env python3
import copy,importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("triage",P/"triage_nationwide_original_acquisition.py")
T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
def fixture():
    objs=[json.loads(p.read_text(encoding="utf8")) for p in (T.REGISTRY,T.LEGACY,T.RECOVERY,T.DEPTH)]
    registry=objs[0]
    discovery={"schema_version":1,"states_enrolled":51,"states":[
        {"state":r["state"],"discovery_status":"public_search_completed_leads_unverified","search_leads":[]}
        for r in registry["jurisdictions"]]}
    return discovery,objs
class AcquisitionTriage(unittest.TestCase):
    def test_all_states_and_priority_without_fact_upgrade(self):
        discovery,parts=fixture()
        s=discovery["states"][0];s["search_leads"]=[{
            "candidate_original_url":"https://www.newexample.gov/public/flock-alpr-policy",
            "title":"Flock ALPR policy records",
            "original_document_content_reviewed":False,
            "flock_equipment_confirmed":False,"state_relevance_confirmed":False}]
        out=T.prioritize(discovery,*parts)
        self.assertEqual(out["states"],51)
        self.assertEqual(out["new_unreviewed_candidates"],1)
        self.assertEqual(len(out["ready_for_review"]),1)
        item=out["ready_for_review"][0]
        self.assertFalse(item["eligible_for_publication"])
        self.assertFalse(item["publisher_identity_verified"])
        self.assertFalse(item["source_version_difference_verified"])
        self.assertEqual(out["automatic_watch_events_sent"],0)
        self.assertTrue(all(r["inventory_complete"] is False for r in out["state_gaps"]))
    def test_unsafe_sensitive_and_duplicate_sources_held(self):
        discovery,parts=fixture()
        lead=lambda url,title="Flock ALPR policy report":{
            "candidate_original_url":url,"title":title,
            "original_document_content_reviewed":False,
            "flock_equipment_confirmed":False,"state_relevance_confirmed":False}
        existing=list(T.existing_urls(*parts).keys())[0]
        discovery["states"][0]["search_leads"]=[
          lead("https://evil.example/flock"),lead("https://www.example.gov/raw-plate-reads"),
          lead(existing),lead("https://www.valid.gov/public/flock-alpr-policy"),
          lead("https://www.valid.gov/public/flock-alpr-policy"),
          lead("https://www.valid.gov/public/not-relevant","Council agenda")]
        out=T.prioritize(discovery,*parts)
        self.assertEqual(out["new_unreviewed_candidates"],1)
        self.assertEqual(out["state_gaps"][0]["duplicates_or_invalid_held"],5)
    def test_reject_unreviewed_claim_promotion(self):
        discovery,parts=fixture()
        discovery["states"][0]["search_leads"]=[{
            "candidate_original_url":"https://www.valid.gov/flock-policy","title":"Flock ALPR policy",
            "original_document_content_reviewed":True,
            "flock_equipment_confirmed":False,"state_relevance_confirmed":False}]
        self.assertEqual(T.prioritize(discovery,*parts)["new_unreviewed_candidates"],0)
        discovery["states"].pop()
        with self.assertRaisesRegex(ValueError,"Complete"):T.prioritize(discovery,*parts)
    def test_provider_failure_not_zero_government_activity(self):
        discovery,parts=fixture()
        discovery["states"][0]["discovery_status"]="search_provider_unavailable_retry_needed"
        out=T.prioritize(discovery,*parts)
        self.assertEqual(out["state_gaps"][0]["search_status"],"search_provider_unavailable_retry_needed")
        self.assertIn("unavailable",out["limitation"])
if __name__=="__main__":unittest.main()
