#!/usr/bin/env python3
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
P=Path(__file__).resolve().parent/"archive_government_original_versions.py"
spec=importlib.util.spec_from_file_location("archive_originals",P)
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
sha=lambda b:hashlib.sha256(b).hexdigest()
BEFORE=b"<!doctype html><html><body>Official original government policy: searches require valid case.</body></html>"
AFTER=b"<!doctype html><html><body>Official original government policy: searches require case, supervisor approval, and audit.</body></html>"
def sample(before=BEFORE,after=AFTER):
 rows=[{"source_id":"test-"+str(i).zfill(3),"kind":"html","state":"CA",
   "source_url":"https://test.gov/page","status":"held_http_error","change":"source_unavailable_no_verified_baseline",
   "previous_usable_sha256":None,"current_observation_sha256":None} for i in range(100)]
 rows[0].update({"status":"original_government_html_accessible",
   "change":"source_bytes_changed_review_required",
   "previous_usable_sha256":sha(before),"current_observation_sha256":sha(after)})
 return {"schema_version":2,"observed_on":"2026-10-30","receipts":rows}
class OriginalArchiveTests(unittest.TestCase):
 def test_content_verified_and_unapproved_diff(self):
  with tempfile.TemporaryDirectory() as tmp:
   cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
   (cur/"test-000.html").write_bytes(AFTER)
   (old/"test-000.html").write_bytes(BEFORE)
   (old/"manifest.json").write_text(json.dumps({"schema_version":1,"sources":{
    "test-000":{"sha256":sha(BEFORE),"kind":"html","observed_on":"2026-10-29"}}}))
   out=A.reconcile(sample(),cur,old)
   assert out["source_bytes_verified_and_archived"]==1
   assert out["machine_differences_for_human_review"]==1
   assert out["automatic_editorial_approvals"]==0
   c=out["original_version_pairs"][0]
   assert c["machine_page_candidates"][0]["page"]==1
   assert "supervisor" in c["machine_page_candidates"][0]["after_excerpt"]
   assert c["verified_documentary_policy_change"] is False
   assert (old/"test-000.html").read_bytes()==AFTER
 def test_prior_bytes_missing_or_tampered_are_holds(self):
  with tempfile.TemporaryDirectory() as tmp:
   cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
   (cur/"test-000.html").write_bytes(AFTER)
   out=A.reconcile(sample(),cur,old)
   assert out["machine_differences_for_human_review"]==0
   assert out["original_version_pairs"][0]["editorial_status"]=="held_missing_authentic_prior_document_bytes"
 def test_forged_current_bytes_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
   (cur/"test-000.html").write_bytes(b"forged")
   with self.assertRaisesRegex(ValueError,"receipt-hash"):
    A.reconcile(sample(),cur,old)
if __name__=="__main__":unittest.main()
