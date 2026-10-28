#!/usr/bin/env python3
import importlib.util
import io
import json
import unittest
import zipfile
from pathlib import Path

P=Path(__file__).with_name("build_census_2026_jurisdiction_universe.py")
spec=importlib.util.spec_from_file_location("national_census_geographies",P)
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
def archive(rows,kind,sep="\t",filename="national.txt"):
 body=sep.join(["USPS","GEOID","NAME","LSAD","FUNCSTAT"])+"\n"
 for r in rows:body+=sep.join([r[0],r[1],r[2],"25","S"])+"\n"
 out=io.BytesIO()
 with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
  z.writestr(filename,body)
 return out.getvalue()
def rows(states=None):
 states=states or C.STATES
 return [(s,str(i+1).zfill(6),s+" Test jurisdiction") for i,s in enumerate(states)]
class TestOfficialCensusUniverse(unittest.TestCase):
 def test_all_51_states_and_distinct_geo_classes(self):
  s=rows()
  z={
    "county":archive(s,"county"),
    "place":archive(s,"place",sep="|"),
    "county_subdivision":archive(s,"county_subdivision")
  }
  data=C.build(fetcher=lambda kind:z[kind],strict_counts=False)
  self.assertEqual(data["states"],51)
  self.assertEqual(data["total_geographic_entities"],153)
  self.assertEqual(len(data["source_receipts"]),3)
  self.assertEqual(len(data["by_state"]),51)
  self.assertEqual(sum(i["counties"] for i in data["by_state"]),51)
  self.assertEqual(data["total_verified_flock_agencies"],0)
  self.assertEqual(data["total_verified_policy_adoptions"],0)
  self.assertIs(data["complete_municipal_agency_census"],False)
  self.assertTrue(all(x["known_law_enforcement_agency"] is False
   and x["flock_vendor_verified"] is False and x["alpr_policy_reviewed"] is False
   and x["camera_locations_inferred"]==0
    for x in data["geographic_research_queue"]))
 def test_no_puerto_rico_in_50_states_dc_ledger(self):
  parsed=C.parse_archive("county",archive(rows()+[("PR","72001","Test Puerto Rico county")],"county"))
  self.assertEqual(len(parsed),51)
  self.assertFalse(any(x["state"]=="PR" for x in parsed))
 def test_reject_malicious_zip_member_and_duplicate_geoid(self):
  data=archive(rows(),"place",filename="../source.txt")
  with self.assertRaisesRegex(ValueError,"layout"):
   C.parse_archive("place",data)
  dupe=archive([("WA","53001","A"),("WA","53001","B")],"county")
  with self.assertRaisesRegex(ValueError,"Duplicated"):
   C.parse_archive("county",dupe)
 def test_reject_untrusted_original_format(self):
  with self.assertRaises(ValueError):C.parse_archive("county",b"notzip"*50)
  with self.assertRaises(ValueError):C.parse_archive("county",b"x"*(C.ARCHIVE_LIMIT+1))
  with self.assertRaises(ValueError):C.url_for("unregistered_file")
 def test_completeness_guard_fail_closed(self):
  demo={
   "county":archive(rows(),"county"),
   "place":archive(rows(),"place"),
   "county_subdivision":archive(rows(),"county_subdivision")
  }
  with self.assertRaisesRegex(ValueError,"count"):
   C.build(fetcher=lambda kind:demo[kind],strict_counts=True)
  demo["county"]=archive(rows(["AL"]),"county")
  with self.assertRaisesRegex(ValueError,"state"):
   C.build(fetcher=lambda kind:demo[kind],strict_counts=False) if False else C.build(fetcher=lambda kind:demo[kind],strict_counts=True)
if __name__=="__main__":unittest.main()
