"""Offline source-identity and privacy assertions for Shelbyville audit."""
import unittest
from unittest.mock import patch
from probe_shelbyville_overlap import audited_private_points

class Tests(unittest.TestCase):
    def test_checked_source_returns_aggregate_ready_coordinates_in_memory(self):
        with patch('probe_shelbyville_overlap.linked_government_org', return_value=True):
            p=audited_private_points(
                page_fetch=lambda _: (object(), 'a'*64),
                publisher=lambda url,return_identity: {'org_id':'CITYORG123'},
                arcgis_fetch=lambda url: {'name':'Flock Cameras','objectIdField':'OBJECTID'},
                inventory=lambda *args,**kw: {'features':2, 'stable_original_ids':True,
                    'bounded_point_geometry':True,
                    '_private_points':[{'id':1,'lat':35.5,'lon':-86.5},
                                       {'id':2,'lat':35.51,'lon':-86.51}]})
            self.assertEqual(len(p),2)

    def test_unauthorized_org_must_fail(self):
        with patch('probe_shelbyville_overlap.linked_government_org', return_value=False):
            with self.assertRaisesRegex(ValueError,'not independently proven'):
                audited_private_points(
                    page_fetch=lambda _: (object(),'b'*64),
                    publisher=lambda url,return_identity:{'org_id':'UNRELATED'})
    def test_shifted_inventory_must_fail(self):
        with patch('probe_shelbyville_overlap.linked_government_org', return_value=True):
            with self.assertRaisesRegex(ValueError,'outside reviewed city envelope'):
                audited_private_points(
                    page_fetch=lambda _: (object(),'c'*64),
                    publisher=lambda url,return_identity:{'org_id':'CITYORG123'},
                    arcgis_fetch=lambda _: {'name':'Flock Cameras','objectIdField':'OBJECTID'},
                    inventory=lambda *args,**kwargs:{'features':1,'stable_original_ids':True,
                        'bounded_point_geometry':True,
                        '_private_points':[{'id':1,'lat':50.0,'lon':-86.5}]})

if __name__=='__main__':
    unittest.main()
