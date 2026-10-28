import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("monitor_policy",
 ROOT/"scripts"/"monitor_policy_adoption_originals.py")
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
ledger=json.loads((ROOT/"data"/"verified-policy-adoption-status-2026-10-27.json").read_text())

GREEN='''<html><body>
<h1>Green Bay Police Department - Policy Manual</h1>
<a href="/DocumentCenter/View/18791/Policy-424-Automated-License-Plate-Readers-ALPR-May-2026">Policy 424 Automated License Plate Readers (ALPR) May 2026</a>
<a href="/DocumentCenter/View/19136/DRAFTED-REVISION---Policy-424-Automated-License-Plate-Readers-ALPR-September-2026">DRAFTED REVISION - Policy 424 Automated License Plate Readers (ALPR) September 2026</a>
</body></html>'''
APACHE='''<html><body>
<p>The following Ordinances and Resolutions have been adopted but have not been incorporated in the City Code yet:</p>
<table><tr><th>Document Number:</th><th>Related To:</th><th>Adopted by Council:</th><th>Becomes Effective on:</th></tr>
<tr><td><a>Ordinance No. 1579</a></td><td>Automated License Plate Readers ordinance, including enforcement and penalties</td><td>10/06/2026</td><td></td></tr>
<tr><td>Ordinance No. 1577</td><td>Parks</td><td>10/06/2026</td><td></td></tr>
</table></body></html>'''
class MonitorOriginalStatus(unittest.TestCase):
 def test_exact_original_publication_baseline(self):
  urls={ledger["records"][0]["source_url"]:APACHE,
        ledger["records"][1]["source_url"]:GREEN}
  out=M.run(ledger,fetch=lambda url:urls[url])
  self.assertEqual(out["needs_review"],0)
  self.assertEqual(out["new_enacted_policy_records_auto_published"],0)
  rows={x["id"]:x for x in out["sources"]}
  green=rows["green-bay-wi-policy-424-draft-still-listed-2026-10-27"]
  self.assertEqual(green["source_status"],"confirmed_original_index_still_marks_draft")
  self.assertIs(green["adoption_verified"],False)
  self.assertFalse(green["new_original_policy_candidates_needing_review"])
  apache=rows["apache-junction-az-ordinance-1579-adopted-2026-10-06"]
  self.assertEqual(apache["source_status"],"confirmed_city_clerk_adoption_register_entry_present")
  self.assertIs(apache["adoption_verified_from_registered_source"],True)
  self.assertIs(apache["effective_date_verified"],False)
 def test_new_published_policy_link_requires_review_not_automatic_adoption(self):
  candidate='''<a href="/DocumentCenter/View/23456/Policy-424-October-2026">Policy 424 Automated License Plate Readers (ALPR) October 2026</a>'''
  out=M.review_green_bay(GREEN.replace("</body>",candidate+"</body>"))
  self.assertEqual(out["source_status"],"needs_review_index_changed_or_new_policy_link")
  self.assertEqual(out["new_original_policy_candidates_needing_review"],[
   "/DocumentCenter/View/23456/Policy-424-October-2026"])
  self.assertFalse(out["adoption_verified"])
 def test_if_draft_label_disappears_hold_and_do_not_auto_adopt(self):
  out=M.review_green_bay(GREEN.replace("DRAFTED REVISION - ","ADOPTED - "))
  self.assertEqual(out["source_status"],"needs_review_index_changed_or_new_policy_link")
  self.assertFalse(out["adoption_verified"])
 def test_clerk_notice_missing_or_archived_not_auto_repeal(self):
  x=M.review_apache_junction(APACHE.replace("10/06/2026</td><td></td>","??</td><td></td>",1))
  self.assertEqual(x["source_status"],"needs_review_city_clerk_entry_changed_or_archived")
  self.assertFalse(x["adoption_verified_from_registered_source"])
 def test_server_error_wont_generate_false_status(self):
  def unavailable(url):raise TimeoutError("no source")
  out=M.run(ledger,fetch=unavailable)
  self.assertEqual(out["needs_review"],2)
  self.assertTrue(all(x["source_status"]=="needs_review_source_unreachable" for x in out["sources"]))
  self.assertEqual(out["new_enacted_policy_records_auto_published"],0)
 def test_identifiers_must_be_exact(self):
  fake=json.loads(json.dumps(ledger))
  fake["records"][0]["id"]="other-city"
  with self.assertRaises(ValueError):M.run(fake,fetch=lambda url:"ok")
if __name__=="__main__":unittest.main()
