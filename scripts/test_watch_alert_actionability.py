import unittest
from watch_alert_actionability import insights,source_https
class WatchInsightTests(unittest.TestCase):
 def test_every_eligible_source_category_has_proportionate_action(self):
  for kind in ("government_decision","contract_document","contract_renewal","vendor_portal_snapshot",
    "vendor_count_changed","retention_changed","sharing_list_changed",
    "policy_original_reviewed","policy_draft_reviewed"):
   x=insights({"kind":kind,"source_url":"https://city.example.gov/records/2026"},"sacramento county|CA")
   self.assertTrue(x["why"] and x["next"])
   self.assertIn("research-workspace.html?agency=sacramento%20county%7CCA",x["case_url"])
 def test_no_unqualified_url_or_category(self):
  for url in ("http://example.gov","https://evil.gov@localhost/file","https://example.gov/a#frag","file:///etc/passwd"):
   with self.assertRaises(ValueError):insights({"kind":"government_decision","source_url":url},"foo|CA")
  with self.assertRaises(ValueError):insights({"kind":"unknown","source_url":"https://gov.example.gov/a"},"foo|CA")
 def test_draft_never_claims_adoption(self):
  d=insights({"kind":"policy_draft_reviewed","source_url":"https://gov.example.gov/a"},"test|CA")
  self.assertIn("not an effective policy",d["why"])
if __name__=="__main__":unittest.main()
