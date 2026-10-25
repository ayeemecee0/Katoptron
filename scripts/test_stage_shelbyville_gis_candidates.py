"""Offline privacy and append-only staging regression for Shelbyville."""
import unittest
from unittest.mock import patch
import stage_shelbyville_gis_candidates as s

PROOF = {
    'gov_page_sha256': 'a'*64,
    'arcgis_org_id': '0Uo0Kvp9YTHRegvR',
    'private_original_points': [
       {'id':1, 'lat':35.5, 'lon':-86.5},
       {'id':2, 'lat':35.51, 'lon':-86.51},
    ]
}

class StageTests(unittest.TestCase):
    def test_private_receipts_never_auto_review(self):
        cases, evidence = s.make_receipts(PROOF)
        self.assertEqual(len(cases), 2)
        self.assertEqual(len(evidence), 2)
        self.assertTrue(all('classification' not in p and 'reviewed_at' not in p
                            for p in cases))
        self.assertTrue(all('evidence_status' not in p and 'reviewed_at' not in p
                            for p in evidence))
        self.assertEqual(evidence[0]['source_kind'], 'government_arcgis_organization')
        self.assertEqual(s.make_receipts(PROOF), (cases,evidence))
        new=dict(PROOF,private_original_points=[
            {'id':1, 'lat':35.5001, 'lon':-86.5},PROOF['private_original_points'][1]
        ])
        self.assertNotEqual(s.make_receipts(new)[1][0]['evidence_sha256'],
                            evidence[0]['evidence_sha256'])
    def test_duplicate_feature_id_held(self):
        duplicate=dict(PROOF,private_original_points=[PROOF['private_original_points'][0]]*2)
        with self.assertRaisesRegex(ValueError,'duplicate'):
            s.make_receipts(duplicate)
    def test_dry_run_cannot_write(self):
        def prohibited_api(*args,**kwargs):
            raise AssertionError('Dry run used a live private write')
        with patch.object(s,'fetch_all',return_value=[{
            'latitude':38.5,'longitude':-121.5} for _ in range(293)]):
            n=s.run(stage_private=False,api=prohibited_api,audited=lambda **kw:PROOF)
        self.assertEqual(n,2)
    def test_private_stage_only_writes_unreviewed_tables(self):
        writes=[]
        def api(route,method=None,payload=None,prefer=None):
            if method=='POST':
                writes.append((route,payload))
                return None
            return []
        with (patch.object(s,'fetch_all',return_value=[{
            'latitude':38.5,'longitude':-121.5} for _ in range(293)]),
            patch.object(s,'hold_conflicting_staged_evidence',return_value=None)):
            self.assertEqual(s.run(stage_private=True,api=api,
                                   audited=lambda **kw:PROOF),2)
        self.assertEqual(len(writes),2)
        self.assertTrue(writes[0][0].startswith('flock_point_evidence_cases?'))
        self.assertTrue(writes[1][0].startswith('flock_point_evidence_attestations?'))
        self.assertNotIn('reviewed_at',str(writes))
        self.assertNotIn('government_verified',str(writes))

if __name__=='__main__':
    unittest.main()
