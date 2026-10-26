"""Offline failure-path acceptance for production M1-M3 audit."""
import copy
import datetime as dt
import unittest
import audit_m1_m3_production as audit

URL='https://city.example.gov/rest/Flock/FeatureServer/0'
CITY='City, ST'
NOW=dt.datetime.now(dt.timezone.utc)
def snapshot():
    return (
        [{'record_key':'gis-authority-1','label':'Agency camera',
          'jurisdiction_label':CITY,'latitude':38.5,'longitude':-121.5,
          'source_url':URL,'evidence_sha256':'a'*64,
          'evidence_summary':'Original government camera location',
          'verification_status':'verified','location_accuracy':'exact',
          'verification_method':'official_georeferenced_camera_record_v1',
          'last_source_recheck_at':NOW.isoformat(),
          'source_flock_label_status':'unconfirmed'}],
        [{'source_key':'authority','gis_layer_url':URL,
          'jurisdiction_label':CITY,'source_status':'verified'}],
        [{'case_key':'tier-1','source_key':'second','source_url':URL+'-alt',
          'jurisdiction_label':'Other, ST','latitude':39.1,'longitude':-122.1,
          'evidence_sha256':'b'*64,
          'caveat':'NOT independently hardware verified or currently operational',
          'publication_status':'active','source_checked_at':NOW.isoformat()}],
        [{'source_key':'second','gis_layer_url':URL+'-alt',
          'jurisdiction_label':'Other, ST','policy_status':'approved'}],
        [{'gis_layer_url':'https://gis.example.org/candidate','trust_status':'unverified'}],
        [{'gis_layer_url':'https://gis.example.org/candidate',
          'disposition':'investigate_original_agency',
          'next_review_after':'2026-11-25T00:00:00+00:00'}]
    )

class SourceTierAcceptance(unittest.TestCase):
    def test_bounded_complete_separate_layers(self):
        result=audit.check(snapshot(),1)
        self.assertEqual(result['verified_source_points'],1)
        self.assertEqual(result['unconfirmed_source_points'],1)
        self.assertEqual(result['research_remaining'],1)

    def test_no_untrusted_source_promoted(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[1][0]['source_status']='unverified'
        with self.assertRaisesRegex(ValueError,'No current independently approved source'):
            audit.check(sample,1)

    def test_bad_digest_or_missing_recheck_held(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[0][0]['evidence_sha256']='broken'
        with self.assertRaisesRegex(ValueError,'provenance'):
            audit.check(sample,1)
        sample=list(copy.deepcopy(snapshot()))
        sample[0][0]['last_source_recheck_at']=None
        with self.assertRaisesRegex(ValueError,'provenance'):
            audit.check(sample,1)

    def test_original_source_cannot_be_counted_twice(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[0].append(copy.deepcopy(sample[0][0]))
        with self.assertRaisesRegex(ValueError,'provenance'):
            audit.check(sample,1)

    def test_unconfirmed_overlap_must_fail(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[2][0]['jurisdiction_label']=CITY
        sample[3][0]['jurisdiction_label']=CITY
        sample[2][0]['latitude']=38.5
        sample[2][0]['longitude']=-121.5
        with self.assertRaisesRegex(ValueError,'overlaps'):
            audit.check(sample,1)

    def test_manually_reopened_source_is_actionable_without_fake_certification(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[5][0]['disposition']='needs_review'
        sample[5][0]['next_review_after']=None
        result=audit.check(sample,1)
        self.assertEqual(result['research_remaining'],1)
        self.assertEqual(result['trusted_source_count'],1)

    def test_missing_lifecycle_state_held(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[5].clear()
        with self.assertRaisesRegex(ValueError,'Unclassified'):
            audit.check(sample,1)

    def test_live_oak_generic_lpr_requires_disclaimer(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[1][0]['source_key']='live_oak_tx'
        with self.assertRaisesRegex(ValueError,'Generic Live Oak LPR'):
            audit.check(sample,1)
        sample[0][0]['evidence_summary']+='; NOT per-device manufacturer'
        sample[0][0]['source_flock_label_status']='generic_lpr'
        self.assertEqual(audit.check(sample,1)['live_oak_source_positions'],1)

    def test_source_flock_label_undocumented_or_missing_rejected(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[0][0]['source_flock_label_status']='source_flock_identified'
        with self.assertRaisesRegex(ValueError,'reviewed source key'):
            audit.check(sample,1)
        sample[0][0]['source_flock_label_status']=None
        with self.assertRaisesRegex(ValueError,'not classified'):
            audit.check(sample,1)

    def test_positive_label_only_for_pinned_flock_source(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[1][0]['source_key']='monroe_wa'
        sample[0][0]['source_flock_label_status']='source_flock_identified'
        result=audit.check(sample,1)
        self.assertEqual(result['source_labeled_flock_points'],1)
        self.assertEqual(result['generic_lpr_source_points'],0)
        sample[0][0]['source_flock_label_status']='unconfirmed'
        with self.assertRaisesRegex(ValueError,'unexpectedly changed'):
            audit.check(sample,1)

    def test_government_recheck_freshness_and_future_skew(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[0][0]['last_source_recheck_at']=(NOW-dt.timedelta(days=366)).isoformat()
        with self.assertRaisesRegex(ValueError,'freshness'):
            audit.check(sample,1,now=NOW)
        sample[0][0]['last_source_recheck_at']=(NOW+dt.timedelta(minutes=11)).isoformat()
        with self.assertRaisesRegex(ValueError,'freshness'):
            audit.check(sample,1,now=NOW)
        sample[0][0]['last_source_recheck_at']='not-a-date'
        with self.assertRaisesRegex(ValueError,'freshness'):
            audit.check(sample,1,now=NOW)

    def test_low_confidence_source_recheck_freshness(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[2][0]['source_checked_at']=(NOW-dt.timedelta(days=15)).isoformat()
        with self.assertRaisesRegex(ValueError,'Unconfirmed source-publication'):
            audit.check(sample,1,now=NOW)
        sample[2][0]['source_checked_at']=(NOW+dt.timedelta(minutes=15)).isoformat()
        with self.assertRaisesRegex(ValueError,'Unconfirmed source-publication'):
            audit.check(sample,1,now=NOW)

    def test_invalid_gis_coordinates_fail(self):
        sample=list(copy.deepcopy(snapshot()))
        sample[0][0]['latitude']=float('nan')
        with self.assertRaisesRegex(ValueError,'geometry'):
            audit.check(sample,1)

if __name__=='__main__':
    unittest.main()
