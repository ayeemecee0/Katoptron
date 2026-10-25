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
    def test_privacy_safe_diagnostics_classify_only_allowlisted_internal_errors(self):
        from audit_affiliated_flock_inventory import InventoryHeld
        self.assertEqual(
            m.safe_held_reason(InventoryHeld('original ObjectID inventory unavailable')),
            'InventoryHeld:source_inventory_unavailable')
        # Never leak a new exception message: it can contain untrusted
        # original-service responses, unpublished source URLs or coordinates.
        self.assertEqual(m.safe_held_reason(InventoryHeld('untrusted 31,-86.3 URL')),
                         'InventoryHeld')
        self.assertEqual(m.safe_held_reason(ValueError('private response text')),
                         'ValueError')

    def test_source_page_html_drift_can_refresh_only_existing_unchanged_pins(self):
        from audit_affiliated_flock_inventory import InventoryHeld
        cases, current = m.make_receipts(proof())
        original_hash = 'b'*64
        old = [dict(e, evidence_sha256=original_hash, evidence_status='staged')
               for e in current]
        prior = [dict(case_key=c['case_key'], latitude=c['latitude'],
                      longitude=c['longitude'], evidence_sha256=original_hash,
                      publication_status='active') for c in cases]
        writes = []
        def api(path, method=None, payload=None, prefer=None):
            if method=='POST':
                writes.extend(payload)
                return None
            if path.startswith('flock_source_attributed_map_points?'):
                return prior
            if path.startswith('flock_point_evidence_attestations?'):
                return old
            raise AssertionError('Unexpected source '+path)
        with (patch.object(m, 'hold_conflicting_staged_evidence',
                           side_effect=InventoryHeld(
                              'Private source proof changed; independent review required')),
              patch.object(m, 'fetch_all', return_value=[
                 {'latitude':38.5,'longitude':-121.5,
                  'jurisdiction_label':'Elsewhere'} for _ in range(316)])):
            self.assertEqual(m.run(True,api,lambda **kw:proof()),12)
        self.assertEqual(len(writes),12)
        self.assertEqual({w['evidence_sha256'] for w in writes},{original_hash})
        self.assertEqual({w['publication_status'] for w in writes},{'active'})

    def test_provenance_drift_never_refreshes_withdrawn_or_changed_receipt(self):
        cases, current = m.make_receipts(proof())
        old = [dict(e, evidence_sha256='b'*64, evidence_status='staged')
               for e in current]
        prior = [dict(case_key=c['case_key'], latitude=c['latitude'],
                      longitude=c['longitude'], evidence_sha256='b'*64,
                      publication_status='active') for c in cases]
        def api(path, **kw):
            if path.startswith('flock_point_evidence_attestations?'):
                return old
            return prior
        old[0]['evidence_status']='withdrawn'
        with self.assertRaisesRegex(ValueError,'revoked'):
            m.retain_immutable_provenance_if_page_changed(cases,current,prior,api)
        old[0]['evidence_status']='staged'
        prior[0]['longitude']+=0.001
        with self.assertRaisesRegex(ValueError,'no longer matches'):
            m.retain_immutable_provenance_if_page_changed(cases,current,prior,api)
        prior[0]['longitude']=cases[0]['longitude']
        prior[0]['publication_status']='withdrawn'
        with self.assertRaisesRegex(ValueError,'withdrawn'):
            m.retain_immutable_provenance_if_page_changed(cases,current,prior,api)

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
