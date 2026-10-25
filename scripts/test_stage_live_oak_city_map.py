import unittest
from unittest.mock import patch
import stage_live_oak_city_map as s

PROOF={'layer_url':'https://services3.arcgis.com/Org1/arcgis/rest/services/Cameras/FeatureServer/0',
 'government_page_sha256':'c'*64,'source_count':2,
 'original_points':[{'id':1,'lat':29.56,'lon':-98.33},
                    {'id':2,'lat':29.57,'lon':-98.34}],
 'manufacturer_labeled_flock':0}

class LiveOakPrivateResearch(unittest.TestCase):
 def test_unreviewed_no_verified_status(self):
  cases,evidence=s.make_receipts(PROOF)
  self.assertEqual(len(cases),2)
  self.assertEqual(len(evidence),2)
  self.assertEqual(evidence[0]['source_kind'],'third_party_gis')
  self.assertTrue(all('verification_status' not in x and 'classification' not in x for x in cases))
  self.assertTrue(all('reviewed_at' not in x for x in evidence))
  with self.assertRaisesRegex(ValueError,'duplicated'):
   s.make_receipts({**PROOF,'original_points':[PROOF['original_points'][0]]*2})
 def test_dry_run_writes_nothing(self):
  with patch.object(s,'fetch_all',return_value=[
    {'latitude':38.5,'longitude':-121.5} for _ in range(293)]):
   self.assertEqual(s.stage(False,api=lambda *a,**k:(_ for _ in ()).throw(
    AssertionError('Dry-run attempted database write')),audited=lambda **k:PROOF),2)
 def test_staging_only_writes_private_tables(self):
  paths=[]
  def api(path,method=None,payload=None,prefer=None):
   if method=='POST':paths.append(path);return None
   return []
  with (patch.object(s,'fetch_all',return_value=[
      {'latitude':38.5,'longitude':-121.5} for _ in range(293)]),
      patch.object(s,'hold_conflicting_staged_evidence')):
   self.assertEqual(s.stage(True,api=api,audited=lambda **k:PROOF),2)
  self.assertEqual([x.split('?')[0] for x in paths],
   ['flock_point_evidence_cases','flock_point_evidence_attestations'])

if __name__=='__main__':unittest.main()
