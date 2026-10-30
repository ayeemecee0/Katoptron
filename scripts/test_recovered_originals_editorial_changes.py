#!/usr/bin/env python3
"""Publisher integrity, newly restored URL, and documentary difference safety gates."""
import copy,hashlib,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 p=ROOT/"scripts"/(name+".py")
 spec=importlib.util.spec_from_file_location(name,p)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m
G=module("watch_nationwide_government_originals")
D=module("review_nationwide_source_changes")
class Recovery(unittest.TestCase):
 def test_11_individually_located_government_originals_are_not_operational_proof(self):
  rows=G.recovery_sources()
  self.assertEqual(len(rows),11)
  self.assertEqual({r["state"] for r in rows},set("CO FL HI IA MI MS NC NV NY UT WV".split()))
  self.assertTrue(all(G.exact(r["source_url"]) for r in rows))
  self.assertTrue(all(r["origin_role"]=="supplemental_government_publisher_individual_claims_unverified" for r in rows))
  doc=json.loads(G.RECOVERY.read_text())
  self.assertTrue(all(r["operational_camera_verified"] is False and
      r["executed_contract_verified"] is False and r["original_document_version_change_verified"] is False
      for r in doc["original_source_recovery_candidates"]))
 def test_unapproved_domain_and_status_fail_closed(self):
  data=json.loads(G.RECOVERY.read_text())
  data["original_source_recovery_candidates"][0]["source_url"]="https://attacker.gov.evil.example/"
  with self.assertRaises(ValueError):G.recovery_sources(data)
  data=json.loads(G.RECOVERY.read_text())
  data["original_source_recovery_candidates"][0]["operational_camera_verified"]=True
  with self.assertRaises(ValueError):G.recovery_sources(data)
 def test_supplemental_receipts_are_separate_from_old_45_source_seeds(self):
  reg=json.loads(G.REGISTRY.read_text());legacy=json.loads(G.EXISTING.read_text())
  def down(_):raise ValueError("http_error")
  data=G.watch(reg,legacy,fetcher=down,workers=2)
  self.assertEqual(len(data["seed_receipts"]),45)
  self.assertEqual(len(data["legacy_receipts"]),14)
  self.assertEqual(len(data["recovery_receipts"]),11)
  self.assertEqual(len(data["depth_receipts"]),11)
  self.assertEqual(data["monitored_sources_total"],81)
  self.assertEqual(data["verified_policy_adoptions_published"],0)
  self.assertTrue(all(x["camera_coverage_claimed"] is False for x in data["jurisdictions"]))
 def test_review_requires_actual_changed_page_and_two_original_documents(self):
  src=G.recovery_sources()[1]
  before="a"*64;after="b"*64
  snapshot={"schema_version":2,"observed_on":"2026-10-29","receipts":[{
   "source_id":src["id"],"state":src["state"],"source_url":src["source_url"],
   "change":"source_bytes_changed_review_required","previous_usable_sha256":before,
   "current_observation_sha256":after}]}
  empty={"schema_version":1,"approvals":[]}
  queue,approved=D.review(snapshot,empty)
  self.assertEqual(queue["changed_publisher_pages"],1)
  self.assertEqual(queue["approved_original_document_differences"],0)
  self.assertEqual(queue["unreviewed_claims_automatically_published"],0)
  self.assertEqual(len(approved),0)
  row={"source_id":src["id"],"before_sha256":before,"after_sha256":after,
    "before_original_url":"https://example.gov/official/earlier.pdf",
    "after_original_url":"https://example.gov/official/later.pdf",
    "before_pdf_page":2,"after_pdf_page":3,
    "before_excerpt":"The 2025 original document states an explicitly limited authorization.",
    "after_excerpt":"The 2026 original document describes a changed and dated authorization.",
    "reviewer":"Named government document editorial reviewer",
    "reviewed_on":"2026-10-29 original version comparison",
    "government_issuer":"Original publisher identity confirmed from its independent government homepage",
    "legal_status_caveat":"Document wording differs; execution, effectiveness and operation were not determined",
    "why_significant":"A documented original-source wording change merits further records and interview followup",
    "unverified_questions":"Which later documents prove effective policy, financial expenditure or contract execution?",
    "title":"Dated original publisher wording difference requiring investigation",
    "category":"contract_text_difference",
    "editorial_approved":True,"not_proof_of_misconduct":True}
  queue,approved=D.review(snapshot,{"schema_version":1,"approvals":[row]})
  self.assertEqual(len(approved),1)
  self.assertIn("#page=2",approved[0]["before"]["government_url"])
  self.assertTrue(approved[0]["automatically_approved_wrongdoing"] is False)
  altered=copy.deepcopy(row);altered["before_sha256"]="c"*64
  with self.assertRaisesRegex(ValueError,"hashes"):D.review(snapshot,{"schema_version":1,"approvals":[altered]})
  altered=copy.deepcopy(row);altered["after_original_url"]=row["before_original_url"]
  with self.assertRaisesRegex(ValueError,"Permanent"):D.review(snapshot,{"schema_version":1,"approvals":[altered]})
  altered=copy.deepcopy(row);altered["category"]="installed_camera_now"
  with self.assertRaisesRegex(ValueError,"Unsupported"):D.review(snapshot,{"schema_version":1,"approvals":[altered]})
  altered=copy.deepcopy(row);altered["editorial_approved"]=False
  with self.assertRaisesRegex(ValueError,"Human editorial"):D.review(snapshot,{"schema_version":1,"approvals":[altered]})
 def test_real_repository_approval_registry_is_empty_until_review(self):
  approvals=json.loads(D.APPROVALS.read_text())
  self.assertEqual(len(approvals["approvals"]),0)
if __name__=="__main__":unittest.main()
