"""Offline M9 launch capacity and sensitive telemetry regression."""
import unittest
from unittest.mock import patch
import monitor_production_capacity as m

OK={'database_bytes':117_000_000,
    'private_community_report_count':0,
    'private_community_photo_count':0,
    'private_community_photo_metadata_bytes':0,
    'private_photo_size_metadata_missing':0,
    'retained_one_day_rate_events':0,
    'expired_one_day_rate_events':0,
    'active_auth_accounts':1,
    'registered_private_bucket_count':1}

class Capacity(unittest.TestCase):
 def test_free_capacity_pass_and_no_sensitive_output(self):
    out=m.evaluate(dict(OK))
    self.assertLess(out['database_percent'],30)
    self.assertEqual(out['warnings'],[])
    self.assertNotIn('email',str(out).lower())
 def test_early_warning_is_nonfatal(self):
    o=m.evaluate({**OK,'database_bytes':310_000_000})
    self.assertEqual(o['database_percent'],62)
    self.assertEqual(len(o['warnings']),1)
    o=m.evaluate({**OK,'private_community_photo_metadata_bytes':800_000_000})
    self.assertEqual(len(o['warnings']),1)
 def test_hard_capacity_failures(self):
    with self.assertRaisesRegex(ValueError,'80%'):
      m.evaluate({**OK,'database_bytes':401_000_000})
    with self.assertRaisesRegex(ValueError,'85%'):
      m.evaluate({**OK,'private_community_photo_metadata_bytes':860_000_000})
 def test_storage_permission_and_ttl_fail(self):
    cases=[({**OK,'registered_private_bucket_count':0},'bucket'),
      ({**OK,'private_photo_size_metadata_missing':1},'metadata'),
      ({**OK,'expired_one_day_rate_events':1},'Expired')]
    for arg,msg in cases:
      with self.subTest(msg=msg),self.assertRaisesRegex(ValueError,msg):
        m.evaluate(arg)
 def test_bad_snapshot_never_counts_as_health(self):
    cases=[None,{},[],{**OK,'database_bytes':None},
      {**OK,'private_photo_size_metadata_missing':True},
      {**OK,'unknown_raw_email':'sensitive'}]
    for bad in cases:
      with self.subTest(bad=str(type(bad))),self.assertRaises(ValueError):
       m.evaluate(bad)
 def test_fixed_endpoint_and_thresholds(self):
    self.assertEqual(m.RPC,m.PROJECT+'/rest/v1/rpc/katoptron_private_launch_capacity')
    self.assertLess(m.DATABASE_WARN_AT,m.DATABASE_FAIL_AT)
    self.assertLess(m.BUCKET_WARN_AT,m.BUCKET_FAIL_AT)
if __name__=='__main__':unittest.main()
