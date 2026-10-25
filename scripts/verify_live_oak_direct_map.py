"""Narrow source verification for the exact Live Oak police-published Flock map.

The city's original Flock Safety program page links the exact public ArcGIS
application. This is a direct agency endorsement of the MAP, not an endorsement
of an arbitrary GIS publisher or all neighboring ArcGIS layers. The agency GIS
has a generic per-feature 'LPR Camera' type, not proof of current uptime.
"""
import datetime as dt
import hashlib
import json
from collections import Counter
from probe_live_oak_tx_public_map import audit, CITY

KEY='live_oak_tx'
LAYER='https://services9.arcgis.com/xdpiCgT89eSIEpbi/arcgis/rest/services/LiveOakCameras/FeatureServer/0'
BOUND=(29.3,-98.6,29.8,-98.1)

def authorize(s,p):
    if (s.get('source_key')!=KEY or s.get('source_status')!='verified'
        or s.get('gis_layer_url')!=LAYER or s.get('government_evidence_url')!=CITY
        or s.get('jurisdiction_label')!='Live Oak, TX'
        or s.get('expected_id_field')!='OBJECTID'
        or tuple(s.get(k) for k in ('bounds_south','bounds_west','bounds_north','bounds_east'))!=BOUND
        or p.get('source_key')!=KEY or p.get('profile_status')!='verified'
        or p.get('identity_mode')!='municipal_public_flock_map'
        or p.get('service_evidence_mode')!='city_police_direct_map'
        or p.get('expected_layer_name')!='Cameras'
        or p.get('vendor_field')!='Device_Type'
        or p.get('camera_id_field')!='OBJECTID'):
        raise ValueError('Live Oak municipality source does not match reviewed exact map authority')
    return True

def qualify(s,p,auditor=audit):
    authorize(s,p)
    proof=auditor(private_points=True)
    if (not isinstance(proof,dict) or proof.get('layer_url')!=LAYER or
        not isinstance(proof.get('government_page_sha256'),str)
        or len(proof['government_page_sha256'])!=64
        or not isinstance(proof.get('original_points'),list)
        or len(proof['original_points'])!=proof.get('source_count')
        or not 1<=len(proof['original_points'])<=150
        or proof.get('manufacturer_labeled_flock') not in range(0,len(proof['original_points'])+1)):
        raise ValueError('Government-linked Live Oak map inventory incomplete')
    rows=[];seen=set()
    for point in proof['original_points']:
        oid,lat,lon=point.get('id'),point.get('lat'),point.get('lon')
        if (type(oid) is not int or oid<=0 or oid in seen or
            type(lat) not in (int,float) or type(lon) not in (int,float) or
            not BOUND[0]<=lat<=BOUND[2] or not BOUND[1]<=lon<=BOUND[3]):
            raise ValueError('Original municipal camera feature has invalid ID or geometry')
        seen.add(oid)
        digest=hashlib.sha256(json.dumps({
           'layer':LAYER,'oid':oid,'latitude':lat,'longitude':lon,
           'camera_type':'City police Flock programme original publicly linked LPR map'
        },sort_keys=True,separators=(',',':')).encode()).hexdigest()
        rows.append({
           'record_key':f'gis-{KEY}-{oid}-{digest[:12]}',
           'label':f'Live Oak, TX · police-published ALPR map #{oid}',
           'jurisdiction_label':'Live Oak, TX',
           'latitude':lat,'longitude':lon,'location_accuracy':'exact',
           'uncertainty_radius_m':0,'source_type':'official_government',
           'source_url':LAYER,
           'evidence_summary':(
               'Original City of Live Oak Police Flock Safety webpage explicitly links '
               'the Live Oak Camera Map. An independently fetched ArcGIS Web Map '
               'identifies this exact Cameras point layer; original feature OIDs and '
               'complete LPR Camera geometry were checked twice. City source '
               'documents map position, NOT per-device manufacturer, operation, '
               'plate reads or installation date.'
           ),
           'evidence_sha256':digest,
           'verification_method':'official_georeferenced_camera_record_v1',
           'last_confirmed_on':dt.date.today().isoformat()
        })
    if len(rows)!=len(proof['original_points']):
        raise ValueError('Live Oak full original camera inventory was not reconciled')
    return rows,Counter(),len(rows)
