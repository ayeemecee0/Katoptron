import importlib.util
import unittest
from pathlib import Path

P=Path(__file__).with_name("acquire_original_government_documents.py")
spec=importlib.util.spec_from_file_location("gov_acquisition",P)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

class GovDocumentAcquisition(unittest.TestCase):
 def test_original_government_page_link_evidence_and_no_content_claims(self):
  page=b'''<html><h1>Flock Safety ALPR Information</h1>
  <a href="/DocumentCenter/View/10/ALPR-Policy.pdf">ALPR Policy Updated.pdf</a>
  <a href="/DocumentCenter/View/11/Shared-Flock-2026.csv">Shared Flock 2026.csv</a>
  <a href="/DocumentCenter/View/12/Flock-contract.pdf">Signed Flock contract.pdf</a>
  <a href="https://private.example/records">Download all records</a>
  <a href="http://portagein.gov/elsewhere.pdf">Insecure document</a>
  <a href="https://other-town.gov/policy.pdf">Other city policy</a>
  </html>'''
  r=M.extract_links(page,"https://portagein.gov/547/Flock-Information-Center","Portage, IN")
  self.assertEqual(len(r),3)
  classes={x["document_class"] for x in r}
  self.assertEqual(classes,{"policy","sharing_export","contract"})
  for row in r:
   self.assertEqual(row["confidence"],"original_government_link_only")
   self.assertEqual(row["review_status"],"requires_document_review")
   self.assertEqual(row["government_page_url"],"https://portagein.gov/547/Flock-Information-Center")
   self.assertTrue(row["document_url"].startswith("https://portagein.gov/"))
   self.assertNotIn("amount_usd",row)
   self.assertNotIn("event_date",row)
   self.assertNotIn("latitude",row)
 def test_csv_narrow_names_not_alpr_logs(self):
  self.assertEqual(M.csv_recipient_names(b'Agency Name,Other\nFolsom CA PD,one\nRoseville CA PD,two\n'),
      ["Folsom CA PD","Roseville CA PD"])
  self.assertEqual(M.csv_recipient_names(b'plate,agency name\nABC123,Folsom CA PD\n'),[])
  self.assertEqual(M.csv_recipient_names(b'queried timestamp,search\n2026,a\n'),[])
  self.assertEqual(M.csv_recipient_names(b'name,other\nA,1\n'),[])
 def test_cross_domain_or_nonpublic_urls_not_followed(self):
  root="https://portagein.gov/alpr"
  self.assertIsNone(M.normalize_url("https://evil.example/fake.pdf",root,"portagein.gov"))
  self.assertIsNone(M.normalize_url("http://portagein.gov/insecure.pdf",root,"portagein.gov"))
  self.assertIsNone(M.normalize_url("https://127.0.0.1/private.pdf",root,"portagein.gov"))
  self.assertIsNone(M.normalize_url("https://othercity.gov/contract.pdf",root,"portagein.gov"))
  self.assertEqual(M.normalize_url("/facts.pdf#section",root,"portagein.gov"),
    "https://portagein.gov/facts.pdf")
 def test_non_flock_government_page_held(self):
  with self.assertRaisesRegex(ValueError,"not an ALPR"):
   M.extract_links(b'<a href="/contract.pdf">A contract</a>',
     "https://portagein.gov/non-flock","Portage, IN")
 def test_original_source_errors_never_change_ownership_or_analytics(self):
  def source(url,limit):
   if url==M.SEEDS[0][0]:
    return b'<h1>Flock Safety ALPR</h1><a href="/a/Flock-contract.pdf">Signed Flock contract</a>','text/html'
   raise OSError("403 or unavailable")
  items,names,successful,errors=M.scan(source)
  self.assertEqual(successful,1)
  self.assertEqual(len(items),1)
  self.assertEqual(len(errors),len(M.SEEDS)-1)
  self.assertFalse(names)
  self.assertEqual(next(iter(items.values()))["review_status"],"requires_document_review")

if __name__=="__main__":unittest.main()
