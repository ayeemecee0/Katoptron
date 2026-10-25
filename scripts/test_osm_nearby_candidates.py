import unittest
from osm_nearby_candidates import candidates,summarize,meters

def row(k,lat,lon):return {'osm_key':'node/'+str(k),'latitude':lat,'longitude':lon}

class NearbyAuditTests(unittest.TestCase):
 def test_nearby_nonidentical_flock_observations_are_candidates(self):
  pts=[row(1,38.50000,-121.50000),
       row(2,38.50006,-121.50000),
       row(3,38.50000,-121.50000),
       row(4,38.504,-121.50000)]
  p=candidates(pts)
  self.assertEqual(len(p),2)
  self.assertEqual({tuple(x[:2]) for x in p},{('node/1','node/2'),('node/2','node/3')})
  self.assertTrue(6<p[0][2]<7)
  self.assertEqual(summarize(p)['source_records_in_nearby_pairs'],3)
 def test_boundary_between_adjacent_grid_cells_is_not_missed(self):
  pts=[row(1,38.500499,-121.5001),row(2,38.500501,-121.5001)]
  self.assertEqual(len(candidates(pts)),1)
 def test_high_latitude_longitudinal_neighbours(self):
  pts=[row(1,71.0000,-150.0000),row(2,71.0000,-149.9997)]
  self.assertEqual(len(candidates(pts)),1)
 def test_far_and_exact_same_coordinates_excluded(self):
  self.assertEqual(candidates([row(1,38.5,-121.5),row(2,38.5,-121.5)]),[])
  self.assertEqual(candidates([row(1,38.5,-121.5),row(2,38.5003,-121.5)]),[])
 def test_duplicate_source_id_held(self):
  with self.assertRaisesRegex(ValueError,'Duplicate OSM'):
   candidates([row(1,38.5,-121.5),row(1,38.5001,-121.5)])
 def test_nearby_not_merged_and_input_untouched(self):
  pts=[row(1,38.5,-121.5),row(2,38.50004,-121.5)]
  source=[r.copy() for r in pts]
  pairs=candidates(pts)
  self.assertEqual(pts,source)
  self.assertEqual(len(pairs),1)
  self.assertEqual(pairs[0][2],round(meters((38.5,-121.5),(38.50004,-121.5)),2))

if __name__=='__main__':unittest.main()
