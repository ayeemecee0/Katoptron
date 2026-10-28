#!/usr/bin/env python3
import io,unittest
from pypdf import PdfWriter
from verify_apache_resolution_chapter import URL,fetch,inspect
class Tests(unittest.TestCase):
 def test_source_only_exact_city_document(self):
  self.assertEqual(URL,'https://www.apachejunctionaz.gov/DocumentCenter/View/33562/RES-26-43')
  self.assertNotEqual(URL.replace('www.apachejunctionaz.gov','attacker.invalid'),URL)
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
