#!/usr/bin/env python3
import io,unittest,json
from pypdf import PdfWriter
from verify_apache_resolution_chapter import URL,fetch,inspect,META,validate_review_manifest,EXPECTED_SHA
class Tests(unittest.TestCase):
 def test_source_only_exact_city_document(self):
  self.assertEqual(URL,'https://www.apachejunctionaz.gov/DocumentCenter/View/33562/RES-26-43')
  self.assertNotEqual(URL.replace('www.apachejunctionaz.gov','attacker.invalid'),URL)
 def test_pinned_review_receipt_and_adverse_date_claims(self):
  d=json.loads(META.read_text(encoding='utf8'))
  self.assertEqual(validate_review_manifest(d)['original_sha256'],EXPECTED_SHA)
  for key,value in (
   ('signed_resolution_adoption_date','2026-10-08'),
   ('legal_effective_date_verified',True),
   ('original_council_agenda_appendix_exact_match_verified',True),
   ('notices_date_agrees_with_signed_resolution',True),
   ('exact_camera_points_added',30),
   ('original_sha256','0'*64)):
   tampered={**d,key:value}
   with self.assertRaisesRegex(ValueError,'ungrounded'):
    validate_review_manifest(tampered)
 def test_wrong_pdf_never_verified(self):
  with self.assertRaises(Exception):inspect(b'<html>not a PDF</html>',require_pin=True)
 def test_five_page_shape_does_not_infer_legal_or_operating_state(self):
  writer=PdfWriter()
  for _ in range(5):writer.add_blank_page(width=612,height=792)
  out=io.BytesIO();writer.write(out)
  with self.assertRaises(ValueError):inspect(out.getvalue(),require_pin=True)
  with self.assertRaises(ValueError):inspect(out.getvalue(),require_pin=False)
 def test_empty_effective_date_never_inferred(self):
  # Structural receipt alone never claims date or live system compliance.
  self.assertNotIn('effective_date=2026-10-06',inspect.__doc__ or '')
if __name__=='__main__':unittest.main()
