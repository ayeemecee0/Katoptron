import importlib.util,unittest
from pathlib import Path
p=Path(__file__).with_name("extract_original_government_fact_candidates.py")
spec=importlib.util.spec_from_file_location("extract_original_government_fact_candidates",p)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

class FactExtraction(unittest.TestCase):
 def test_only_source_scoped_numeric_unverified_candidates(self):
  rows=M.candidates(["""Flock Safety Agreement for automated license plate readers:
   Annual proposed contract $120,000.00. Data retention is 30 days.
   Effective date 2026-08-18. External agency data sharing restrictions apply.
   Vehicle license plate 8ABC123, Officer Name and location 121 Main St."""],
   "https://city.example.gov/Docs/FLOCK-contract.pdf","a"*64)
  keys={r["fact_type"] for r in rows}
  self.assertEqual(keys,{"amount_candidate","retention_days_candidate",
    "effective_date_candidate","sharing_terms_candidate"})
  self.assertTrue(all(r["verification_status"]=="requires_independent_page_review" for r in rows))
  self.assertTrue(all("8ABC123" not in str(r) and "Officer" not in str(r) and "Main St" not in str(r) for r in rows))
 def test_document_without_vendor_anchor_never_yields_fact(self):
  self.assertEqual(M.candidates(["General city purchasing $54000; 30 days retention"],
    "https://city.example.gov/Docs/contract.pdf","b"*64),[])
 def test_invalid_hash_or_oversize_input_held(self):
  with self.assertRaises(ValueError):M.candidates(["Flock contract $12000"],"https://city.gov/a","incorrect")
  with self.assertRaises(ValueError):M.candidates(["Flock Safety"]*13,"https://city.gov/a","f"*64)
if __name__=="__main__":unittest.main()
