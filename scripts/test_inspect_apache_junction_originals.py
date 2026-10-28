import importlib.util
import io
import unittest
from pathlib import Path
from pypdf import PdfWriter

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"scripts"/"inspect_apache_junction_originals.py"
spec=importlib.util.spec_from_file_location("inspect_apache",path)
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

class ApacheOriginalSafety(unittest.TestCase):
 def test_only_exact_host_and_url(self):
  self.assertTrue(A.verified_url(A.ORIGINALS["city_clerk_ordinance_1579"]))
  self.assertFalse(A.verified_url("http://apachejunctionaz.gov/DocumentCenter/View/33565/ORD1579"))
  self.assertFalse(A.verified_url("https://apachejunctionaz.gov.evil.com/DocumentCenter/View/33429"))
  self.assertFalse(A.verified_url("https://evil.com@apachejunctionaz.gov/DocumentCenter/View/33429"))
  self.assertFalse(A.verified_url("https://apachejunctionaz.gov/DocumentCenter/View/33429#fragment"))
 def test_not_a_pdf_held(self):
  def fake(url):raise ValueError("Website returned HTML or redirect")
  result=A.investigate(fetcher=fake)
  self.assertEqual(len(result["records"]),4)
  self.assertTrue(all(r["status"]=="held_source_unavailable_or_unreviewed" for r in result["records"].values()))
  self.assertEqual(result["automatically_verified_ordinance_text"],0)
  self.assertEqual(result["automatically_verified_effective_dates"],0)
  self.assertEqual(result["automatically_published_camera_coordinates"],0)
 def test_pdf_produces_review_candidate_not_verified_policy(self):
  pdf=PdfWriter();pdf.add_blank_page(width=612,height=792)
  buf=io.BytesIO();pdf.write(buf)
  def fake(url):return buf.getvalue(),"application/pdf"
  result=A.investigate(fetcher=fake)
  self.assertEqual(len(result["records"]),4)
  self.assertTrue(all(r["pages"]==1 for r in result["records"].values()))
  self.assertTrue(all(r["status"]=="retrieved_original_requires_individual_page_review" for r in result["records"].values()))
  self.assertFalse(any(r["verified_adoption_or_effective_date"] for r in result["records"].values()))
  self.assertEqual(result["automatically_published_camera_coordinates"],0)
if __name__=="__main__":unittest.main()
