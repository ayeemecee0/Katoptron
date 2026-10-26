"""Unit tests for M9 public workflow readiness; no external API traffic."""
import datetime as dt
import unittest
import monitor_release_gates as m

NOW=dt.datetime(2026,10,26,20,0,tzinfo=dt.timezone.utc)
W='validate.yml'
def run(hours=1,result='success',status='completed',branch='main'):
 stamp=(NOW-dt.timedelta(hours=hours)).isoformat().replace('+00:00','Z')
 return {'head_branch':branch,'created_at':stamp,'status':status,'conclusion':result}

class ReleaseHealth(unittest.TestCase):
 def test_recent_green(self):
  self.assertEqual(m.evaluate(W,[run(4)],NOW),4)
 def test_failure_after_previous_green_blocks_launch(self):
  with self.assertRaisesRegex(ValueError,'FAILED'):
   m.evaluate(W,[run(1,result='failure'),run(14)],NOW)
 def test_stale_success(self):
  with self.assertRaisesRegex(ValueError,'stale'):
   m.evaluate(W,[run(200)],NOW)
 def test_new_running_requires_prior_green(self):
  self.assertEqual(m.evaluate(W,[run(1,None,'in_progress'),run(9)],NOW),9)
  with self.assertRaisesRegex(ValueError,'lacks successful'):
   m.evaluate(W,[run(1,None,'in_progress')],NOW)
 def test_hung_run_blocks_health(self):
  with self.assertRaisesRegex(ValueError,'stuck'):
   m.evaluate(W,[run(3,None,'in_progress'),run(8)],NOW)
 def test_old_failed_job_then_good(self):
  self.assertEqual(m.evaluate(W,[run(1),run(7,'failure')],NOW),1)
 def test_not_a_success(self):
  for conclusion in ('cancelled','skipped','timed_out',None):
   with self.subTest(conclusion=conclusion),self.assertRaises(ValueError):
    m.evaluate(W,[run(1,conclusion)],NOW)
 def test_wrong_branch_and_bad_clock(self):
  with self.assertRaisesRegex(ValueError,'no main-branch'):
   m.evaluate(W,[run(1,branch='other')],NOW)
  with self.assertRaisesRegex(ValueError,'timestamp'):
   m.evaluate(W,[{**run(1),'created_at':'not-a-date'}],NOW)
  with self.assertRaisesRegex(ValueError,'Future'):
   m.evaluate(W,[run(-1)],NOW)
 def test_exact_workflow_allowlist(self):
  with self.assertRaisesRegex(ValueError,'Unexpected'):
   m.evaluate('unreviewed.yml',[run()],NOW)
  self.assertIn('live_community_acceptance.yml',m.REQUIRED)
  self.assertIn('monitor_production_capacity.yml',m.REQUIRED)
if __name__=='__main__':unittest.main()
