import importlib.util
import unittest
from pathlib import Path
p=Path(__file__).with_name("watch_original_government_versions.py")
spec=importlib.util.spec_from_file_location("watch_original_government_versions",p)
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)

class OriginalVersionSafety(unittest.TestCase):
 def setUp(self):
  self.row={"id":"frankfort-ky-flock-nonrenewal-commission-vote-2026",
   "source_url":"https://www.frankfort.ky.gov/m/NewsFlash/Home/Detail/274",
   "source_date":"2026-10-13","locality_key":"frankfort|KY",
   "watch_category":"historical_research_only"}
  self.anchor=V.ANCHORS[self.row["id"]]
  self.receipts=[];self.reviews=[]
 def api(self,path,method="GET",body=None):
  if method=="GET":
   existing=[r for r in self.receipts if r["source_id"]==self.row["id"]]
   return [dict(text_sha256=x["text_sha256"],anchor_context_sha256=x["anchor_context_sha256"]) for x in existing[-1:]]
  if "flock_original_page_versions" in path:
   if not any(x["text_sha256"]==body[0]["text_sha256"] for x in self.receipts):
    self.receipts.append(body[0])
  elif "flock_original_page_review_queue" in path:
   if not any(x["current_sha256"]==body[0]["current_sha256"] for x in self.reviews):
    self.reviews.append(body[0])
  else:raise AssertionError("Unexpected review API")
 def original(self,suffix=""):
  return ("<html><main><p>The commission "+self.anchor+
          ". Final status remains a city-published statement.</p><p>"+suffix+
          "</p></main></html>").encode()
 def test_baseline_not_an_alert_or_claimed_verified_update(self):
  first=V.scan([self.row],lambda _:self.original(),self.api)
  self.assertEqual(first[self.row["id"]],"baselined_unreviewed_not_an_event")
  self.assertEqual(len(self.reviews),0)
  second=V.scan([self.row],lambda _:self.original(),self.api)
  self.assertEqual(second[self.row["id"]],"unchanged")
  self.assertEqual(len(self.receipts),1)
 def test_new_publisher_text_requires_manual_review_never_email(self):
  V.scan([self.row],lambda _:self.original(),self.api)
  result=V.scan([self.row],lambda _:self.original("Additional revised city context."),self.api)
  self.assertIn("requires_original_editorial_review",result[self.row["id"]])
  self.assertEqual(len(self.reviews),1)
  self.assertEqual(self.reviews[0]["status"] if "status" in self.reviews[0] else "needs_original_editorial_review","needs_original_editorial_review")
  V.scan([self.row],lambda _:self.original("Additional revised city context."),self.api)
  self.assertEqual(len(self.reviews),1)
 def test_disappeared_anchor_or_wrong_publisher_is_held(self):
  self.assertEqual(V.scan([self.row],lambda _:b"<html>No city decision</html>",self.api)[self.row["id"]],"held_ValueError")
  self.assertEqual(len(self.receipts),0)
  bad=dict(self.row,source_url="https://frankfort.ky.gov.evil.invalid/injected")
  self.assertEqual(V.scan([bad],lambda _:self.original(),self.api)[self.row["id"]],"held_ValueError")
 def test_external_unauthorized_source_or_duplicate_rejected(self):
  with self.assertRaisesRegex(ValueError,"Duplicate"):
   V.scan([self.row,self.row],lambda _:self.original(),self.api)
  bad=dict(self.row,watch_category="new_public_event")
  self.assertEqual(V.scan([bad],lambda _:self.original(),self.api)[self.row["id"]],"held_ValueError")
if __name__=="__main__":unittest.main()
