"""Safe checks for read-only, source-associated Flock feature inventories."""
import urllib.parse
import unittest
import audit_affiliated_flock_inventory as m

URL='https://services3.arcgis.com/Example123/arcgis/rest/services/Flock_Cameras/FeatureServer/0'
SERVICE={'layers':[{'id':0,'name':'Flock Cameras'}]}
LAYER={'name':'Flock Cameras','type':'Feature Layer',
       'geometryType':'esriGeometryPoint','objectIdField':'OBJECTID',
       'fields':[{'name':'OBJECTID','type':'esriFieldTypeOID'},
                 {'name':'CameraID','type':'esriFieldTypeString'}]}
def expected(url):
    if url==URL.rsplit('/',1)[0]+'?f=json':return SERVICE
    if url==URL+'?f=json':return LAYER
    if '/query?' not in url:raise AssertionError('unapproved upstream endpoint')
    q=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    if q.get('returnIdsOnly')==['true']:
        return {'objectIdFieldName':'OBJECTID','objectIds':[3,8]}
    if q.get('objectIds')==['3,8']:
        return {'features':[
         {'attributes':{'OBJECTID':3},'geometry':{'x':-117.16,'y':33.69}},
         {'attributes':{'OBJECTID':8},'geometry':{'x':-117.15,'y':33.70}}]}
    raise AssertionError('unexpected read')

class Inventory(unittest.TestCase):
 def test_complete_two_snapshot_inventory_with_no_coordinates_in_result(self):
    result=m.inspect(URL,'Flock Cameras','OBJECTID',expected)
    self.assertEqual(result['features'],2)
    self.assertTrue(result['stable_original_ids'])
    self.assertTrue(result['has_individual_camera_id_field'])
    self.assertNotIn('latitude',str(result))
    self.assertNotIn('-117.15',str(result))
 def test_unapproved_hosts_are_never_fetched(self):
    for url in ('http://services.arcgis.com/a/arcgis/rest/services/Flock/FeatureServer/0',
                'https://example.org/arcgis/rest/services/Flock/FeatureServer/0',
                'https://services.arcgis.com.evil.example/x/arcgis/rest/services/Flock/FeatureServer/0'):
       with self.subTest(url=url):
        with self.assertRaises(m.InventoryHeld):
         m.inspect(url,'Flock Cameras','OBJECTID',
                   lambda _:self.fail('unsafe fetch'))
 def test_original_parent_name_and_geometry_are_required(self):
    def wrong(url):
     x=expected(url)
     if url.endswith('/0?f=json'):
      return {**x,'geometryType':'esriGeometryPolygon'}
     return x
    with self.assertRaises(m.InventoryHeld):
     m.inspect(URL,'Flock Cameras','OBJECTID',wrong)
 def test_missing_objectid_and_changed_second_snapshot_fail_closed(self):
    calls=[0]
    def drift(url):
     x=expected(url)
     if 'returnIdsOnly=true' in url:
      calls[0]+=1
      if calls[0]==2:return {'objectIdFieldName':'OBJECTID','objectIds':[3,9]}
     return x
    with self.assertRaisesRegex(m.InventoryHeld,'changed'):
     m.inspect(URL,'Flock Cameras','OBJECTID',drift)
 def test_duplicate_original_id_is_not_published(self):
    def duplicate(url):
     x=expected(url)
     if 'returnIdsOnly=true' in url:
      return {'objectIdFieldName':'OBJECTID','objectIds':[3,3]}
     return x
    with self.assertRaisesRegex(m.InventoryHeld,'duplicate'):
     m.inspect(URL,'Flock Cameras','OBJECTID',duplicate)
 def test_partial_feature_response_and_offsite_point_are_held(self):
    def shortened(url):
     x=expected(url)
     if 'objectIds=3%2C8' in url:
      return {'features':x['features'][:1]}
     return x
    with self.assertRaisesRegex(m.InventoryHeld,'incomplete'):
     m.inspect(URL,'Flock Cameras','OBJECTID',shortened)
    def offsite(url):
     x=expected(url)
     if 'objectIds=3%2C8' in url:
      return {'features':[x['features'][0],
           {'attributes':{'OBJECTID':8},'geometry':{'x':0,'y':0}}]}
     return x
    with self.assertRaisesRegex(m.InventoryHeld,'valid US point'):
     m.inspect(URL,'Flock Cameras','OBJECTID',offsite)

if __name__=='__main__':unittest.main()
