#!/usr/bin/env python3
import csv,importlib.util,io,json,unittest
from pathlib import Path
P=Path(__file__).with_name("build_fbi_derived_agency_roster.py")
sp=importlib.util.spec_from_file_location("ori_import",P)
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
def data(records,header=None):
 io_=io.StringIO();columns=header or ["ori","state_abbr","agency_name","agency_type","county","latitude","longitude"]
 w=csv.DictWriter(io_,fieldnames=columns);w.writeheader()
 for r in records:w.writerow(r)
 return io_.getvalue().encode()
def one(ori="CA1234500",state="CA",name="Fictional test Police Department"):
 return {"ori":ori,"state_abbr":state,"agency_name":name,"agency_type":"City",
 "county":"Test County","latitude":"-34","longitude":"51"}
class TestORI(unittest.TestCase):
 def test_stable_ori_secondary_source_not_program_evidence(self):
  raw=data([one(),one("NY6789100","NY","Another Fictional Police Department")])
  o=M.parse(raw,require_count=False)
  self.assertEqual(len(o),2)
  self.assertEqual(o[0]["ori"],"CA1234500")
  self.assertEqual(o[0]["state"],"CA")
  self.assertIs(o[0]["original_federal_directory_directly_fetched"],False)
  self.assertFalse(o[0]["flock_vendor_verified"])
  self.assertFalse(o[0]["alpr_program_verified"])
  self.assertFalse(o[0]["policy_adoption_verified"])
  self.assertEqual(o[0]["camera_coordinates_added"],0)
  self.assertNotIn("latitude",o[0])
  self.assertNotIn("longitude",o[0])
 def test_never_import_bad_identity_and_no_automatic_matching(self):
  with self.assertRaisesRegex(ValueError,"Duplicate ORI"):
   M.parse(data([one(),one(name="Duplicate Police Name")]),require_count=False)
  with self.assertRaisesRegex(ValueError,"Unusable"):
   M.parse(data([one(ori="X")]),require_count=False)
  with self.assertRaisesRegex(ValueError,"schema"):
   M.parse(data([{"unknown":"none"}],["unknown"]),require_count=False)
 def test_row_count_and_state_completion_gate(self):
  with self.assertRaisesRegex(ValueError,"population"):
   M.parse(data([one()]),require_count=True)
  with self.assertRaisesRegex(ValueError,"byte limit"):
   M.parse(b"x"*(M.MAX_BYTES+1),require_count=False)
 def test_source_and_directory_distinct(self):
  sample=data([one(),one("DC0010000","DC","District Test Police Department")])
  x=M.build(fetcher=lambda:sample,strict=False)
  self.assertEqual(x["states_count"],51)
  self.assertEqual(x["research_agency_count"],2)
  self.assertEqual(x["state_counts"]["CA"],1)
  self.assertEqual(x["state_counts"]["DC"],1)
  self.assertEqual(x["flock_deployments_verified"],0)
  self.assertEqual(x["fbi_agency_currently_operating_verified"],0)
  self.assertEqual(x["individual_camera_coordinates_published"],0)
if __name__=="__main__":unittest.main()
