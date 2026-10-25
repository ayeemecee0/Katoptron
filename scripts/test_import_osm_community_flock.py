"""Regress exact-Osm-ID, ODbL classification and non-official point imports."""
import unittest
from unittest.mock import patch
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
 def test_unexpected_count_held(self):
  with self.assertRaisesRegex(ValueError,'outside bounds'):
   m.prepare_rows([f()],DAY)

if __name__=='__main__':unittest.main()
