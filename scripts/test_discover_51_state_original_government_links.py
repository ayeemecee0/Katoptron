#!/usr/bin/env python3
import importlib.util,json,unittest,xml.etree.ElementTree as ET
from pathlib import Path
P=Path(__file__).with_name("discover_51_state_original_government_links.py")
spec=importlib.util.spec_from_file_location("nationwide_state_source_discovery",P)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
R=json.loads(M.REGISTRY.read_text(encoding="utf8"))
def feed(items):
 root=ET.Element("rss",{"version":"2.0"})
 channel=ET.SubElement(root,"channel")
 for title,url in items:
  item=ET.SubElement(channel,"item")
  ET.SubElement(item,"title").text=title
  ET.SubElement(item,"link").text=url
  ET.SubElement(item,"description").text="Flock Safety ALPR government disclosure"
 return ET.tostring(root,encoding="utf-8",xml_declaration=True)
class AllStatesDiscovery(unittest.TestCase):
 def test_all_fifty_states_and_dc_scheduled(self):
  self.assertEqual(len(R["jurisdictions"]),51)
  self.assertIn("DC",{x["state"] for x in R["jurisdictions"]})
  result=M.scan(R,provider=lambda name:feed([("Flock ALPR government document","https://example.gov/police/alpr")]),workers=6)
  self.assertEqual(result["states_enrolled"],51)
  self.assertEqual(result["states_checked"],51)
  self.assertEqual(result["states_provider_unavailable"],0)
  self.assertEqual(result["unreviewed_government_link_leads"],51)
  self.assertTrue(all(not s["search_leads"][0]["flock_equipment_confirmed"] for s in result["states"]))
 def test_untrusted_external_source_excluded(self):
  items=[
   ("Flock Safety ALPR","https://example.gov/police/flock"),
   ("Flock Safety ALPR","https://example.gov/police/flock"),
   ("Flock safety","https://gov.example.evil/steal"),
   ("Flock safety","http://other.gov/path"),
   ("Flock safety","https://other.gov/../secrets"),
   ("Flock safety","https://other.gov/plate-search-logs"),
   ("Flock safety","https://other.gov/policy")]
  result=M.parse_rss("Alaska",feed(items))
  self.assertEqual(len(result),2)
  self.assertTrue(all(not x["state_relevance_confirmed"] and not x["original_document_content_reviewed"] for x in result))
 def test_unavailable_search_provider_never_means_no_flock(self):
  result=M.scan(R,provider=lambda name:(_ for _ in ()).throw(ValueError("blocked")),workers=4)
  self.assertEqual(result["states_checked"],0)
  self.assertEqual(result["states_provider_unavailable"],51)
  self.assertTrue(all(x["discovery_status"]=="search_provider_unavailable_retry_needed" for x in result["states"]))
 def test_reject_non_rss_or_incomplete_queue(self):
  with self.assertRaisesRegex(ValueError,"RSS"):M.parse_rss("Alabama",b"<html>blocked</html>")
  obj=json.loads(json.dumps(R));obj["jurisdictions"].pop()
  with self.assertRaisesRegex(ValueError,"not complete"):M.scan(obj,provider=lambda _:feed([]))
if __name__=="__main__":unittest.main()
