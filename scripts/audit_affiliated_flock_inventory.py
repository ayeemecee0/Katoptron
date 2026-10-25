"""Read-only full original ArcGIS Flock point inventory audit for a researched publisher.

Must be called ONLY after independent original-government-to-ArcGIS publisher
attribution. Geometry is validated privately, never logged or returned.
This does not authorize a government camera or publish a coordinate.
"""
import math
import re
import urllib.parse

LAYER_URL=re.compile(
    r'^https://services[0-9]*\.arcgis\.com/[A-Za-z0-9]+/'
    r'arcgis/rest/services/[A-Za-z0-9_-]+/FeatureServer/[0-9]+$')
MAX_FEATURES=500
PAGE_SIZE=50
FLOCK_NAME=re.compile(r'^flock[_ -]*cameras?(?: - [A-Za-z ]{1,50})?$',re.I)

class InventoryHeld(ValueError):
    pass

def inspect(layer_url,expected_name,expected_oid,fetch,private_points=False):
    """Return safe counts/boolean evidence ONLY, never data or coordinates."""
    if not isinstance(layer_url,str) or not LAYER_URL.fullmatch(layer_url):
        raise InventoryHeld("layer URL not allowlisted public ArcGIS FeatureServer")
    if not isinstance(expected_name,str) or not FLOCK_NAME.fullmatch(expected_name):
        raise InventoryHeld("unreviewed Flock layer name")
    if not isinstance(expected_oid,str) or not re.fullmatch(r'[A-Za-z0-9_]{2,90}',expected_oid):
        raise InventoryHeld("invalid original ObjectID field")

    service_url=layer_url.rsplit('/',1)[0]
    svc=fetch(service_url+'?f=json')
    lyr=fetch(layer_url+'?f=json')
    lid=int(layer_url.rsplit('/',1)[1])
    if (not isinstance(svc,dict) or svc.get('error') or
        not isinstance(lyr,dict) or lyr.get('error') or
        not isinstance(svc.get('layers'),list) or
        not any(isinstance(x,dict) and x.get('id')==lid and
                x.get('name')==expected_name for x in svc['layers']) or
        lyr.get('name')!=expected_name or
        lyr.get('type')!='Feature Layer' or
        lyr.get('geometryType')!='esriGeometryPoint'):
        raise InventoryHeld("Flock original point-layer metadata or parent changed")
    fieldset=lyr.get('fields')
    if (not isinstance(fieldset,list) or
        not any(isinstance(f,dict) and f.get('name')==expected_oid
                and f.get('type')=='esriFieldTypeOID' for f in fieldset)):
        raise InventoryHeld("original typed ObjectID absent")
    id_field=lyr.get('objectIdField')
    if not isinstance(id_field,str) or id_field!=expected_oid:
        raise InventoryHeld("declared ObjectID identity mismatch")
    # Optional independent per-camera identity is a *lead*, not proof.
    has_camera_id=any(isinstance(f,dict) and
        f.get('type')=='esriFieldTypeString' and
        f.get('name') in ('CameraID','Camera_ID','Flock_ID','ID','NAME')
        for f in fieldset)

    def object_ids():
        response=fetch(layer_url+'/query?'+urllib.parse.urlencode({
            'f':'json','where':'1=1','returnIdsOnly':'true'}))
        if not isinstance(response,dict) or response.get('error'):
            raise InventoryHeld("original ObjectID inventory unavailable")
        ids=response.get('objectIds')
        field=response.get('objectIdFieldName')
        if (not isinstance(field,str) or field.lower()!=expected_oid.lower()
            or not isinstance(ids,list) or not 1<=len(ids)<=MAX_FEATURES
            or any(type(i) is not int or i<=0 for i in ids)
            or len(set(ids))!=len(ids)):
            raise InventoryHeld("empty, duplicate, truncated or malformed original inventory")
        return sorted(ids)

    start=object_ids()
    seen=[]
    verified_private=[]
    for offset in range(0,len(start),PAGE_SIZE):
        requested=start[offset:offset+PAGE_SIZE]
        response=fetch(layer_url+'/query?'+urllib.parse.urlencode({
            'f':'json','objectIds':','.join(map(str,requested)),
            'outFields':expected_oid,'returnGeometry':'true','outSR':'4326'}))
        if (not isinstance(response,dict) or response.get('error') or
            response.get('exceededTransferLimit') or
            not isinstance(response.get('features'),list) or
            len(response['features'])!=len(requested)):
            raise InventoryHeld("original geometry page missing or incomplete")
        for feature in response['features']:
            a=feature.get('attributes') if isinstance(feature,dict) else None
            g=feature.get('geometry') if isinstance(feature,dict) else None
            if not isinstance(a,dict) or not isinstance(g,dict):
                raise InventoryHeld("original feature missing metadata or point")
            values=[v for k,v in a.items() if isinstance(k,str) and
                    k.lower()==expected_oid.lower()]
            if len(values)!=1 or type(values[0]) is not int:
                raise InventoryHeld("original individual ObjectID missing")
            lat,lon=g.get('y'),g.get('x')
            if (type(lat) not in (int,float) or
                type(lon) not in (int,float) or
                not math.isfinite(lat) or not math.isfinite(lon) or
                not (17<=lat<=72 and -180<=lon<=-64)):
                raise InventoryHeld("feature lacks valid US point geometry")
            seen.append(values[0])
            if private_points:
                verified_private.append({'id':values[0], 'lat':round(lat,7), 'lon':round(lon,7)})
        if sorted(seen[-len(requested):])!=requested:
            raise InventoryHeld("original layer omitted or duplicated requested features")
    if len(seen)!=len(start) or sorted(seen)!=start or object_ids()!=start:
        raise InventoryHeld("original camera inventory changed during audit")
    # Never return private coordinates, individual IDs, or source URLs.
    result={'features':len(start),'stable_original_ids':True,
            'bounded_point_geometry':True,'has_individual_camera_id_field':has_camera_id}
    if private_points:
        # Only return to a specifically approved PRIVATE staging worker.
        # Never stringify this member in GitHub Actions or browser output.
        result['_private_points']=sorted(verified_private,key=lambda r:r['id'])
    return result
