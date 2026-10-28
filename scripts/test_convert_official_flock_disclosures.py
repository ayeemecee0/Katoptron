import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).with_name("convert_official_flock_disclosures.py")
sp=importlib.util.spec_from_file_location("flock_original_html",P);M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
C=json.loads(M.CATALOG.read_text(encoding="utf8"))
class TestGovernmentEvidenceConversion(unittest.TestCase):
 def test_registry_11_distinct_new_state_government_agencies(self):
  rows=M.validate_catalog(C)
  self.assertEqual(len(rows),11)
  self.assertEqual(len({x["state"] for x in rows}),11)
  self.assertTrue(all(x["exact_camera_coordinates_added"]==0 for x in rows))
 def test_fake_source_does_not_persist_verified_facts(self):
  row=C["records"][0]
  fake=b"<html><body>The wrong police agency reports Flock cameras, no other details</body></html>"*4
  out=M.inspect(row,fetcher=lambda url:(fake,url))
  self.assertEqual(out["status"],"held_original_source_claim_drift")
  self.assertFalse(out["verified_original_html"])
  self.assertIsNone(out["original_html_sha256"])
  self.assertFalse(out["claim_specific_anchors_verified"])
  self.assertEqual(out["verified_camera_coordinates_added"],0)
 def test_known_publisher_with_explicit_anchors_is_only_attributed_statement(self):
  row=C["records"][0]
  source="<html><body><main><p>"+row["anchor"]+"</p><p>"+"</p><p>".join(row["additional_source_anchors"])+"</p></main></body></html>"
  got=M.inspect(row,fetcher=lambda url:(source.encode(),url))
  self.assertEqual(got["status"],"verified_agency_published_html_statements")
  self.assertTrue(got["claim_specific_anchors_verified"])
  self.assertEqual(got["corroborated_anchor_count"],3)
  self.assertFalse(got["legal_policy_adoption_verified"])
  self.assertFalse(got["current_equipment_or_technical_configuration_independently_verified"])
  self.assertEqual(got["device_count_individually_verified"],0)
 def test_script_injected_claim_does_not_qualify_source(self):
  row=C["records"][0]
  f="<html><body><script>"+row["anchor"]+" "+" ".join(row["additional_source_anchors"])+"</script></body></html>"
  got=M.inspect(row,fetcher=lambda url:(f.encode(),url))
  self.assertEqual(got["status"],"held_original_source_claim_drift")
 def test_untrusted_host_and_unscoped_urls_rejected(self):
  for url in ("https://evil.com/flock","https://city.gov.evil.com/path","http://city.gov/policy",
    "https://city.gov:8443/policy","https://city.gov/../admin","https://city.gov/raw-plate-reads",
    "https://city.gov/policy#page=3"):
   self.assertFalse(M.publisher_url(url),url)
 def test_per_source_outage_does_not_drop_states_or_promote_facts(self):
  result=M.run(C,fetcher=lambda url:(_ for _ in ()).throw(ValueError("Source unavailable")),workers=3)
  self.assertEqual(len(result["records"]),11)
  self.assertEqual(result["verified_agency_publisher_statements"],0)
  self.assertEqual(result["states_new_source_disclosures"],[])
  self.assertEqual(result["verified_exact_camera_points_added"],0)
 def test_authority_and_status_tampering_rejected(self):
  obj=json.loads(json.dumps(C));obj["records"][0]["source_url"]="https://attacker.com/policy"
  with self.assertRaisesRegex(ValueError,"Unapproved"):M.validate_catalog(obj)
  obj=json.loads(json.dumps(C));obj["records"][0]["policy_adoption_verified"]=True
  with self.assertRaisesRegex(ValueError,"Unapproved"):M.validate_catalog(obj)
  obj=json.loads(json.dumps(C));obj["records"][0]["state"]=obj["records"][1]["state"]
  with self.assertRaisesRegex(ValueError,"Unapproved"):M.validate_catalog(obj)
if __name__=="__main__":unittest.main()
