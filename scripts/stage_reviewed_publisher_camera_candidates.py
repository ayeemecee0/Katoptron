"""Hold original-government-affiliated Flock GIS points in PRIVATE evidence queue.

Scope intentionally pinned to one independently researched municipality while
the generic source approval policy remains evidence-gated. A CITY publisher
association does NOT approve an individual camera installation. Service-role
staging never writes review flags or any public map/camera record.
"""
import argparse
import hashlib
import json
import re
from urllib.parse import quote

from auto_verify_flock_agenda import api_request
from auto_verify_camera_gis import get_official_json
from audit_external_arcgis_candidates import inspect_arcgis_publisher
from audit_affiliated_flock_inventory import inspect, InventoryHeld
from discover_government_gis_links import (
    fetch_government_page,original_camera_disclosure)
from probe_original_gov_arcgis_org_links import linked_government_org

CITY='https://www.cityofmenifee.us/maps'
POLICE='https://menifeepolice.org/automated-licesnse-plate-reader/'
GIS='https://services.arcgis.com/RjTKod25O4b8SbZx/arcgis/rest/services/PeregrineWebLayers/FeatureServer/20'
NAME='Flock Cameras'
JURISDICTION='Menifee, CA'
# Deliberately conservative research scope, NOT an official municipality
# polygon or assertion that the equipment is live.
ENVELOPE=(33.48,-117.50,33.92,-116.93)
MAX_CASES=100


def approved_research_preconditions(api=api_request,fetch_page=fetch_government_page,
                                   publisher=inspect_arcgis_publisher,
                                   arcgis=get_official_json):
    programs=api('flock_documented_programs?select=program_key,official_evidence_url,'
                 'record_status,program_status&program_key=eq.menifee_ca&limit=2')
    candidates=api('flock_gis_source_candidates?select=gis_layer_url,layer_name,'
                   'object_id_field,geometry_type,trust_status&gis_layer_url=eq.'+
                   quote(GIS,safe='')+'&limit=2')
    if (not isinstance(programs,list) or len(programs)!=1 or
        programs[0].get('official_evidence_url')!=POLICE or
        programs[0].get('record_status')!='verified' or
        programs[0].get('program_status')!='documented_at_source_date' or
        not isinstance(candidates,list) or len(candidates)!=1 or
        candidates[0].get('gis_layer_url')!=GIS or
        candidates[0].get('layer_name')!=NAME or
        candidates[0].get('object_id_field','').lower()!='objectid' or
        candidates[0].get('geometry_type')!='esriGeometryPoint' or
        candidates[0].get('trust_status')!='unverified'):
        raise InventoryHeld('Original government programme or private layer identity changed')
    original_gov,hash_page=fetch_page(CITY)
    original_police,hash_police=fetch_page(POLICE)
    if (not re.fullmatch(r'[a-f0-9]{64}',hash_page) or
        not re.fullmatch(r'[a-f0-9]{64}',hash_police) or
        not original_camera_disclosure(original_police)):
        raise InventoryHeld('Current original Menifee police Flock disclosure unavailable')
    # The original city links a map application that independently matches
    # the exact ArcGIS organization that owns the Flock FeatureServer item.
    org=publisher(GIS,return_identity=True)
    if not isinstance(org,dict) or not linked_government_org(original_gov,CITY,org,arcgis):
        raise InventoryHeld('Original city webpage no longer attributes Esri publisher')
    return candidates[0],org,hash_page,hash_police


def private_records(points,org_id,page_hash,police_hash):
    """Create cases/attestations to stage, never review or publish."""
    if (not isinstance(org_id,str) or not re.fullmatch(r'[A-Za-z0-9]{8,48}',org_id)
        or not re.fullmatch(r'[a-f0-9]{64}',page_hash)
        or not re.fullmatch(r'[a-f0-9]{64}',police_hash)
        or not isinstance(points,list) or not 1<=len(points)<=MAX_CASES):
        raise InventoryHeld('Unbounded or unauthenticated private inventory')
    south,west,north,east=ENVELOPE
    seen=set()
    cases=[]
    evidence=[]
    for record in points:
        oid,lat,lon=record.get('id'),record.get('lat'),record.get('lon')
        if (type(oid) is not int or oid<=0 or oid in seen or
            type(lat) not in (int,float) or type(lon) not in (int,float) or
            not south<=lat<=north or not west<=lon<=east):
            raise InventoryHeld('Source point lacks unique identity or city-area geometry')
        seen.add(oid)
        seed=GIS+':'+str(oid)
        digest=hashlib.sha256(seed.encode()).hexdigest()
        case='tier_'+digest[:32]
        evidence_key='proof_'+digest[:32]
        claim=(
          'Original Menifee city GIS publisher has a public layer labeled Flock Cameras,'
          ' with a current full original point-ID inventory; Menifee Police'
          ' separately documents a Flock Safety ALPR program. This remains'
          ' UNREVIEWED: it does not establish deployment, current operation'
          ' or agency endorsement of individual camera positions.'
        )
        excerpt=('Original Menifee municipal GIS application independently attributes'
                 ' the ArcGIS publisher. Separate original police Flock Safety ALPR'
                 ' program disclosure. Camera-specific source endorsement pending.')
        fingerprint=hashlib.sha256(json.dumps(
            {'url':GIS,'oid':oid,'lat':lat,'lon':lon,'org':org_id,
             'gov_page':page_hash,'police_page':police_hash},
            sort_keys=True,separators=(',',':')).encode()).hexdigest()
        cases.append({
          'case_key':case,'label':'Possible Flock camera (municipal GIS)',
          'jurisdiction_label':JURISDICTION,
          'latitude':lat,'longitude':lon,
          'evidence_summary':claim,'source_url':GIS,
        })
        evidence.append({
          'evidence_key':evidence_key,'case_key':case,
          'source_kind':'government_arcgis_organization',
          'source_family':'menifee.municipal.arcgis',
          'source_url':GIS,'authority_url':CITY,
          'latitude':lat,'longitude':lon,
          'evidence_sha256':fingerprint,'source_excerpt':excerpt,
          # No "evidence_status", "classification", review flags or timestamps.
        })
    return cases,evidence



