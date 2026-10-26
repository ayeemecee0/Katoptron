import importlib.util
import sys
import unittest
from pathlib import Path

PATH=Path(__file__).with_name("mirror_licensed_agency_network.py")
sys.path.insert(0,str(PATH.parent))
spec=importlib.util.spec_from_file_location("mirror_network",PATH)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class SafeMirroredNetwork(unittest.TestCase):
 def test_minimum_network_and_no_fabricated_pins(self):
    meta={"generatedAt":"2026-10-19T12:22:41Z",
          "featureCount":5000,"portalCount":700,"directedEdges":112000}
    nodes={"type":"FeatureCollection","features":[]}
    edges={}
    for i in range(5000):
        nodes["features"].append({
          "type":"Feature","geometry":{"type":"Point","coordinates":[-90,40]},
          "properties":{
            "id":f"agency-{i+1:05d}","name":f"Test City {i} CA PD",
            "state":"CA","city":f"Test City {i}","type":"police",
            "isPortal":i<700,"portalSlug":str(i) if i<700 else None,
            "isJunk":False,"isInactive":False,"connectionCount":160,
            "aliases":[],"cameras":22
          }})
    for i in range(700):
        edges[f"agency-{i+1:05d}"]=[
          f"agency-{j+1:05d}" for j in range(5000) if i!=j][:160]
    result,links,proof=M.build(meta,nodes,edges)
    self.assertEqual(proof["featureCount"],5000)
    self.assertEqual(proof["directedEdges"],112000)
    self.assertEqual(len(result["features"]),5000)
    self.assertNotIn("geometry",result["features"][0])
    self.assertNotIn("coordinates",str(result["features"][0]))
    self.assertTrue(result["features"][0]["properties"]["isPortal"])
    self.assertEqual(links["agency-00001"][0],"agency-00002")
    self.assertIn("Coordinates omitted",proof["transformation"])
    self.assertIn("CC BY-SA 4.0",proof["license"])

if __name__=="__main__":unittest.main()
