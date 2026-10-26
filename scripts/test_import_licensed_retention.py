import importlib.util
import sys
import unittest
from pathlib import Path

D=Path(__file__).parent
sys.path.insert(0,str(D))
spec=importlib.util.spec_from_file_location("import_licensed_retention",D/"import_licensed_retention.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

class SecondaryRetentionSafety(unittest.TestCase):
 def test_snapshot_recognizes_missing_as_unknown(self):
    self.assertEqual(M.retention_days(30),30)
    self.assertEqual(M.retention_days("30 days"),30)
    self.assertEqual(M.retention_days(None),None)
    self.assertEqual(M.retention_days("not published"),None)
    self.assertEqual(M.retention_days(-1),None)
 def test_bounded_source_and_identity(self):
    data={"portals":[
     {"slug":f"test-city-{i}-ca-pd","state":"CA","type":"PD",
      "data_retention":30,"organizations_shared_with":[]}
     for i in range(750)],"summary":{}}
    reg={p["slug"]:f"test-agency-{i}" for i,p in enumerate(data["portals"])}
    rows=M.normalize(data,reg,"2026-10-25")
    self.assertEqual(len(rows),750)
    self.assertNotIn("latitude",rows[0])
    self.assertEqual(rows[0]["retention_days"],30)
    previous=[{"source_agency_id":"test-agency-0",
       "retention_days":7,"observed_on":"2026-10-01"}]
    new=M.history_events(rows,previous,{"test-agency-0":"Folsom CA PD"})
    self.assertEqual(len(new),1)
    self.assertEqual(new[0]["kind"],"retention_changed")
    self.assertEqual(new[0]["locality_key"],"folsom|CA")
    self.assertIn("secondary",new[0]["evidence_tier"])
 def test_truncation_is_held(self):
    with self.assertRaisesRegex(ValueError,"truncated"):
        M.normalize({"portals":[{"slug":"a"}],"summary":{}},{},
          "2026-10-25")

if __name__=="__main__":unittest.main()
