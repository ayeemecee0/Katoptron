"""Scope original-government Live Oak map camera verification to exact evidence."""
import unittest
from unittest.mock import patch
import auto_verify_camera_profiles as profiles
import verify_live_oak_direct_map as d

SOURCE=dict(
 source_key='live_oak_tx',source_status='verified',
 gis_layer_url=d.LAYER,government_evidence_url=d.CITY,
 jurisdiction_label='Live Oak, TX',expected_id_field='OBJECTID',
 bounds_south=29.3,bounds_west=-98.6,bounds_north=29.8,bounds_east=-98.1)
POLICY=dict(source_key='live_oak_tx',profile_status='verified',
 expected_layer_name='Cameras',identity_mode='municipal_public_flock_map',
 vendor_field='Device_Type',camera_id_field='OBJECTID',
 service_evidence_mode='city_police_direct_map')
PROOF={
 'government_page_sha256':'a'*64,'layer_url':d.LAYER,
 'source_count':2,'manufacturer_labeled_flock':0,
 'original_points':[{'id':3,'lat':29.56,'lon':-98.33},
                    {'id':9,'lat':29.57,'lon':-98.32}]
}
class GovernmentMapSourceTests(unittest.TestCase):
 def test_city_direct_map_authority_is_exact(self):
  self.assertTrue(d.authorize(SOURCE,POLICY))
  self.assertTrue(profiles.authorize(SOURCE,POLICY,None,None))
  for changed in (
      {**SOURCE,'gis_layer_url':d.LAYER.replace('LiveOakCameras','AnotherMap')},
      {**SOURCE,'government_evidence_url':'https://othercity.gov/flock'},
      {**SOURCE,'jurisdiction_label':'Another City'},
      {**SOURCE,'bounds_south':29.0}):
   with self.subTest(changed=changed):
    with self.assertRaises(ValueError):d.authorize(changed,POLICY)
  with self.assertRaises(ValueError):
   d.authorize(SOURCE,{**POLICY,'source_key':'arbitrary_esri'})
  with self.assertRaises(ValueError):
   d.authorize(SOURCE,{**POLICY,'camera_id_field':'Name'})
 def test_source_only_publication_records_not_automatically_active(self):
  rows,held,n=d.qualify(SOURCE,POLICY,lambda **kw:PROOF)
  self.assertEqual(n,2)
  self.assertEqual(len(rows),2)
  self.assertEqual(len(held),0)
  self.assertEqual(rows[0]['verification_method'],
                    'official_georeferenced_camera_record_v1')
  self.assertIn('NOT per-device manufacturer',rows[0]['evidence_summary'])
  self.assertEqual(rows[0]['source_url'],d.LAYER)
  self.assertEqual(rows[0]['jurisdiction_label'],'Live Oak, TX')
  self.assertEqual(len({r['record_key'] for r in rows}),2)
  self.assertEqual(d.qualify(SOURCE,POLICY,lambda **kw:PROOF)[0],rows)
 def test_geometry_or_original_receipt_drift_withheld(self):
  for proof in (
   {**PROOF,'source_count':3},
   {**PROOF,'original_points':PROOF['original_points'][:1]*2},
   {**PROOF,'layer_url':'https://services9.arcgis.com/wrong/FeatureServer/0'},
   {**PROOF,'government_page_sha256':'broken'},
   {**PROOF,'original_points':[{'id':1,'lat':40.0,'lon':-98.33}]}):
   with self.subTest(proof=proof):
    with self.assertRaises(ValueError):
     d.qualify(SOURCE,POLICY,lambda **kw:proof)
 def test_daily_verifier_accepts_only_same_exact_source(self):
  with patch.object(d,'audit',return_value=PROOF):
   rows,held,n=profiles.source_with_bounded_retries(SOURCE,POLICY)
  self.assertEqual(n,2)
  self.assertEqual(len(rows),2)
if __name__=='__main__':unittest.main()
