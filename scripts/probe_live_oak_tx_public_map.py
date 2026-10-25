"""Read-only original city published map provenance audit (Live Oak TX).

Follow exactly the application's ArcGIS item metadata and its Web Map.
Never infer an individual camera point from a rendered map; never print source
coordinates, feature identities or unpublished GIS layer URLs.
"""
import re
from urllib.parse import urljoin,urlsplit,urlencode
from auto_verify_camera_gis import get_official_json
from discover_government_gis_links import fetch_government_page,normalized_url

CITY='https://www.liveoaktx.net/departments/police/flock-safety'
APP='https://liveoaktx.maps.arcgis.com/apps/instant/basic/index.html?appid=1fe4ad954b3346b9a7e2a3a337c5cfbf'
APPID='1fe4ad954b3346b9a7e2a3a337c5cfbf'
ID=re.compile(r'^[0-9a-fA-F]{32}$')
ITEM='https://www.arcgis.com/sharing/rest/content/items/'
WEBMAP_FIELDS={'webmap','webmapid','mapid','mapitemid'}

def map_identifiers(app_data):
    found=set()
    def walk(value,depth=0):
        if depth>6:return
        if isinstance(value,dict):
            if len(value)>500:raise ValueError('Unbounded original ArcGIS application config')
            for key,sub in value.items():
                if not isinstance(key,str):continue
                if key.lower() in WEBMAP_FIELDS and isinstance(sub,str) and ID.fullmatch(sub):
                    found.add(sub.lower())
                elif isinstance(sub,(dict,list)):
                    walk(sub,depth+1)
        elif isinstance(value,list):
            if len(value)>150:raise ValueError('Unbounded original application config list')
            for v in value:walk(v,depth+1)
    walk(app_data)
    return sorted(found)

