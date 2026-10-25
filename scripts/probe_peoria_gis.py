"""Read-only exact-inventory audit of Peoria AZ's original-government Flock layer.

Checks complete ArcGIS ObjectID snapshots before and after fetching every
feature in bounded chunks. Does not publish, stage, or log coordinates.
"""
import json
import math
import urllib.parse
import urllib.request

SERVICE = 'https://gis.peoriaaz.gov/arcgis/rest/services/PM/pmPublicWorks/MapServer'
LAYER = SERVICE + '/286'
MAX_POINTS = 500
CHUNK = 50


def read(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Katoptron/1.0 public GIS verification',
        'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=24) as response:
        if response.geturl() != url:
            raise ValueError('Redirected government GIS service')
        body = response.read(2_000_001)
    if len(body) > 2_000_000:
        raise ValueError('Too-large government GIS response')
    obj = json.loads(body)
    if not isinstance(obj, dict) or obj.get('error'):
        raise ValueError('Government GIS returned an error')
    return obj


def query(fetch, parameters):
    return fetch(LAYER + '/query?' + urllib.parse.urlencode(parameters))


def inventory(fetch=read):
    meta = fetch(LAYER + '?f=json')
    service = fetch(SERVICE + '?f=json')
    fields = meta.get('fields', [])
    names = {field.get('name') for field in fields if isinstance(field, dict)}
    oid_field = meta.get('objectIdField')
    if (meta.get('name') != 'Flock Cameras'
            or meta.get('geometryType') != 'esriGeometryPoint'
            or meta.get('type') != 'Feature Layer'
            or oid_field != 'OBJECTID'
            or not {'OBJECTID', 'CameraID', 'Location'}.issubset(names)):
        raise ValueError('Not an identifiable government Flock camera point layer')
    if not any(isinstance(x, dict) and x.get('id') == 286
               and x.get('name') == 'Flock Cameras'
               for x in service.get('layers', [])):
        raise ValueError('City GIS service does not list exact Flock layer')

    def original_ids():
        snapshot = query(fetch, {'where': '1=1', 'returnIdsOnly': 'true',
                                 'f': 'json'})
        ids = snapshot.get('objectIds')
        if (snapshot.get('objectIdFieldName') not in (None, oid_field)
                or not isinstance(ids, list)
                or not 1 <= len(ids) <= MAX_POINTS
                or any(type(x) is not int or x < 0 for x in ids)
                or len(set(ids)) != len(ids)):
            raise ValueError('Original camera ObjectID inventory invalid or oversized')
        return sorted(ids)

    ids = original_ids()
    seen = set()
    camera_ids = set()
    points = set()
    for start in range(0, len(ids), CHUNK):
        expected = set(ids[start:start + CHUNK])
        result = query(fetch, {
            'objectIds': ','.join(map(str, sorted(expected))),
            'outFields': 'OBJECTID,CameraID,Location',
            'returnGeometry': 'true', 'outSR': '4326', 'f': 'json'})
        features = result.get('features')
        if (not isinstance(features, list)
                or result.get('exceededTransferLimit')
                or len(features) != len(expected)):
            raise ValueError('Government camera feature batch missing or truncated')
        actual = set()
        for feature in features:
            attr = feature.get('attributes', {})
            geometry = feature.get('geometry', {})
            oid = attr.get('OBJECTID')
            camera_id = attr.get('CameraID')
            lon, lat = geometry.get('x'), geometry.get('y')
            if (type(oid) is not int or oid not in expected or oid in actual
                    or not isinstance(camera_id, str)
                    or not camera_id.strip()
                    or len(camera_id) > 150
                    or camera_id.strip() in camera_ids
                    or type(lon) not in (int, float)
                    or type(lat) not in (int, float)
                    or not math.isfinite(lon) or not math.isfinite(lat)
                    or not -113 <= lon <= -111.4
                    or not 33.2 <= lat <= 34.5):
                raise ValueError('Ambiguous original camera ID or geometry')
            actual.add(oid)
            camera_ids.add(camera_id.strip())
            point = (round(lat, 7), round(lon, 7))
            if point in points:
                raise ValueError('Two cameras share identical source coordinates')
            points.add(point)
        if actual != expected or seen.intersection(actual):
            raise ValueError('Camera ObjectID batch identity mismatch')
        seen.update(actual)
    if ids != original_ids() or seen != set(ids):
        raise ValueError('Original camera inventory changed during verification')
    return {'point_count': len(ids), 'stable_ids': True,
            'complete_original_inventory': True,
            'operational_status': 'not_established'}


def main():
    result = inventory()
    print('Original city-government GIS Flock layer:',
          'PM/pmPublicWorks/MapServer/286')
    print('Exact complete original point count:', result['point_count'])
    print('Stable unique ObjectIDs and CameraIDs:', result['stable_ids'])
    print('Source inventory complete:', result['complete_original_inventory'])
    print('Installed or active status: not independently established')
    print('New public camera locations published: 0')


if __name__ == '__main__':
    main()
