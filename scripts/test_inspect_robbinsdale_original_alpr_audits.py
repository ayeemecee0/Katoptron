#!/usr/bin/env python3
import importlib.util,io,unittest
from pathlib import Path
from pypdf import PdfWriter
P=Path(__file__).with_name("inspect_robbinsdale_original_alpr_audits.py")
sp=importlib.util.spec_from_file_location("audit_sources",P)
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
class TestAudit(unittest.TestCase):
 def test_independent_originals_separate(self):
  self.assertEqual(set(M.ORIGINALS),{"flock_2025","axon_2026"})
  self.assertTrue(all(x.startswith("https://www.lrl.mn.gov/docs/") for x in M.ORIGINALS.values()))
  self.assertNotEqual(M.ORIGINALS["flock_2025"],M.ORIGINALS["axon_2026"])
  self.assertIn("flock",M.ANCHORS["flock_2025"][2][0])
  self.assertIn("axon",M.ANCHORS["axon_2026"][2][0])
 def test_invalid_or_blank_pdf_not_verified(self):
  with self.assertRaises(ValueError):M.inspect("unknown",b"%PDF-1.4")
  w=PdfWriter()
  for _ in range(5):w.add_blank_page(width=612,height=792)
  b=io.BytesIO();w.write(b)
  with self.assertRaisesRegex(ValueError,"page anchor"):
   M.inspect("flock_2025",b.getvalue())
  short=PdfWriter();short.add_blank_page(width=612,height=792)
  b=io.BytesIO();short.write(b)
  with self.assertRaisesRegex(ValueError,"page count"):
   M.inspect("flock_2025",b.getvalue())
if __name__=="__main__":unittest.main()
