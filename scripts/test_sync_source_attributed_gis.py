"""Offline tier boundaries and fail-closed publication regression."""
import unittest
from unittest.mock import patch
import sync_source_attributed_gis as m

def proof():
    return {'gov_page_sha256':'a'*64,
            'arcgis_org_id':'SourcePublisher123',
            'private_original_points':[
                {'id':i+1,'lat':35.48+i*0.001,'lon':-86.46-i*0.001}
                for i in range(12)]}

class SourceAttribution(unittest.TestCase):
    def test_dry_run_never_writes_government_or_lower_tier(self):
        def api(path,method=None,payload=None,prefer=None):
            self.assertNotEqual(method,'POST')
            return []
        with (patch.object(m,'hold_conflicting_staged_evidence'),
              patch.object(m,'fetch_all',return_value=[
                 {'latitude':38.5,'longitude':-121.5,
                  'jurisdiction_label':'Elsewhere'} for _ in range(316)])):
            self.assertEqual(m.run(False,api,lambda **kw:proof()),12)

    def test_existing_evidence_drift_blocks_tier_refresh(self):
        def api(path,method=None,payload=None,prefer=None):
            self.assertNotEqual(method,'POST')
            return [{'case_key':m.make_receipts(proof())[0][0]['case_key'],
                     'latitude':35.48,'longitude':-86.46,
                     'evidence_sha256':'b'*64,'publication_status':'active'}]
        with (patch.object(m,'hold_conflicting_staged_evidence'),
              patch.object(m,'fetch_all',return_value=[
                 {'latitude':38.5,'longitude':-121.5,
                  'jurisdiction_label':'Elsewhere'} for _ in range(316)])):
            with self.assertRaisesRegex(ValueError,'fingerprint drift'):
                m.run(True,api,lambda **kw:proof())

    def test_only_source_attributed_table_can_receive_new_points(self):
        writes=[]
        def api(path,method=None,payload=None,prefer=None):
            if method=='POST':
                writes.append((path,payload))
                return None
            return []
        with (patch.object(m,'hold_conflicting_staged_evidence'),
              patch.object(m,'fetch_all',return_value=[
                 {'latitude':38.5,'longitude':-121.5,
                  'jurisdiction_label':'Elsewhere'} for _ in range(316)])):
            self.assertEqual(m.run(True,api,lambda **kw:proof()),12)
        self.assertEqual(len(writes),1)
        self.assertTrue(writes[0][0].startswith('flock_source_attributed_map_points?'))
        self.assertEqual({x['publication_status'] for x in writes[0][1]}, {'active'})
        self.assertTrue(all('NOT established' in r['caveat'] for r in writes[0][1]))
        self.assertNotIn('flock_camera_locations',str(writes))

if __name__=='__main__':unittest.main()
