import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("recheck_three_held_government_originals.py")
sp=importlib.util.spec_from_file_location("recheck_original_holds",P)
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
R=json.loads(M.REGISTRY.read_text(encoding="utf8"))
P0=json.loads(M.ORIGINALS.read_text(encoding="utf8"))
N=json.loads(M.NEWER.read_text(encoding="utf8"))
def supplied(url):
 row=next(x for x in M.CHECKED.values() if x["url"]==url)
 html="<html><body><main>"+" ".join(row["anchors"])+"</main></body></html>"
 return html.encode(),url
class SourceRepairTests(unittest.TestCase):
 def test_all_three_explicit_statuses(self):
  x=M.inspect(R,P0,N,fetcher=supplied)
  self.assertEqual(x["base_source_holds"],12)
  self.assertEqual(x["resolved_original_source_items"],3)
  self.assertEqual(x["remaining_original_source_holds"],9)
  self.assertEqual([r["state"] for r in x["results"]],["FL","NC","CO"])
  self.assertEqual(x["actual_flock_camera_locations_added"],0)
  self.assertFalse(x["current_operating_status_independently_verified"])
  self.assertEqual(x["results"][2]["disposition"],"superseded_original_government_source_lead")
  self.assertFalse(x["results"][2]["old_url_independently_retrieved"])
 def test_page_claim_drift_and_outage_never_publish(self):
  a=M.inspect(R,P0,N,fetcher=lambda url:(b"<html><body>wrong unrelated website</body></html>",url))
  self.assertEqual(a["resolved_original_source_items"],1)
  self.assertEqual(a["remaining_original_source_holds"],11)
  self.assertTrue(all(x["disposition"].startswith("held_") for x in a["results"][:2]))
  x=M.inspect(R,P0,N,fetcher=lambda url:(_ for _ in ()).throw(ValueError("blocked")))
  self.assertEqual(x["resolved_original_source_items"],1)
  self.assertEqual(x["remaining_original_source_holds"],11)
 def test_original_source_urls_and_prior_status_are_bound(self):
  j=json.loads(json.dumps(R))
  j["official_seed_sources"]= [dict(x) for x in j["official_seed_sources"]]
  next(x for x in j["official_seed_sources"] if x["id"]=="fl-police-operational-status-statement")["source_url"]="https://evil.example/alpr"
  with self.assertRaisesRegex(ValueError,"history"):M.inspect(j,P0,N,fetcher=supplied)
  n=json.loads(json.dumps(N))
  next(x for x in n["source_disclosures"] if x["id"]=="lafayette-co")["publisher_statement_category"]="agency_reports_flock_use"
  with self.assertRaisesRegex(ValueError,"supersession"):M.inspect(R,P0,n,fetcher=supplied)
if __name__=="__main__":unittest.main()
