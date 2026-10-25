"""Offline regression fixtures for complete Peoria ArcGIS inventory verification."""
import unittest
from urllib.parse import parse_qs, urlsplit

from probe_peoria_gis import inventory, LAYER, SERVICE


class TestPeoriaInventory(unittest.TestCase):
    def fixture(self, mode='valid'):
        calls = {'ids': 0}

        def fetch(url):
            if url == LAYER + '?f=json':
                return {'name': 'Flock Cameras', 'geometryType': 'esriGeometryPoint',
                        'type': 'Feature Layer', 'objectIdField': 'OBJECTID',
                        'fields': [{'name': name, 'type': 'esriFieldTypeOID' if name == 'OBJECTID' else 'esriFieldTypeString'} for name in ('OBJECTID', 'CameraID', 'Location')]}
            if url == SERVICE + '?f=json':
                return {'layers': [{'id': 286, 'name': 'Flock Cameras'}]}
            q = parse_qs(urlsplit(url).query)
            if q.get('returnIdsOnly') == ['true']:
                calls['ids'] += 1
                return {'objectIds': [1, 2] if mode != 'drift' or calls['ids'] == 1 else [1, 3],
                        'objectIdFieldName': 'OBJECTID'}
            ids = [int(v) for v in q.get('objectIds', [''])[0].split(',')]
            features = [{'attributes': {'OBJECTID': i, 'CameraID': 'CAM-' + str(i),
                                        'Location': 'Peoria'},
                         'geometry': {'x': -112.25 + i * .001, 'y': 33.5}}
                        for i in ids]
            if mode == 'truncated':
                features.pop()
            if mode == 'duplicate_id':
                features[-1]['attributes']['CameraID'] = 'CAM-1'
            if mode == 'out_of_bounds':
                features[-1]['geometry']['x'] = 0
            return {'features': features}
        return fetch

    def test_complete_inventory(self):
        self.assertEqual(inventory(self.fixture())['point_count'], 2)

    def test_truncation_is_held(self):
        with self.assertRaisesRegex(ValueError, 'truncated'):
            inventory(self.fixture('truncated'))

    def test_inventory_change_is_held(self):
        with self.assertRaisesRegex(ValueError, 'changed'):
            inventory(self.fixture('drift'))

    def test_duplicate_camera_id_is_held(self):
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            inventory(self.fixture('duplicate_id'))

    def test_out_of_bounds_is_held(self):
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            inventory(self.fixture('out_of_bounds'))


if __name__ == '__main__':
    unittest.main()
