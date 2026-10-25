import unittest
from unittest.mock import patch
import publish_live_oak_direct_map as p
import verify_live_oak_direct_map as d

SOURCE=dict(
 source_key=d.KEY,source_status='verified',gis_layer_url=d.LAYER,
 government_evidence_url=d.CITY,jurisdiction_label='Live Oak, TX',
 expected_id_field='OBJECTID',bounds_south=29.3,bounds_west=-98.6,
 bounds_north=29.8,bounds_east=-98.1)
POLICY=dict(
 source_key=d.KEY,profile_status='verified',
 identity_mode='municipal_public_flock_map',
 service_evidence_mode='city_police_direct_map',expected_layer_name='Cameras',
 camera_id_field='OBJECTID',vendor_field='Device_Type')
ROW={'record_key':'gis-live_oak_tx-3-abc123', 'latitude':29.55,
     'longitude':-98.33,'source_url':d.LAYER}

class CitySourcePublication(unittest.TestCase):
 def test_reject_nonapproved_source(self):
  def bad(path,*a,**k):
   return [{**SOURCE,'gis_layer_url':d.LAYER.replace('LiveOakCameras','Falsified')}]
  with self.assertRaises(ValueError):p.reviewed_authority(bad)
 def test_readonly_no_write_and_separate_other_sources(self):
  requests=[]
  def api(path,*a,**k):
   requests.append(path)
   if path.startswith('trusted_flock_gis_sources?'):return [SOURCE]
   if path.startswith('gis_verification_profiles?'):return [POLICY]
   raise AssertionError('Read-only dry-run attempted new query')
  with patch.object(p,'fetch_all',return_value=[
      {'record_key':str(i),'latitude':38.5,'longitude':-121.5,
       'source_url':'https://gov.example/MapServer/0'}
        for i in range(293)]):
   self.assertEqual(p.reconcile(False,api,
      lambda s,t:([ROW],{},1)),1)
  self.assertEqual(len(requests),2)
 def test_missing_or_duplicated_gis_source_held(self):
  def api(path,*a,**k):
   return [SOURCE] if path.startswith('trusted_flock_gis_sources?') else [POLICY]
  with patch.object(p,'fetch_all',return_value=[
      {'record_key':str(i),'latitude':29.55,'longitude':-98.33,
       'source_url':'another.gov'}
       for i in range(293)]):
   with self.assertRaisesRegex(ValueError,'within 100m'):
    p.reconcile(False,api,lambda s,t:([ROW],{},1))
 def test_incomplete_source_cannot_publish(self):
  def api(path,*a,**k):
   return [SOURCE] if path.startswith('trusted_flock_gis_sources?') else [POLICY]
  with self.assertRaisesRegex(ValueError,'not entirely verified'):
   p.reconcile(True,api,lambda s,t:([ROW],{},2))

if __name__=='__main__':unittest.main()
