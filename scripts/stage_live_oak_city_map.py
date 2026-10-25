"""Privately stage city-linked Live Oak camera-map points as unreviewed leads.

The government's Flock page links a city-branded Web Map, but ArcGIS layer
metadata labels each device only LPR Camera and independent manufacturer/
publisher approval is not complete. Never approve or publish these points.
"""
import argparse
import hashlib
import json
from auto_verify_flock_agenda import api_request
from paged_supabase import fetch_all
from probe_peoria_overlap import summarize
from probe_live_oak_tx_public_map import audit, CITY, APP
from stage_reviewed_publisher_camera_candidates import hold_conflicting_staged_evidence

FAMILY='live_oak.city_map_lpr'
JURISDICTION='Live Oak, TX'

def make_receipts(proof):
    pts=proof['original_points']
    if not isinstance(pts,list) or not 1<=len(pts)<=100:
        raise ValueError('Original map inventory incomplete')
    cases=[];attestations=[];ids=set()
    for point in pts:
        oid,lat,lon=point['id'],point['lat'],point['lon']
        if type(oid) is not int or oid<=0 or oid in ids:
            raise ValueError('Original city camera layer has duplicated point identities')
        ids.add(oid)
        token=hashlib.sha256((proof['layer_url']+':'+str(oid)).encode()).hexdigest()[:30]
        case_key='tier_'+token; proof_key='proof_'+token
        receipt=hashlib.sha256(json.dumps({
            'gis':proof['layer_url'],'oid':oid,'lat':lat,'lon':lon,
            'gov_sha256':proof['government_page_sha256']
        },sort_keys=True,separators=(',',':')).encode()).hexdigest()
        cases.append({
            'case_key':case_key,'label':'Original government-linked city LPR map; manufacturer unverified',
            'jurisdiction_label':JURISDICTION,
            'latitude':lat,'longitude':lon,
            'source_url':APP,
            'evidence_summary':'City police Flock Safety webpage directly links city-branded Live Oak Camera Map. Underlying layer has source-documented LPR Camera points. ArcGIS publisher ownership and Flock device identity not independently proven; UNREVIEWED and not active-camera status.'
        })
        attestations.append({
            'evidence_key':proof_key,'case_key':case_key,'source_kind':'third_party_gis',
            'source_family':FAMILY,'source_url':proof['layer_url'],
            'authority_url':CITY,'latitude':lat,'longitude':lon,
            'evidence_sha256':receipt,
            'source_excerpt':'City police Flock page directly links original city camera map; underlying georeferenced point layer names generic LPR Camera devices. Does not establish per-point Flock manufacturer, operation or camera ownership.'
        })
    return cases,attestations

def stage(stage_private=False,api=api_request,audited=audit):
    proof=audited(private_points=True)
    pts=proof['original_points']
    canonical=fetch_all(api,
        'flock_camera_locations?select=record_key,latitude,longitude'
        '&verification_status=eq.verified&location_accuracy=eq.exact&limit=100',
        'record_key',max_records=5000)
    if len(canonical)<293:
        raise ValueError('Full existing verified camera inventory unavailable')
    overlap=summarize([(p['lat'],p['lon']) for p in pts],canonical)
    if overlap['possible_existing_nearby']:
        raise ValueError('Nearby existing verified cameras require manual disambiguation')
    cases,evidence=make_receipts(proof)
    if stage_private:
        hold_conflicting_staged_evidence(cases,evidence,api)
        for table,rows,key in (
            ('flock_point_evidence_cases',cases,'case_key'),
            ('flock_point_evidence_attestations',evidence,'evidence_key')):
            response=api(table+'?on_conflict='+key,method='POST',payload=rows,
                prefer='resolution=ignore-duplicates,return=minimal')
            if response is not None:raise ValueError('Unexpected private evidence insertion receipt')
    print('LIVE OAK public mapped LPR points inspected',len(pts))
    print('LIVE OAK verified nearby camera overlap candidates',overlap['possible_existing_nearby'])
    print('LIVE OAK private unreviewed cases staged',len(cases) if stage_private else 0)
    print('LIVE OAK official GIS cameras published',0)
    return len(cases)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--stage-private',action='store_true')
    opts=p.parse_args()
    try:stage(stage_private=opts.stage_private)
    except Exception as exc:raise SystemExit('Live Oak source held: '+type(exc).__name__) from None
