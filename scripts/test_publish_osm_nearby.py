import unittest
from unittest.mock import patch
import publish_osm_nearby as publisher

PAIRS=[('node/1','node/2',4.25),('node/2','way/4',14.12)]
DAY='2026-10-25'

class PublicationTests(unittest.TestCase):
 def meta(self):
  with patch.object(publisher,'EXPECTED_MIN_PAIRS',1):
   return publisher.snapshot_meta(DAY,116128,PAIRS)
 def test_snapshot_digest_stable_and_evidence_is_proximity(self):
  m=self.meta()
  self.assertEqual(m['pair_count'],2)
  self.assertEqual(m['source_records_in_pairs'],3)
  self.assertEqual(m['pairs_within_5m'],1)
  self.assertEqual(m['pairs_5_to_15m'],1)
  self.assertEqual(m['snapshot_id'],self.meta()['snapshot_id'])
 def test_incomplete_or_dangerous_audit_held(self):
  with self.assertRaisesRegex(ValueError,'pair count'):
   publisher.snapshot_meta(DAY,116128,PAIRS)
  with patch.object(publisher,'EXPECTED_MIN_PAIRS',1):
   with self.assertRaisesRegex(ValueError,'duplicate'):
    publisher.snapshot_meta(DAY,116128,[PAIRS[0],PAIRS[0]])
   with self.assertRaisesRegex(ValueError,'Invalid OSM'):
    publisher.snapshot_meta(DAY,116128,[('node/2','node/1',5.1)])
 def test_full_staging_then_publication_only_after_exact_count(self):
  m=self.meta();calls=[]
  def rest(table,verb,query=None,body=None,prefer=None):
   calls.append((table,verb,query,body,prefer))
   if verb=='GET':return {},[]
   if verb=='PATCH':return {},[{'snapshot_id':m['snapshot_id']}]
   return {},None
  with patch.object(publisher,'EXPECTED_MIN_PAIRS',1),patch.object(
      publisher,'read_exact_count',return_value=2):
   out=publisher.publish(DAY,116128,PAIRS,rest=rest)
  self.assertEqual(out,m)
  self.assertEqual([i[1] for i in calls],['GET','POST','POST','PATCH'])
  self.assertEqual(calls[2][3][0]['distance_m'],4.25)
  self.assertEqual(calls[-1][3].keys(),{'published_at'})
  self.assertEqual(calls[2][0],'flock_osm_nearby_candidates')
 def test_partial_upload_never_publishes(self):
  calls=[]
  def rest(table,verb,query=None,body=None,prefer=None):
   calls.append(verb)
   return ({},[]) if verb=='GET' else ({},None)
  with patch.object(publisher,'EXPECTED_MIN_PAIRS',1),patch.object(
      publisher,'read_exact_count',return_value=1):
   with self.assertRaisesRegex(ValueError,'publication held'):
    publisher.publish(DAY,116128,PAIRS,rest=rest)
  self.assertNotIn('PATCH',calls)
 def test_rerun_does_not_republish_a_completed_snapshot(self):
  m=self.meta();calls=[]
  def rest(table,verb,query=None,body=None,prefer=None):
   calls.append(verb)
   return {},[{'pair_count':2,'published_at':'2026-10-25T10:00:00Z'}]
  with patch.object(publisher,'EXPECTED_MIN_PAIRS',1),patch.object(
      publisher,'read_exact_count',return_value=2):
   publisher.publish(DAY,116128,PAIRS,rest=rest)
  self.assertEqual(calls,['GET'])

if __name__=='__main__':unittest.main()
