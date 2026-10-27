#!/usr/bin/env python3
import hashlib,importlib.util,json,unittest
from pathlib import Path
from pypdf import PdfWriter
from io import BytesIO
P=Path(__file__).with_name("triage_wa_ag_external_originals.py")
spec=importlib.util.spec_from_file_location("ag_external_triage",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
REG=json.loads(M.REGISTRY.read_text(encoding="utf8"))
class CheckExternalOriginals(unittest.TestCase):
 def test_saved_external_source_receipts_against_ago_snapshot(self):
  source=json.loads((M.ROOT/"data"/"wa-ag-external-policy-source-inspection.json").read_text(encoding="utf8"))
  checked=M.validate(source,REG)
  self.assertEqual(len(checked["receipts"]),25)
  self.assertEqual(sum(r["inspection_status"].startswith("original_") for r in checked["receipts"]),14)
  self.assertEqual(len({r["policy_source_url"] for r in checked["receipts"]}),24)
 def test_recheck_source_drift_does_not_promote_html_or_held(self):
  original=json.loads((M.ROOT/"data"/"wa-ag-external-policy-source-inspection.json").read_text(encoding="utf8"))
  changed=json.loads(json.dumps(original))
  pdf=next(r for r in changed["receipts"] if r["inspection_status"]=="original_pdf_text_detected")
  pdf["content_sha256"]="0"*64
  changes=M.compare_to_published(changed,original)
  self.assertIn(pdf["agency_name"],changes["pdf_original_bytes_or_pages_changed_requires_review"])
  htmlrow=next(r for r in changed["receipts"] if r["inspection_status"]=="original_html_text_detected")
  htmlrow["content_sha256"]="a"*64
  changes=M.compare_to_published(changed,original)
  self.assertIn(htmlrow["agency_name"],changes["html_wrapper_bytes_changed_recheck_leads"])
  hold=next(r for r in changed["receipts"] if r["inspection_status"].startswith("held"))
  hold.update(inspection_status="original_html_text_detected",content_sha256="b"*64,bytes=500,
   page_count=None,text_pages=0,image_pages=0,page_mentions_flock=[])
  changes=M.compare_to_published(changed,original)
  self.assertIn(hold["agency_name"],changes["previously_held_now_retrieved_requires_review"])
 def test_exact_ago_source_list_and_alias(self):
  rows=M.candidates(REG)
  self.assertEqual(len(rows),25)
  self.assertEqual(len({r["policy_source_url"] for r in rows}),24)
  king=next(x for x in rows if x["agency_name"]=="King County Sheriff's Office")
  maple=next(x for x in rows if x["agency_name"]=="Maple Valley Police Department")
  self.assertEqual(king["policy_source_url"],maple["policy_source_url"])
 def test_no_redirect_network_and_allowlisted_hosts(self):
  for url in ["https://127.0.0.1/private","http://www.pasco-wa.gov/DocumentCenter/View/71306/Chapter-4139-ALPR",
   "https://example.com/external.pdf","https://public.powerdms.com.evil.example/tree/",
   "https://www.pasco-wa.gov:443/DocumentCenter/Access","https://www.pasco-wa.gov/../private","https://www.pasco-wa.gov/Documents/x#frag",
   "https://www.pasco-wa.gov/DocumentCenter/%2e%2e/secrets"]:
   self.assertFalse(M.exact(url),url)
  self.assertTrue(M.exact("https://www.pasco-wa.gov/DocumentCenter/View/71306/Chapter-4139-ALPR"))
  self.assertEqual(M.evaluate({"agency_name":"Test","policy_source_url":"https://www.pasco-wa.gov/DocumentCenter/View/71306/Chapter-4139-ALPR","submitted_on":None},
    loader=lambda _: (_ for _ in ()).throw(ValueError("redirect_disallowed")))["inspection_status"],"held_redirect")
 def test_no_pdf_nonpdf_and_bad_html_facts(self):
  one=M.candidates(REG)[0]
  for typ,raw,state in [
   ("application/pdf",b"%PDF-1.7 malformed"+b"x"*200,"held_invalid_pdf"),
   ("text/plain",b"plain text only"*12,"held_unsupported_content"),
   ("text/html",b"<html><body></body></html>"*4,"held_empty_or_unusable")]:
   result=M.evaluate(one,loader=lambda u:(typ,raw))
   self.assertEqual(result["inspection_status"],state)
   self.assertIsNone(result["content_sha256"])
 def test_html_metadata_not_policy_confirmation(self):
  first=M.candidates(REG)[0]
  raw=b"<html><body><main>Police Department ALPR policy document Flock Safety</main>" + b" real government page"*10 +b"</body></html>"
  row=M.evaluate(first,loader=lambda u:("text/html",raw))
  self.assertEqual(row["inspection_status"],"original_html_text_detected")
  self.assertEqual(row["content_sha256"],hashlib.sha256(raw).hexdigest())
  self.assertEqual(row["page_mentions_flock"],[0])
  self.assertFalse(row["manufacturer_identity_assertion"])
  self.assertFalse(row["installed_equipment_assertion"])
 def test_unsupported_unreadable_cannot_be_published(self):
  d=M.build(REG,loader=lambda url:("text/plain",b"unknown document type"*10),workers=2,date="2026-10-27")
  self.assertEqual(len(d["receipts"]),25)
  self.assertTrue(all(row["inspection_status"]=="held_unsupported_content" for row in d["receipts"]))
  self.assertTrue(all(row["content_sha256"] is None for row in d["receipts"]))
  d["receipts"][0]["installed_equipment_assertion"]=True
  with self.assertRaisesRegex(ValueError,"evidence classification"):M.validate(d,REG)
 def test_prevent_unevidenced_source_switches(self):
  d=M.build(REG,loader=lambda url:("text/plain",b"unverified-source"*15),workers=2,date="2026-10-27")
  d["receipts"][0]["policy_source_url"]="https://www.pasco-wa.gov/another-file"
  with self.assertRaisesRegex(ValueError,"identity"):M.validate(d,REG)
 def test_blank_pdf_remains_held(self):
  w=PdfWriter();w.add_blank_page(width=320,height=320)
  buf=BytesIO();w.write(buf)
  entry=M.candidates(REG)[0]
  r=M.evaluate(entry,loader=lambda u:("application/pdf",buf.getvalue()))
  self.assertEqual(r["inspection_status"],"held_invalid_pdf")
  self.assertEqual(r["page_count"],None)
if __name__=="__main__":unittest.main()
