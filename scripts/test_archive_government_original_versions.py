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
   assert out['authenticated_before_after_original_byte_pairs']==1
   assert out['original_version_pairs'][0]['editorial_status']=='machine_text_difference_requires_editorial_check'
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
 def test_site_loading_timer_is_not_documentary_change(self):
  before=b'<!doctype html><html><body>Government original policy: no change. Loading Articles 0.003858804702</body></html>'
  after=b'<!doctype html><html><body>Government original policy: no change. Loading Articles 0.004951000213</body></html>'
  with tempfile.TemporaryDirectory() as tmp:
   cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
   (cur/"test-000.html").write_bytes(after)
   (old/"test-000.html").write_bytes(before)
   (old/"manifest.json").write_text(json.dumps({"schema_version":1,"sources":{
    "test-000":{"sha256":sha(before),"kind":"html","observed_on":"2026-10-29"}}}))
   o=A.reconcile(sample(before,after),cur,old)
   assert o["authenticated_before_after_original_byte_pairs"]==1
   assert o["machine_differences_for_human_review"]==0
   assert o["original_version_pairs"][0]["editorial_status"]=="authenticated_byte_pair_no_substantive_text_difference_identified"
 def test_original_government_site_chrome_is_not_policy_change(self):
  examples=[
   (b'<html>West Virginia Code | \xc2\xa717C-6-7A Thursday, October 29, 2026 Government policy unchanged</html>',
    b'<html>West Virginia Code | \xc2\xa717C-6-7A Friday, October 30, 2026 Government policy unchanged</html>'),
   (b'<html>Accessibility notice. 65\xc2\xb0F X Hot Key: CTRL-Q Government policy unchanged</html>',
    b'<html>Accessibility notice. 64\xc2\xb0F X Hot Key: CTRL-Q Government policy unchanged</html>')
  ]
  for before,after in examples:
   with tempfile.TemporaryDirectory() as tmp:
    cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
    (cur/"test-000.html").write_bytes(after)
    (old/"test-000.html").write_bytes(before)
    (old/"manifest.json").write_text(json.dumps({"schema_version":1,"sources":{
      "test-000":{"sha256":sha(before),"kind":"html","observed_on":"2026-10-29"}}}))
    out=A.reconcile(sample(before,after),cur,old)
    assert out["authenticated_before_after_original_byte_pairs"]==1
    assert out["machine_differences_for_human_review"]==0
 def test_forged_current_bytes_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
   (cur/"test-000.html").write_bytes(b"forged")
   with self.assertRaisesRegex(ValueError,"receipt-hash"):
    A.reconcile(sample(),cur,old)
 def test_unavailable_source_retains_last_good_bytes_and_provenance(self):
  with tempfile.TemporaryDirectory() as tmp:
   cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
   (cur/"test-000.html").write_bytes(AFTER)
   (old/"test-000.html").write_bytes(BEFORE)
   (old/"manifest.json").write_text(json.dumps({"schema_version":1,"sources":{
    "test-000":{"sha256":sha(BEFORE),"kind":"html","observed_on":"2026-10-29"}}}))
   first=A.reconcile(sample(),cur,old)
   self.assertEqual(first["new_authentic_document_version_pairs"],1)
   held=sample()
   held["receipts"][0].update({"status":"held_timeout_or_network",
    "change":"previously_retrieved_source_currently_held",
    "previous_usable_sha256":sha(AFTER),"current_observation_sha256":None})
   second=A.reconcile(held,cur,old)
   self.assertEqual(second["source_bytes_verified_and_archived"],0)
   self.assertEqual((old/"test-000.html").read_bytes(),AFTER)
   manifest=json.loads((old/"manifest.json").read_text())
   self.assertEqual(manifest["sources"]["test-000"]["sha256"],sha(AFTER))
   self.assertEqual(manifest["sources"]["test-000"]["source_url"],"https://test.gov/page")
 def test_original_version_pairs_are_immutable_and_not_repeated_findings(self):
  with tempfile.TemporaryDirectory() as tmp:
   cur=Path(tmp)/"current";old=Path(tmp)/"baseline";cur.mkdir();old.mkdir()
   (old/"test-000.html").write_bytes(BEFORE)
   (old/"manifest.json").write_text(json.dumps({"schema_version":1,"sources":{
    "test-000":{"sha256":sha(BEFORE),"kind":"html","observed_on":"2026-10-29"}}}))
   (cur/"test-000.html").write_bytes(AFTER)
   first=A.reconcile(sample(BEFORE,AFTER),cur,old)
   self.assertEqual(first["new_authentic_document_version_pairs"],1)
   (cur/"test-000.html").write_bytes(BEFORE)
   second=A.reconcile(sample(AFTER,BEFORE),cur,old)
   self.assertEqual(second["new_authentic_document_version_pairs"],1)
   (cur/"test-000.html").write_bytes(AFTER)
   third=A.reconcile(sample(BEFORE,AFTER),cur,old)
   self.assertEqual(third["new_authentic_document_version_pairs"],0)
   self.assertEqual(third["previously_seen_document_pairs_not_new_findings"],1)
   self.assertFalse(third["original_version_pairs"][0]["newly_observed_fingerprint_pair"])
   for content in (BEFORE,AFTER):
    saved=old/"versions"/"test-000"/(sha(content)+".html")
    self.assertEqual(saved.read_bytes(),content)
if __name__=="__main__":unittest.main()
