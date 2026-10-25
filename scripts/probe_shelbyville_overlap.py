"""Read-only original-government linked Shelbyville GIS source vs canonical points.

Inspect fresh original agency ArcGIS map link, exact third-party FeatureServer
organization, stable feature inventory, and existing published points.
Only aggregate counts are printed. No staging, approval, or publication.
"""
from audit_affiliated_flock_inventory import inspect
from audit_external_arcgis_candidates import inspect_arcgis_publisher
from auto_verify_camera_gis import get_official_json
from auto_verify_flock_agenda import api_request
from discover_government_gis_links import fetch_government_page
from paged_supabase import fetch_all
from probe_original_gov_arcgis_org_links import linked_government_org
from probe_peoria_overlap import summarize

CITY = 'https://test.shelbyvilletn.org/planning-community-development/'
GIS = ('https://services3.arcgis.com/0Uo0Kvp9YTHRegvR/arcgis/rest/services/'
       'Flock_Cameras_-_Public/FeatureServer/0')
MAX_PUBLIC = 5000


def audited_private_points(page_fetch=fetch_government_page,
                           arcgis_fetch=get_official_json,
                           publisher=inspect_arcgis_publisher,
                           inventory=inspect):
    original, checksum = page_fetch(CITY)
    if not isinstance(checksum, str) or len(checksum) != 64:
        raise ValueError('Original city webpage receipt missing')
    identity = publisher(GIS, return_identity=True)
    if (not isinstance(identity, dict)
            or not linked_government_org(original, CITY, identity, arcgis_fetch)):
        raise ValueError('City government ArcGIS organization link not independently proven')
    metadata = arcgis_fetch(GIS + '?f=json')
    name, oid = metadata.get('name'), metadata.get('objectIdField')
    if name != 'Flock Cameras' or oid != 'OBJECTID':
        raise ValueError('Original Flock layer identity changed')
    proof = inventory(GIS, name, oid, arcgis_fetch, private_points=True)
    points = proof.pop('_private_points', None)
    if (not isinstance(points, list)
            or len(points) != proof.get('features')
            or not proof.get('stable_original_ids')
            or not proof.get('bounded_point_geometry')):
        raise ValueError('Original complete point inventory not proven')
    for point in points:
        if not (35.2 <= point['lat'] <= 36.0 and
                -87.2 <= point['lon'] <= -86.0):
            raise ValueError('Original camera feature outside reviewed city envelope')
    return [(p['lat'], p['lon']) for p in points]


def run(read=api_request):
    points = audited_private_points()
    canonical = fetch_all(
        read,
        'flock_camera_locations?select=record_key,latitude,longitude'
        '&verification_status=eq.verified&location_accuracy=eq.exact&limit=100',
        'record_key', max_records=MAX_PUBLIC)
    if len(canonical) < 293:
        raise ValueError('Published inventory incomplete; refuse overlap result')
    summary = summarize(points, canonical)
    print('SHELBYVILLE independent government publisher attribution: checked')
    print('SHELBYVILLE source layer exact original points:', summary['source_points'])
    print('SHELBYVILLE possible nearby published cameras:',
          summary['possible_existing_nearby'])
    print('SHELBYVILLE no existing published cameras within 100m:',
          summary['no_existing_within_100m'])
    print('SHELBYVILLE operational status: not independently established')
    print('SHELBYVILLE public camera records written: 0')
    return summary


if __name__ == '__main__':
    run()