def verified_item_org(item,fetch):
    org=item.get('orgId') if isinstance(item,dict) else None
    if isinstance(org,str) and re.fullmatch(r'[A-Za-z0-9]{8,48}',org):
        return org
    owner=item.get('owner') if isinstance(item,dict) else None
    if not isinstance(owner,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{3,90}',owner):
        raise ValueError('ArcGIS item missing independently provable owner')
    profile=fetch('https://www.arcgis.com/sharing/rest/community/users/'+owner+'?f=json')
    if (not isinstance(profile,dict) or profile.get('username')!=owner or
            not isinstance(profile.get('orgId'),str) or
            not re.fullmatch(r'[A-Za-z0-9]{8,48}',profile['orgId'])):
        raise ValueError('Original Esri account organization identity not proven')
    return profile['orgId']


def inspect_mapped_point_inventory(layer, fetch):
    url = layer.get('url') if isinstance(layer, dict) else None
    if not isinstance(url, str):
        raise ValueError('Original app map lacks an exact source URL')
    p = urlsplit(url)
    valid_host = bool(p.hostname and (
        re.fullmatch(r'services[0-9]*[.]arcgis[.]com', p.hostname)
        or p.hostname.endswith('.liveoaktx.net')))
    parts = p.path.rstrip('/').split('/')
    valid_path = len(parts) >= 2 and parts[-2] in ('FeatureServer','MapServer') and parts[-1].isdigit()
    if p.scheme != 'https' or p.username or p.password or p.port or p.query or p.fragment or not valid_host or not valid_path:
        raise ValueError('Original app layer has unapproved source locator')
    metadata = fetch(url+'?f=json')
    if isinstance(metadata,dict):
        print('LIVE OAK layer geometry class',repr(metadata.get('geometryType')),
              'name category',repr(str(metadata.get('name',''))[:50]))
    if (not isinstance(metadata, dict) or metadata.get('type') != 'Feature Layer'
        or metadata.get('geometryType') != 'esriGeometryPoint'
        or not re.search('flock|license.?plate|live oak cameras', str(metadata.get('name','')), re.I)):
        raise ValueError('Original map layer not a named Flock point source')
    fields=metadata.get('fields')
    if isinstance(fields,list):
        print('LIVE OAK published_camera_layer_schema',
              [str(x.get('name',''))[:50] for x in fields[:25] if isinstance(x,dict)])
    answer = fetch(url+'/query?'+urlencode({'f':'json','where':'1=1','returnIdsOnly':'true'}))
    values = answer.get('objectIds') if isinstance(answer,dict) else None
    if not isinstance(values,list) or not 1 <= len(values) <= 500 or len(set(values)) != len(values) or any(type(x) is not int or x <= 0 for x in values):
        raise ValueError('Original camera layer feature ID list incomplete')
    return len(values)

def audit(fetch=get_official_json,page_fetch=fetch_government_page):
    doc,page_digest=page_fetch(CITY)
    anchors={normalized_url(urljoin(CITY,href)) for href,label in doc.anchors
             if isinstance(href,str) and len(href)<1500}
    if APP not in anchors or not isinstance(page_digest,str) or len(page_digest)!=64:
        raise ValueError('Current original police source no longer links its published map')
    application=fetch(ITEM+APPID+'?f=json')
    if (not isinstance(application,dict) or application.get('id')!=APPID
            or application.get('type') not in ('Web Mapping Application','Web Experience')):
        raise ValueError('Original city-linked ArcGIS application identity changed')
    try:app_org=verified_item_org(application,fetch)
    except ValueError:app_org=None  # Attribution hold, not evidence authorization.
    config=fetch(ITEM+APPID+'/data?f=json')
    maps=map_identifiers(config)
    if len(maps)!=1:raise ValueError('City camera app does not identify exactly one Web Map')
    mapid=maps[0]
    item=fetch(ITEM+mapid+'?f=json')
    if (not isinstance(item,dict) or item.get('type')!='Web Map'
        or item.get('id','').lower()!=mapid):
        raise ValueError('App Web Map identity changed')
    try:map_org=verified_item_org(item,fetch)
    except ValueError:map_org=None
    if app_org is not None and map_org is not None and map_org!=app_org:
        raise ValueError('App Web Map publisher differs from original city app')
    data=fetch(ITEM+mapid+'/data?f=json')
    layers=data.get('operationalLayers') if isinstance(data,dict) else None
    if not isinstance(layers,list) or not 1<=len(layers)<=100:
        raise ValueError('Original Web Map operational layer catalogue unavailable')
    for index,layer in enumerate(layers):
        if isinstance(layer,dict):
            print('LIVE OAK source layer title',index,
                  repr(str(layer.get('title') or '')[:55]),
                  'kind',repr(str(layer.get('layerType') or '')[:40]))
    matched=[x for x in layers if isinstance(x,dict) and
          re.search(r'flock|license.?plate|live oak cameras',str(x.get('title',''))+' '+str(x.get('id','')),re.I)]
    for layer in matched:
        try:
            n=inspect_mapped_point_inventory(layer,fetch)
            print('LIVE OAK original_source_camera_ids_count',n)
        except ValueError as exc:
            reasons={'Original app map lacks an exact source URL','Original app layer has unapproved source locator','Original map layer not a named Flock point source','Original camera layer feature ID list incomplete'}
            print('LIVE OAK original_source_layer_held',str(exc) if str(exc) in reasons else type(exc).__name__)
    print('LIVE OAK original_city_page_link',True)
    print('LIVE OAK application_and_webmap_same_organization',
          app_org is not None and app_org==map_org)
    print('LIVE OAK webmap_operational_layer_count',len(layers))
    print('LIVE OAK explicitly_named_Flock_or_ALPR_layers',len(matched))
    print('LIVE OAK original map source status', 'further_original_layer_verification_required')
    print('LIVE OAK newly published verified camera points',0)
    return len(matched)

if __name__=='__main__':
    try:audit()
    except Exception as exc:
        print('LIVE OAK original map inspection held',type(exc).__name__)
        raise