def hold_conflicting_staged_evidence(cases,evidence,api):
    """Fail closed if an append-only staged record no longer matches the source.

    Ignore-duplicates is safe only for byte-equivalent evidence. Changed
    geometry or source receipts must not silently retain a stale private case.
    This check cannot approve or publish anything.
    """
    case_keys=','.join(row['case_key'] for row in cases)
    evidence_keys=','.join(row['evidence_key'] for row in evidence)
    existing_cases=api('flock_point_evidence_cases?select=case_key,latitude,longitude,source_url'
                       '&case_key=in.('+case_keys+')')
    existing_proofs=api('flock_point_evidence_attestations?select=evidence_key,evidence_sha256,'
                        'source_url,latitude,longitude&evidence_key=in.('+evidence_keys+')')
    if not isinstance(existing_cases,list) or not isinstance(existing_proofs,list):
        raise InventoryHeld('Cannot reconcile existing private source receipts')
    expected_cases={row['case_key']:row for row in cases}
    expected_proofs={row['evidence_key']:row for row in evidence}
    if (len(existing_cases)>len(expected_cases) or len(existing_proofs)>len(expected_proofs)):
        raise InventoryHeld('Unexpected private source receipt inventory')
    for old in existing_cases:
        new=expected_cases.get(old.get('case_key'))
        if (new is None or any(old.get(k)!=new[k] for k in
                               ('latitude','longitude','source_url'))):
            raise InventoryHeld('Private source case changed; independent review required')
    for old in existing_proofs:
        new=expected_proofs.get(old.get('evidence_key'))
        if (new is None or any(old.get(k)!=new[k] for k in
                               ('evidence_sha256','source_url','latitude','longitude'))):
            raise InventoryHeld('Private source proof changed; independent review required')


def run(stage_private=False,api=api_request,fetch_page=fetch_government_page,
        arcgis=get_official_json,publisher=inspect_arcgis_publisher):
    candidate,org,page_hash,police_hash=approved_research_preconditions(
        api,fetch_page,publisher,arcgis)
    proof=inspect(GIS,NAME,candidate['object_id_field'],arcgis,
                  private_points=True)
    points=proof.pop('_private_points')
    cases,evidence=private_records(points,org['org_id'],page_hash,police_hash)
    if len(cases)!=proof['features'] or len(evidence)!=proof['features']:
        raise InventoryHeld('Complete original inventory and private cases do not match')
    if stage_private:
        hold_conflicting_staged_evidence(cases,evidence,api)
        # Both inserts are append-only. On partial network failure, the next
        # run fills missing evidence. A crawler cannot update reviewed status.
        result=api('flock_point_evidence_cases?on_conflict=case_key',
                   method='POST',payload=cases,
                   prefer='resolution=ignore-duplicates,return=minimal')
        if result is not None:
            raise InventoryHeld('Unexpected private candidate insertion response')
        result=api('flock_point_evidence_attestations?on_conflict=evidence_key',
                   method='POST',payload=evidence,
                   prefer='resolution=ignore-duplicates,return=minimal')
        if result is not None:
            raise InventoryHeld('Unexpected private attestation insertion response')
    print('GOV-OWNED ARCGIS RESEARCH original_feature_count:',len(cases))
    print('GOV-OWNED ARCGIS RESEARCH private_candidates_staged:',len(cases) if stage_private else 0)
    print('GOV-OWNED ARCGIS RESEARCH canonical_cameras_published: 0')
    print('GOV-OWNED ARCGIS RESEARCH provisional_points_published: 0')
    print('GOV-OWNED ARCGIS RESEARCH status: requires independent owner review of exact layer')
    return len(cases)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage-private',action='store_true')
    p.add_argument('--evidence-hold-ok',action='store_true',
                   help='Report previously staged evidence drift as a guarded research hold')
    args=p.parse_args()
    try:
        run(stage_private=args.stage_private)
    except InventoryHeld as exc:
        # Only known immutable-receipt conflicts are accepted as a guarded
        # held research result. Other source, credential and inventory errors
        # remain hard failures. The workflow never approves camera positions.
        known_holds={
            'Private source proof changed; independent review required',
            'Private source case changed; independent review required',
        }
        if args.evidence_hold_ok and str(exc) in known_holds:
            print('::warning::Private original-government GIS evidence drift requires independent review')
            print('GOV-OWNED ARCGIS RESEARCH status: HELD, no private staging completed')
            print('GOV-OWNED ARCGIS RESEARCH canonical_cameras_published: 0')
        else:
            # These strings are predefined categories, not HTTP response data.
            raise SystemExit('Government publisher research held: '+str(exc)) from None
    except Exception as exc:
        # Do not leak private coordinates, API bodies or credentials.
        raise SystemExit('Government publisher research held: '+type(exc).__name__) from None
