"""Regress exact-Osm-ID, ODbL classification and non-official point imports."""
import unittest
from unittest.mock import patch,MagicMock
import import_osm_community_flock as m

DAY='2026-10-24'
def f(brand='Flock Safety',osm_id=123,lat=38.5,lon=-121.5,kind='node'):
 return {'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},
         'properties':{'brand':brand,'osmType':kind,'osmId':osm_id,
                       'osmTimestamp':'2026-10-23T19:10:12Z'}}

class ImportTests(unittest.TestCase):
 def test_only_explicit_osm_flock_and_valid_us_geometry(self):
  self.assertEqual(m.normalize(f(),DAY)['osm_key'],'node/123')
  self.assertEqual(m.normalize(f(),DAY)['latitude'],38.5)
  self.assertIsNone(m.normalize(f(brand='Rekor'),DAY))
  self.assertIsNone(m.normalize(f(brand=None),DAY))
  self.assertIsNone(m.normalize(f(lat=0),DAY))
  self.assertIsNone(m.normalize(f(osm_id=0),DAY))
  self.assertIsNone(m.normalize(f(kind='relation'),DAY))
 def test_complete_and_dedup(self):
  with patch.object(m,'MIN_FLOCK',2):
   rows=m.prepare_rows([f(),f(),f(osm_id=124),f(brand='Motorola',osm_id=222)],DAY)
  self.assertEqual(len(rows),2)
 def test_changed_same_osm_id_is_held(self):
  with patch.object(m,'MIN_FLOCK',2):
   with self.assertRaisesRegex(ValueError,'Conflicting duplicate'):
    m.prepare_rows([f(),f(lat=38.6)],DAY)
 def test_not_publish_government(self):
  with patch.object(m,'MIN_FLOCK',2):
   rows=m.prepare_rows([f(),f(osm_id=124)],DAY)
  calls=[]
  self.assertEqual(m.import_rows(rows,2,api=lambda batch:calls.append(batch)),2)
  self.assertEqual(len(calls),1)
  self.assertTrue(all('verification_status' not in p for p in calls[0]))
  self.assertTrue(all('latitude' in p and 'source_snapshot_date' in p for p in calls[0]))
 def test_reconcile_does_not_delete_on_partial_source(self):
  with patch.object(m,'read_count') as count:
   with patch.object(m.urllib.request,'urlopen') as net:
    with self.assertRaisesRegex(ValueError,'shrink'):
     m.reconcile(116160,100000,'2026-10-25T03:00:00+00:00')
   count.assert_not_called()
   net.assert_not_called()
 def test_reconcile_does_not_delete_after_incomplete_upload(self):
  with patch.object(m,'read_count',return_value=116000):
   with patch.object(m.urllib.request,'urlopen') as net:
    with self.assertRaisesRegex(ValueError,'count mismatch'):
     m.reconcile(116160,116120,'2026-10-25T03:00:00+00:00')
   net.assert_not_called()
 def test_successful_full_reconciliation_checks_both_sides(self):
  response=MagicMock()
  response.__enter__.return_value.status=204
  response.__enter__.return_value.read.return_value=b''
  with patch.object(m,'read_count',side_effect=[116120,40,116120]) as counts:
   with patch.object(m.urllib.request,'urlopen',return_value=response) as net:
    with patch.dict(m.os.environ,{
     'SUPABASE_URL':'https://bpvkapswslmgfazbzpsv.supabase.co',
     'SUPABASE_SERVICE_ROLE_KEY':'only-a-test-secret'
    }):
     m.reconcile(116160,116120,'2026-10-25T03:00:00+00:00')
    self.assertEqual(net.call_args.args[0].get_method(),'DELETE')
    self.assertIn('last_seen_sync_at=neq.',net.call_args.args[0].full_url)
    self.assertEqual(counts.call_count,3)
 def test_many_renamed_source_ids_does_not_remove_existing_evidence(self):
  with patch.object(m,'read_count',side_effect=[116000,8200]) as counts:
   with patch.object(m.urllib.request,'urlopen') as net:
    with self.assertRaisesRegex(ValueError,'identity churn'):
     m.reconcile(116160,116000,'2026-10-25T03:00:00+00:00')
   net.assert_not_called()
   self.assertEqual(counts.call_count,2)
 def test_upsert_batch_includes_marker_and_preserves_existing_ids(self):
  collected=[]
  row=m.normalize(f(),DAY)
  m.import_rows([row],1,api=lambda batch:collected.extend(batch),
   run_stamp='2026-10-25T03:00:00+00:00')
  self.assertEqual(collected[0]['last_seen_sync_at'],'2026-10-25T03:00:00+00:00')
  self.assertEqual(collected[0]['osm_key'],'node/123')
  self.assertNotIn('evidence_tier',collected[0])
 def test_quality_snapshot_tracks_exact_colocations_and_edited_age(self):
  stamp='2026-10-25T05:00:00+00:00'
  with patch.object(m,'MIN_FLOCK',2):
   a=m.normalize(f(osm_id=101), '2026-10-25')
   b=m.normalize(f(osm_id=102), '2026-10-25')
   c=m.normalize(f(osm_id=103), '2026-10-25')
   a['source_timestamp']='2025-01-01T00:00:00Z'
   b['source_timestamp']='2026-10-24T03:00:00Z'
   c['source_timestamp']=None
   c['latitude']=a['latitude'];c['longitude']=a['longitude']
   snap=m.build_quality_snapshot([a,b,c],stamp,'2026-10-25')
  self.assertEqual(snap['osm_observations'],3)
  self.assertEqual(snap['distinct_coordinates'],1)
  self.assertEqual(snap['colocated_extra_observations'],2)
  self.assertEqual(snap['colocated_coordinate_groups'],1)
  self.assertEqual(snap['osm_edits_older_365d'],1)
  self.assertEqual(snap['osm_edit_timestamp_missing'],1)
  self.assertEqual(len(snap['measurement_receipt_sha256']),64)
 def test_snapshot_rejects_partial_and_future_source(self):
  with patch.object(m,'MIN_FLOCK',2):
   with self.assertRaisesRegex(ValueError,'Incomplete'):
    m.build_quality_snapshot([m.normalize(f(),DAY)],
      '2026-10-25T05:00:00+00:00','2026-10-25')
   a=m.normalize(f(osm_id=100),DAY);b=m.normalize(f(osm_id=101),DAY)
   a['source_timestamp']='2030-01-01T00:00:00Z'
   with self.assertRaisesRegex(ValueError,'Future OSM'):
    m.build_quality_snapshot([a,b],'2026-10-25T05:00:00+00:00','2026-10-25')
 def test_quality_snapshot_append_is_private_only(self):
  r=MagicMock()
  r.__enter__.return_value.status=204
  r.__enter__.return_value.read.return_value=b''
  item={'sync_at':'2026-10-25T05:00:00+00:00',
        'osm_observations':3,'distinct_coordinates':2,
        'colocated_extra_observations':1,'osm_edits_older_365d':0}
  with patch.dict(m.os.environ,{
   'SUPABASE_URL':'https://bpvkapswslmgfazbzpsv.supabase.co',
   'SUPABASE_SERVICE_ROLE_KEY':'only-a-test-secret'
  }):
   with patch.object(m.urllib.request,'urlopen',return_value=r) as request:
    m.publish_quality_snapshot(item)
    self.assertEqual(request.call_args.args[0].get_method(),'POST')
    self.assertIn('flock_osm_quality_snapshots',request.call_args.args[0].full_url)
 def test_unexpected_count_held(self):
  with self.assertRaisesRegex(ValueError,'outside bounds'):
   m.prepare_rows([f()],DAY)

if __name__=='__main__':unittest.main()
