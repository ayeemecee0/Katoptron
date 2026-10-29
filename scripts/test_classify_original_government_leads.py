import importlib.util
import unittest
from pathlib import Path
p=Path(__file__).with_name("classify_original_government_leads.py")
s=importlib.util.spec_from_file_location("classify_original_government_leads",p)
M=importlib.util.module_from_spec(s);s.loader.exec_module(M)

def row(url,label="",kind="meeting_record",status="requires_document_review"):
 return {"document_url":url,"link_label":label,"document_class":kind,"review_status":status}

class LeadDispositions(unittest.TestCase):
 def test_generic_nav_is_rejected_without_flock_claim(self):
  result=M.classify(row("https://gov.example.gov/City-Hall/City-Council","City Council"),set(),set())
  self.assertEqual(result["disposition"],"rejected_generic_navigation")
 def test_original_pdf_bytes_not_verified_contract(self):
  url="https://city.example.gov/Docs/FLOCK-CONTRACT.pdf"
  result=M.classify(row(url,"Flock Safety Contract","contract"),{url},set())
  self.assertEqual(result["disposition"],"held_original_pdf_content_review")
  self.assertNotIn("verified",result["disposition"])
 def test_unacquired_original_has_actionable_hold(self):
  result=M.classify(row("https://city.example.gov/Doc/ALPR-policy.pdf","ALPR policy","policy"),set(),set())
  self.assertEqual(result["disposition"],"held_original_pdf_acquisition")
 def test_original_csv_needs_credentialed_verification(self):
  result=M.classify(row("https://city.example.gov/FLOCK-Access.csv","Flock recipient list","sharing_export"),set(),set())
  self.assertEqual(result["disposition"],"held_original_csv_authentication")
 def test_verified_only_with_document_content_receipt_and_explicit_status(self):
  url="https://city.example.gov/Docs/ALPR-policy.pdf"
  self.assertNotEqual(M.classify(row(url,"ALPR","policy"),{url},{url})["disposition"],"verified_original_content")
  self.assertEqual(M.classify(row(url,"ALPR","policy","document_content_verified"),{url},{url})["disposition"],"verified_original_content")
 def test_dispositions_cover_every_unique_link(self):
  a=M.classify_all([row("https://city.example.gov/council","council"),
      row("https://city.example.gov/Docs/ALPR-policy.pdf","ALPR policy","policy")],[],[])
  self.assertEqual(len(a),2)
  self.assertTrue(all(x["next_action"] for x in a))
  with self.assertRaisesRegex(ValueError,"Nonunique"):
   M.classify_all([row("https://city.example.gov/a")]*2,[],[])

if __name__=="__main__":unittest.main()
