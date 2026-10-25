"""Source-level government ArcGIS map-app discovery is private and auditable."""
import unittest
from unittest.mock import Mock
from discover_government_gis_links import Anchors
import discover_original_gov_camera_map_apps as d

APP='https://liveoaktx.maps.arcgis.com/apps/instant/basic/index.html?appid=1fe4ad954b3346b9a7e2a3a337c5cfbf'
GOV='https://www.liveoaktx.net/departments/police/flock-safety'
SHA='b'*64
def doc(link=APP,label='Live Oak Camera Map',prose='Flock Safety ALPR cameras'):
    item=Anchors()
    item.feed('<h1>'+prose+'</h1><a href="'+link+'">'+label+'</a>')
    return item

def fetch_item(url):
    assert url.startswith(d.ITEM)
    return {'id':'1fe4ad954b3346b9a7e2a3a337c5cfbf',
            'owner':'liveoaktx','type':'Web Mapping Application'}

class GovCameraAppTests(unittest.TestCase):
    def test_city_page_and_exact_app_becomes_unreviewed_private_research(self):
        out=d.proposed(doc(),GOV,SHA,fetch_item)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]['government_page_url'],GOV)
        self.assertEqual(out[0]['app_url'],APP)
        self.assertNotIn('verification_status',out[0])
        self.assertNotIn('latitude',out[0])
    def test_unrelated_publisher_and_planning_app_rejected(self):
        for app in (
          'https://liveoaktx.maps.arcgis.com.evil.com/apps/instant/basic/index.html?appid=1fe4ad954b3346b9a7e2a3a337c5cfbf',
          APP+'&redirect=https://example.org',
          APP.replace('https:','http:'),
          APP.replace('appid=','url='),
          APP+'#unexpected'
        ):
            self.assertIsNone(d.map_app_url(app))
        self.assertEqual(d.proposed(doc(label='Community Parks Map'),GOV,SHA,fetch_item),[])
        self.assertEqual(d.proposed(doc(prose='City planning and public facilities'),GOV,SHA,fetch_item),[])
    def test_id_only_is_not_an_identity_attestation(self):
        out=d.proposed(doc(),GOV,SHA,lambda _: {'id':'a'*32,
                     'owner':'someone','type':'Web Mapping Application'})
        self.assertEqual(out,[])
    def test_private_append_only_receipts_and_removed_source_hold(self):
        row=d.proposed(doc(),GOV,SHA,fetch_item)[0]
        writes=[]
        def api(path,method='GET',payload=None,prefer=None):
            writes.append((path,method,payload))
            return [] if method=='GET' else None
        values=d.sync_original_page(GOV,[row],api)
        self.assertEqual(values['new_private_apps'],1)
        self.assertEqual([w[1] for w in writes],['GET','POST','POST'])
        self.assertTrue(writes[2][0].startswith('flock_government_camera_map_app_receipts?'))
        self.assertNotIn('flock_camera_locations',str(writes))
        writes.clear()
        def existing(path,method='GET',payload=None,prefer=None):
            writes.append((path,method,payload))
            if method=='GET':return [{'app_url':APP,'agency_page_sha256':SHA,'evidence_status':'reviewed'}]
            return None
        out=d.sync_original_page(GOV,[],existing)
        self.assertEqual(out['removed_links_held'],1)
        self.assertEqual(writes[1][2]['evidence_status'],'held')
    def test_page_digest_drift_freezes_reviewed_lead_not_camera(self):
        row=d.proposed(doc(),GOV,'c'*64,fetch_item)[0]
        calls=[]
        def api(path,method='GET',payload=None,prefer=None):
            calls.append((path,method,payload))
            if method=='GET':
                return [{'app_url':APP,'agency_page_sha256':SHA,'evidence_status':'reviewed'}]
            return None
        out=d.sync_original_page(GOV,[row],api)
        self.assertEqual(out['held_due_to_evidence_change'],1)
        self.assertEqual(calls[1][2]['evidence_status'],'held')
        self.assertEqual(calls[2][2][0]['agency_page_sha256'],'c'*64)

if __name__=='__main__':
    unittest.main()
