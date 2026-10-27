#!/usr/bin/env python3
import hashlib,importlib.util,json,unittest
from pathlib import Path
from pypdf import PdfWriter
from io import BytesIO
src=Path(__file__).with_name('triage_wa_ago_policy_origins.py')
spec=importlib.util.spec_from_file_location("triage_wa_policies",src)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
A="https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/"
U=A+"Abbey%20Original%20ALPR.pdf?VersionId=version0123456789"
V=A+"Brook%20Original%20ALPR.pdf?VersionId=version0123456789"
R={"source_url":"https://www.atg.wa.gov/ALPR","registrations":[
 {"agency_name":"Abbey Police Department","submitted_on":"2026-07-01","policy_links_from_official_ago_page":[U]},
 {"agency_name":"Brook Police Department","submitted_on":"2026-07-02","policy_links_from_official_ago_page":[V]},
 {"agency_name":"Other Police","submitted_on":"2026-07-03","policy_links_from_official_ago_page":["https://public.powerdms.com/tree"]}]}
class Tests(unittest.TestCase):
 def test_published_71_source_receipts_match_exact_original_registry(self):
  published=json.loads((M.ROOT/"data"/"wa-ago-original-policy-source-inspection.json").read_text(encoding="utf8"))
  real_reg=json.loads(M.REGISTRY.read_text(encoding="utf8"))
  valid=M.validate_snapshot(published,real_reg)
  self.assertEqual(len(valid["receipts"]),71)
  self.assertEqual(sum(x["inspection_status"].startswith("exact_pdf") for x in valid["receipts"]),64)
  self.assertEqual(sum(bool(x["potential_flock_term_pages"]) for x in valid["receipts"]),10)
 def test_source_changes_fail_closed_but_transient_unavailable_remains_held(self):
  obj=json.loads((M.ROOT/"data"/"wa-ago-original-policy-source-inspection.json").read_text(encoding="utf8"))
  changed=json.loads(json.dumps(obj))
  target=next(r for r in changed["receipts"] if r["inspection_status"].startswith("exact_pdf"))
  target["sha256"]="0"*64
  r=M.compare_to_published(changed,obj)
  self.assertIn(target["agency_name"],r["original_content_changed_requires_new_review"])
  transient=json.loads(json.dumps(obj))
  t=next(r for r in transient["receipts"] if r["agency_name"]==target["agency_name"])
  t.update(inspection_status="held_unreachable",sha256=None,page_count=None,bytes=None,
   searchable_text_pages=0,scanned_image_pages=0,potential_flock_term_pages=[])
  r=M.compare_to_published(transient,obj)
  self.assertIn(t["agency_name"],r["previously_retrievable_now_held"])
  self.assertFalse(r["original_content_changed_requires_new_review"])
 def test_approved_exact_ago_original_only(self):
  self.assertTrue(M.is_exact_ag_hosted(U))
  for bad in ["https://evil.example/ALPR/A.pdf?VersionId=version0123456789",
   "http://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/A.pdf?VersionId=version0123456789",
   "https://agportal-s3bucket.s3.us-west-2.amazonaws.com.evil.example/ALPR/A.pdf?VersionId=version0123456789",
   "https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/../secret.pdf?VersionId=version0123456789",
   "https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/A.pdf",
   "https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/A.pdf?VersionId=tooShort",
   "https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/A.pdf?VersionId=version0123456789#page=1"]:
   self.assertFalse(M.is_exact_ag_hosted(bad),bad)
  self.assertEqual(len(M.candidates(R)),2)
 def test_duplicate_identity_rejected(self):
  v={**R,"registrations":R["registrations"]+[R["registrations"][0]]}
  with self.assertRaisesRegex(ValueError,"Duplicate"):M.candidates(v)
 def test_failed_url_and_non_pdf_cannot_create_verified_original(self):
  rows=M.candidates(R)
  d=M.build(R,workers=2,date="2026-10-27",fetcher=lambda u:b"<html>Not an original policy PDF</html>"*9)
  self.assertEqual(len(d["receipts"]),2)
  self.assertTrue(all(r["inspection_status"]=="held_non_pdf" for r in d["receipts"]))
  self.assertTrue(all(r["sha256"] is None and not r["potential_flock_term_pages"] for r in d["receipts"]))
  with self.assertRaisesRegex(ValueError,"Failed PDF"):
   M.validate_snapshot({**d,"receipts":[{**d["receipts"][0],"sha256":"0"*64}]+d["receipts"][1:]},R)
 def test_real_pypdf_blank_page_does_not_become_false_scanned_review(self):
  w=PdfWriter();w.add_blank_page(width=300,height=300)
  buf=BytesIO();w.write(buf);raw=buf.getvalue()
  d=M.build(R,workers=2,date="2026-10-27",fetcher=lambda u:raw)
  self.assertTrue(all(r["inspection_status"]=="held_unreadable_pdf" for r in d["receipts"]))
 def test_wrong_policy_order_or_forged_vendor_rejected(self):
  d=M.build(R,workers=1,date="2026-10-27",fetcher=lambda u:b"NO DATA"*50)
  with self.assertRaisesRegex(ValueError,"wrongly attributed"):
   M.validate_snapshot({**d,"receipts":list(reversed(d["receipts"]))},R)
  with self.assertRaisesRegex(ValueError,"Forged"):
   M.validate_snapshot({**d,"receipts":[{**d["receipts"][0],"manufacturer_identity_assertion":True}]+d["receipts"][1:]},R)
 def test_redirect_held(self):
  d=M.build(R,workers=1,date="2026-10-27",fetcher=lambda u:(_ for _ in ()).throw(ValueError("redirect")))
  self.assertTrue(all(r["inspection_status"]=="held_redirect" for r in d["receipts"]))
 def test_no_raw_policy_text_published(self):
  d=M.build(R,workers=1,date="2026-10-27",fetcher=lambda u:b"bad"*100)
  self.assertTrue(all("source_text" not in r and "page_content" not in r for r in d["receipts"]))
if __name__=="__main__":unittest.main()
