import unittest
from unittest.mock import patch
from discover_government_gis_links import Anchors
import probe_live_oak_tx_public_map as source

WEBMAP='a'*32
ORG='AgencyOrg123456'
PAGE=source.CITY
def original(with_map=True):
    d=Anchors()
    d.feed('<h1>Flock Safety Cameras</h1><a href="'+
           (source.APP if with_map else 'https://unrelated.example/')+'">City map</a>')
    return d,'b'*64

def item(url):
    if url==source.ITEM+source.APPID+'?f=json':
        return {'id':source.APPID,'orgId':ORG,'type':'Web Mapping Application'}
    if url==source.ITEM+source.APPID+'/data?f=json':
        return {'values':{'webmap':WEBMAP}}
    if url==source.ITEM+WEBMAP+'?f=json':
        return {'id':WEBMAP,'orgId':ORG,'type':'Web Map'}
    if url==source.ITEM+WEBMAP+'/data?f=json':
        return {'operationalLayers':[{'title':'Flock Cameras','id':'flock-layer'},
                                    {'title':'Transportation','id':'street-layer'}]}
    raise AssertionError('Unexpected original Esri item URL')

class OriginalCityMapTests(unittest.TestCase):
    def test_genuine_app_same_publisher_webmap(self):
        self.assertEqual(source.audit(fetch=item,page_fetch=lambda _:original()),1)
    def test_unlinked_arbitrary_app_rejected(self):
        with self.assertRaisesRegex(ValueError,'no longer links'):
            source.audit(fetch=item,page_fetch=lambda _:original(False))
    def test_webmap_organization_mismatch_held(self):
        def fake(url):
            d=item(url)
            if url==source.ITEM+WEBMAP+'?f=json':return {**d,'orgId':'OtherAgency'}
            return d
        with self.assertRaisesRegex(ValueError,'publisher differs'):
            source.audit(fetch=fake,page_fetch=lambda _:original())
    def test_multiple_webmaps_held(self):
        result=source.map_identifiers({'values':{'webmap':WEBMAP,
            'config':{'mapId':'b'*32}}})
        self.assertEqual(len(result),2)
        def fake(url):
            if url==source.ITEM+source.APPID+'/data?f=json':
                return {'values':{'webmap':WEBMAP,'mapId':'b'*32}}
            return item(url)
        with self.assertRaisesRegex(ValueError,'exactly one'):
            source.audit(fetch=fake,page_fetch=lambda _:original())

if __name__=='__main__':unittest.main()
