#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
P=Path(__file__).with_name('inspect_okc_2026_contract_originals.py')
spec=importlib.util.spec_from_file_location('okc_originals',P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class SourceBoundOriginal(unittest.TestCase):
 def test_five_exact_original_government_pdfs(self):
  self.assertEqual(len(M.SOURCES),5)
  self.assertEqual(len(set(x[0] for x in M.SOURCES.values())),5)
  self.assertTrue(all(not fn.startswith("/") and fn.endswith(".pdf") and size<=8_000_000 for fn,size in M.SOURCES.values()))
 def test_reject_unlisted_document_identity(self):
  with self.assertRaises(ValueError):M.retrieve('forged-unapproved-original')
  with self.assertRaises(ValueError):M.inspect('forged-unapproved-original',b'%PDF-1.7')
 def test_non_pdf_and_empty_held(self):
  with self.assertRaises(ValueError):M.inspect('okc-2026-flock-council-memo',b'<html>not a pdf</html>')
if __name__=="__main__":unittest.main()
