"""Read-only audit of Shelbyville TN's publicly advertised GIS publisher and Flock layer.

No database access, no approval or publication. Logs counts and identity only,
never camera geometry or individual points.
"""
from urllib.parse import urlsplit
from auto_verify_camera_gis import get_official_json
from audit_external_arcgis_candidates import inspect_arcgis_publisher
from audit_affiliated_flock_inventory import inspect as inspect_inventory
from discover_government_gis_links import fetch_government_page
from probe_original_gov_arcgis_org_links import linked_government_org

CITY='https://test.shelbyvilletn.org/planning-community-development/'
GIS='https://services3.arcgis.com/0Uo0Kvp9YTHRegvR/arcgis/rest/services/Flock_Cameras_-_Public/FeatureServer/0'

def run():
    page,sha=fetch_government_page(CITY)
    metadata=get_official_json(GIS+'?f=json')
    if not isinstance(metadata,dict) or metadata.get('error'):
        raise ValueError('Published Shelbyville layer metadata inaccessible')
    name=metadata.get('name')
    oid=metadata.get('objectIdField')
    print('SHELBYVILLE layer_type',metadata.get('geometryType'),'layer_name',repr(name))
    print('SHELBYVILLE oid_type',repr(oid))
    identity=inspect_arcgis_publisher(GIS,return_identity=True)
    affiliated=bool(isinstance(identity,dict) and
                    linked_government_org(page,CITY,identity))
    print('SHELBYVILLE original_public_gis_org_attributed',affiliated)
    if not affiliated:
        raise ValueError('Shelbyville original agency to ArcGIS publisher association unproven')
    try:
        proof=inspect_inventory(GIS,name,oid,get_official_json)
        print('SHELBYVILLE complete_original_camera_point_count',proof['features'])
        print('SHELBYVILLE stable_ids',proof['stable_original_ids'])
        print('SHELBYVILLE valid_geometries',proof['bounded_point_geometry'])
        print('SHELBYVILLE independent_camera_id',proof['has_individual_camera_id_field'])
    except ValueError as exc:
        print('SHELBYVILLE original inventory held',type(exc).__name__)
        raise
    print('SHELBYVILLE new camera positions published 0')

if __name__=='__main__':run()
