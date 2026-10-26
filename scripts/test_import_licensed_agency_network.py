import importlib.util
import unittest
from pathlib import Path

P=Path(__file__).with_name("import_licensed_agency_network.py")
spec=importlib.util.spec_from_file_location("agency_source_sync",P)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

class LicensedAgencyImport(unittest.TestCase):
    def setUp(self):
        self.nodes={"type":"FeatureCollection","features":[]}
        self.links={"agency-00001":["agency-00002"]}
        for i in range(5000):
            name=f"Test Agency {i} CA PD"
            self.nodes["features"].append({"properties":{
                "id":f"agency-{i+1:05d}","name":name,
                "isPortal":i<700,"portalSlug":f"agency-{i:05d}" if i<700 else None,
                "state":"CA","type":"police","cameras":0,
                "connectionCount":0}})
        self.links={f"agency-{i+1:05d}":[f"agency-{j+1:05d}"
          for j in range(5000) if j!=i][:160] for i in range(700)}
        self.meta={"featureCount":5000,"portalCount":700,
          "generatedAt":"2026-10-25T17:00:00Z",
          "directedEdges":sum(len(v) for v in self.links.values())}
    def test_source_validator_and_safe_rows(self):
        a=M.validate(self.meta,self.nodes,self.links)
        out=list(M.rows(a,self.meta))
        self.assertEqual(len(out),5000)
        self.assertTrue(out[0]["is_reporting_portal"])
        self.assertIsNone(out[0]["source_reported_mixed_cameras"],
                          "zero source camera counters cannot silently imply a measured zero")
        self.assertFalse(out[-1]["is_reporting_portal"])
        self.assertNotIn("latitude",out[0])
        self.assertNotIn("longitude",out[0])
        self.assertEqual(out[0]["source_tier"],"secondary_aggregated_portal_snapshot")
    def test_reject_unknown_target(self):
        self.links["agency-00001"][0]="phantom"
        with self.assertRaisesRegex(ValueError,"Invalid, duplicate"):
            M.validate(self.meta,self.nodes,self.links)
    def test_reject_fake_extra_cameras(self):
        self.nodes["features"][0]["properties"]["cameras"]=-1
        out=list(M.rows(M.validate(self.meta,self.nodes,self.links),self.meta))
        self.assertIsNone(out[0]["source_reported_mixed_cameras"])
    def test_reject_truncated(self):
        self.meta["directedEdges"]-=1
        with self.assertRaisesRegex(ValueError,"truncated"):
            M.validate(self.meta,self.nodes,self.links)

if __name__=="__main__":unittest.main()
