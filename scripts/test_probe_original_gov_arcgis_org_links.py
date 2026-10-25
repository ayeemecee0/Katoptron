import contextlib
import io
import unittest
from unittest.mock import patch
from discover_government_gis_links import Anchors
import probe_original_gov_arcgis_org_links as a

ORG={'org_id':'ABCD12345678','portal_url_key':'CityGIS',
     'portal_base_url':'maps.arcgis.com'}
URL='https://services3.arcgis.com/0Uo0Kvp9YTHRegvR/arcgis/rest/services/Flock_Cameras_-_Public/FeatureServer/0'
C={'gis_layer_url':URL,'layer_name':'Flock Cameras'}

def document(html):
    p=Anchors()
    p.feed(html)
    return p

class GovPublisher(unittest.TestCase):
 def test_exact_esri_organization_link_not_generic_esri_page(self):
    self.assertTrue(a.is_exact_esri_org_link(
        'https://www.arcgis.com/home/organization.html?orgId=ABCD12345678',ORG))
    self.assertTrue(a.is_exact_esri_org_link('https://citygis.maps.arcgis.com/home/index.html',ORG))
    for u in ('https://www.arcgis.com/home/organization.html?orgId=anotherOrgId',
              'https://www.arcgis.com/home/organization.html',
              'https://www.arcgis.com/home/organization.html?orgId=ABCD12345678&orgId=other',
              'https://www.arcgis.com/home/item.html?id=ABCD12345678',
              'https://evil.example/organization.html?orgId=ABCD12345678',
              'http://www.arcgis.com/home/organization.html?orgId=ABCD12345678',
              'https://citygis.maps.arcgis.com/home/index.html?redirect=evil',
              'https://fake.maps.arcgis.com/home/index.html'):
       with self.subTest(url=u):
        self.assertFalse(a.is_exact_esri_org_link(u,ORG))
 def test_original_gov_arcgis_web_application_owner_verification(self):
    appid='a'*32
    base='https://citygis.maps.arcgis.com/apps/webappviewer/index.html?id='+appid
    item='https://www.arcgis.com/sharing/rest/content/items/'+appid+'?f=json'
    def owned_fetch(url):
       self.assertEqual(url,item)
       return {'id':appid,'type':'Web Mapping Application',
               'owner':'municipalgis','orgId':'ABCD12345678'}
    doc=document('<p>Official city GIS map.</p><a href="'+base+'">City map</a>')
    self.assertTrue(a.linked_government_org(doc,'https://originalcity.gov/gis',ORG,owned_fetch))
    self.assertFalse(a.linked_government_org(doc,'https://originalcity.gov/gis',
        {**ORG,'org_id':'DIFFERENT1234'},owned_fetch))

 def test_original_city_mapviewer_is_private_publisher_proof_only(self):
    webmap='b567681267f642f1bd5e23e4960d64e9'
    city_link='https://citygis.maps.arcgis.com/apps/mapviewer/index.html?webmap='+webmap
    doc=document('<a href="'+city_link+'">Mapping Information</a>')
    endpoint='https://www.arcgis.com/sharing/rest/content/items/'+webmap+'?f=json'
    def matched_fetch(url):
       self.assertEqual(url,endpoint)
       return {'id':webmap,'type':'Web Map','owner':'city_planning',
               'orgId':'ABCD12345678'}
    self.assertTrue(a.linked_government_org(doc,'https://city.gov/planning',ORG,matched_fetch))
    self.assertFalse(a.linked_government_org(doc,'https://city.gov/planning',
        {**ORG,'org_id':'DIFFERENT1234'},matched_fetch))
    self.assertFalse(a.linked_government_org(doc,'https://city.gov/planning',ORG,
        lambda _: {'id':webmap,'type':'Feature Service','owner':'city_planning',
                   'orgId':'ABCD12345678'}))
    for bad in (city_link+'&next=evil',city_link.replace('webmap=','appid='),
                city_link.replace('citygis.maps','fakegis.maps'),
                city_link.replace('https:','http:'),
                city_link+'#fragment'):
       with self.subTest(bad=bad):
          self.assertFalse(a.independently_owned_arcgis_application(bad,ORG,matched_fetch))
 def test_arcgis_app_spoofing_and_unrelated_item_rejected(self):
    appid='b'*32
    base='https://citygis.maps.arcgis.com/apps/webappviewer/index.html?id='+appid
    def unauthorised(_):
       return {'id':appid,'type':'Web Mapping Application',
               'owner':'attacker','orgId':'SOMEOTHERORG'}
    for url in (
        'https://fakegis.maps.arcgis.com/apps/webappviewer/index.html?id='+appid,
        'http://citygis.maps.arcgis.com/apps/webappviewer/index.html?id='+appid,
        base+'&next=https://evil.example',
        base+'&id='+appid,
        'https://citygis.maps.arcgis.com/apps/webappviewer/index.html?id=invalid',
        'https://citygis.maps.arcgis.com/home/item.html?id='+appid,
        'https://citygis.maps.arcgis.com/apps/webappviewer/index.html?id='+appid+'#fragment'
    ):
       with self.subTest(url=url):
          self.assertFalse(a.independently_owned_arcgis_application(url,ORG,unauthorised))
    self.assertFalse(a.independently_owned_arcgis_application(base,ORG,unauthorised))
 def test_arcgis_orgid_can_be_verified_via_exact_owner_profile(self):
    appid='c'*32
    base='https://citygis.maps.arcgis.com/apps/Shortlist/index.html?appid='+appid
    def owner_fetch(url):
      if '/content/items/' in url:
        return {'id':appid,'type':'Web Mapping Application','owner':'municipalgis'}
      if '/community/users/municipalgis' in url:
        return {'username':'municipalgis','orgId':'ABCD12345678'}
      raise AssertionError('unexpected endpoint')
    self.assertTrue(a.independently_owned_arcgis_application(base,ORG,owner_fetch))
    self.assertFalse(a.independently_owned_arcgis_application(base,ORG,
       lambda _: {'error':'unavailable'}))
 def test_government_app_lead_alone_never_promotes_a_camera(self):
    appid='d'*32
    doc=document('<h1>Official municipal GIS</h1><a href="https://citygis.maps.arcgis.com/apps/instant/minimalist/index.html?appid='+
       appid+'">Map app</a>')
    def owned(url):
       return {'id':appid,'type':'Web Mapping Application',
               'owner':'municipalgis','orgId':'ABCD12345678'}
    self.assertTrue(a.linked_government_org(doc,'https://city.gov/maps',ORG,owned))
    with (patch.object(a,'candidate_inputs',return_value=([C],[],[])),
          patch.object(a,'government_pages',return_value=['https://city.gov/maps']),
          patch.object(a,'fetch_government_page',return_value=(doc,'a'*64)),
          patch.object(a,'check_external',
             return_value='verified_arcgis_metadata_only_missing_original_government_link'),
          patch.object(a,'inspect_arcgis_publisher',return_value=ORG),
          patch.object(a,'inspect_camera_inventory',return_value={
             'features':12,'stable_original_ids':True,
             'bounded_point_geometry':True,'has_individual_camera_id_field':True}),
          patch.object(a,'get_official_json',side_effect=owned),
          io.StringIO() as output):
       with contextlib.redirect_stdout(output):
          result=a.run()
       self.assertEqual(result['gov_page_links_exact_esri_organization'],1)
       self.assertIn('camera locations automatically verified: 0',output.getvalue())
 def test_false_esri_portal_custom_domain_never_authorized(self):
    self.assertFalse(a.is_exact_esri_org_link(
      'https://citygis.maps.arcgis.com/home/index.html',
      {**ORG,'portal_base_url':'attacker.example.com'}))
 def test_original_agency_link_must_match_exact_org(self):
    original=document('<a href="https://citygis.maps.arcgis.com/home/">City GIS</a>')
    self.assertTrue(a.linked_government_org(original,'https://originalcity.gov/gis',ORG))
    original=document('<a href="https://www.arcgis.com/">Generic Esri</a>')
    self.assertFalse(a.linked_government_org(original,'https://originalcity.gov/gis',ORG))
 def test_readonly_audit_does_not_promote_from_portal_claim(self):
    docs=document('<a href="https://citygis.maps.arcgis.com/home/">City GIS</a>')
    fake='https://originalcity.gov/gis'
    with (patch.object(a,'candidate_inputs',return_value=([C],[],[])),
          patch.object(a,'government_pages',return_value=[fake]),
          patch.object(a,'fetch_government_page',return_value=(docs,'a'*64)),
          patch.object(a,'check_external',return_value=
            'verified_arcgis_metadata_only_missing_original_government_link'),
          patch.object(a,'inspect_arcgis_publisher',return_value=ORG),
          patch.object(a,'inspect_camera_inventory',return_value={
             'features':12,'stable_original_ids':True,
             'bounded_point_geometry':True,'has_individual_camera_id_field':True}),
          io.StringIO() as output):
      with contextlib.redirect_stdout(output):
       result=a.run()
      logs=output.getvalue()
    self.assertEqual(result['gov_page_links_exact_esri_organization'],1)
    self.assertIn('camera locations automatically verified: 0',logs)
    self.assertNotIn(URL,logs)
    self.assertNotIn(fake,logs)
 def test_missing_gov_endorsement_held(self):
    docs=document('<a href="https://unverified.maps.arcgis.com/home/">Map</a>')
    with (patch.object(a,'candidate_inputs',return_value=([C],[],[])),
          patch.object(a,'government_pages',return_value=['https://city.gov/gis']),
          patch.object(a,'fetch_government_page',return_value=(docs,'a'*64)),
          patch.object(a,'check_external',return_value=
           'verified_arcgis_metadata_only_missing_original_government_link'),
          patch.object(a,'inspect_arcgis_publisher',return_value=ORG),
          patch.object(a,'inspect_camera_inventory',return_value={
             'features':12,'stable_original_ids':True,
             'bounded_point_geometry':True,'has_individual_camera_id_field':True}),
          io.StringIO() as output):
      with contextlib.redirect_stdout(output):
       result=a.run()
    self.assertEqual(result['original_government_organization_link_missing'],1)
    self.assertEqual(result['gov_page_links_exact_esri_organization'],0)
 def test_unknown_original_gov_page_fails_closed(self):
    with (patch.object(a,'candidate_inputs',return_value=([C],[],[])),
          patch.object(a,'government_pages',return_value=[])):
      with self.assertRaisesRegex(ValueError,'No independently governed'):
       a.run()

if __name__=='__main__':unittest.main()
