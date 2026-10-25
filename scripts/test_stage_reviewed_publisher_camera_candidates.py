import io
import contextlib
import unittest
from unittest.mock import patch
from discover_government_gis_links import Anchors
import stage_reviewed_publisher_camera_candidates as s

OID1={'id':3,'lat':33.7,'lon':-117.15}
OID2={'id':8,'lat':33.71,'lon':-117.16}
D='a'*64
ORG={'org_id':'EXAMPLE1234','portal_url_key':'citygis',
     'portal_base_url':'maps.arcgis.com'}
C={'gis_layer_url':s.GIS,'layer_name':s.NAME,
   'object_id_field':'OBJECTID','geometry_type':'esriGeometryPoint',
   'trust_status':'unverified'}

def make(html):
    a=Anchors();a.feed(html);return a
def page(url):
    if url==s.CITY:return make('<h1>City GIS</h1><p>Original city maps.</p>'),D
    if url==s.POLICE:return make('<h1>Flock Safety ALPR cameras</h1>'),D
    raise AssertionError('unreviewed original page')
def good_api(path,method='GET',payload=None,prefer=None):
    if path.startswith('flock_documented_programs?'):
        return [{'official_evidence_url':s.POLICE,'program_status':'documented_at_source_date',
                 'record_status':'verified'}]
    if path.startswith('flock_gis_source_candidates?'):
        return [C]
    raise AssertionError('Unexpected write')
def proof(*args,**kwargs):
    return {'features':2,'stable_original_ids':True,
            'bounded_point_geometry':True,
            'has_individual_camera_id_field':False,
            '_private_points':[OID1,OID2]}

class PublisherStage(unittest.TestCase):
 def test_privately_stages_only_candidate_and_unreviewed_evidence(self):
    writes=[]
    def api(path,method='GET',payload=None,prefer=None):
      if method=='GET':return good_api(path,method,payload,prefer)
      writes.append((path,payload,prefer))
      return None
    with (patch.object(s,'inspect',side_effect=proof),
          patch.object(s,'linked_government_org',return_value=True),
          patch.object(s,'original_camera_disclosure',return_value=True),
          io.StringIO() as buffer):
      with contextlib.redirect_stdout(buffer):
        self.assertEqual(s.run(True,api,page,lambda _: {},lambda *a,**k:ORG),2)
      printed=buffer.getvalue()
    self.assertEqual(len(writes),2)
    self.assertIn('flock_point_evidence_cases?',writes[0][0])
    self.assertIn('flock_point_evidence_attestations?',writes[1][0])
    cases,evidence=writes[0][1],writes[1][1]
    self.assertEqual(len(cases),2)
    self.assertEqual(len(evidence),2)
    self.assertTrue(all('classification' not in c for c in cases))
    self.assertTrue(all('evidence_status' not in e and
        'reviewed_at' not in e and 'review_explanation' not in e for e in evidence))
    self.assertTrue(all(e['source_kind']=='government_arcgis_organization'
        for e in evidence))
    self.assertNotIn(str(OID1['lat']),printed)
    self.assertNotIn(str(OID1['lon']),printed)
    self.assertNotIn(s.GIS,printed)
    self.assertIn('canonical_cameras_published: 0',printed)
 def test_no_source_proof_no_write(self):
    writes=[]
    def api(path,method='GET',payload=None,prefer=None):
       if method!='GET':writes.append(path)
       return good_api(path,method,payload,prefer)
    with (patch.object(s,'linked_government_org',return_value=False),
          patch.object(s,'original_camera_disclosure',return_value=True),
          patch.object(s,'inspect') as inventory):
       with self.assertRaisesRegex(s.InventoryHeld,'no longer'):
          s.run(True,api,page,lambda _: {},lambda *a,**k:ORG)
    inventory.assert_not_called()
    self.assertEqual(writes,[])
 def test_duplicate_oid_or_outside_city_is_entirely_held(self):
    for points in ([OID1,OID1],
                   [OID1,{'id':8,'lat':47.0,'lon':-117.16}]):
      with self.assertRaises(s.InventoryHeld):
        s.private_records(points,'EXAMPLE1234',D,D)
 def test_inventory_check_dry_run_never_writes(self):
    with (patch.object(s,'inspect',side_effect=proof),
          patch.object(s,'linked_government_org',return_value=True),
          patch.object(s,'original_camera_disclosure',return_value=True),
          io.StringIO() as buffer):
      with contextlib.redirect_stdout(buffer):
        self.assertEqual(s.run(False,good_api,page,lambda _: {},
                     lambda *a,**k:ORG),2)
      self.assertIn('private_candidates_staged: 0',buffer.getvalue())

if __name__=='__main__':unittest.main()
