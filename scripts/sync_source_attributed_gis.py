"""Publish only original city-associated GIS observations in a LOW-CONFIDENCE tier.

This does not verify any individual Flock device, installation or uptime.
It never changes canonical government-camera rows, private reviews or their
trust status. The original city-page -> independently identified Esri org,
full twice-checked point inventory, immutable private attestation, canonical
deduplication and private write guards must all pass on EVERY refresh.
"""
import argparse
from auto_verify_flock_agenda import api_request
from paged_supabase import fetch_all
from probe_shelbyville_overlap import audited_private_points
from stage_shelbyville_gis_candidates import make_receipts
from stage_reviewed_publisher_camera_candidates import hold_conflicting_staged_evidence
from probe_peoria_overlap import summarize

from audit_affiliated_flock_inventory import InventoryHeld

SOURCE_KEY='shelbyville_arcgis_affiliation'
MAX_CANONICAL=5000
DISCLAIMER=(
 'Source-attributed municipal ArcGIS publisher Flock-labeled MAP OBSERVATION. '
 'The original city linked an ArcGIS map owned by the layer publisher, but '
 'police approval of this exact layer, individual installed device, current '
 'camera operation and manufacturer identity are NOT established. '
 'This lower-confidence layer is separate from government-verified cameras '
 'and is excluded from verified-route detections.'
)

def retain_immutable_provenance_if_page_changed(cases, evidence, previous, api):
    """Only refresh EXISTING low-confidence pins after a fresh semantic proof.

    Called solely after the live original-city ArcGIS organization check,
    twice-snapshotted exact inventory, coordinate reconciliation, and
    hold_conflicting_staged_evidence's case-identity check all passed.
    If the full city HTML checksum changed, preserve the old immutable
    attestation SHA, never overwrite/review/upgrade the evidence, and
    never add a newly inferred point using this exception.
    """
    if not isinstance(previous, list) or len(previous) != len(cases):
        raise ValueError('Changed government page cannot approve new map locations')
    old_by_case = {p['case_key']: p for p in previous}
    if len(old_by_case) != len(cases) or any(
        p.get('publication_status') != 'active' for p in previous
    ):
        raise ValueError('Previously withdrawn or duplicated source point')
    evidence_keys = ','.join(row['evidence_key'] for row in evidence)
    old = api(
        'flock_point_evidence_attestations?select=evidence_key,case_key,'
        'source_kind,source_family,source_url,authority_url,latitude,longitude,'
        'evidence_sha256,evidence_status&evidence_key=in.(' + evidence_keys + ')'
    )
    if not isinstance(old, list) or len(old) != len(evidence):
        raise ValueError('Unchanged original source receipts not all present')
    by_key = {p['evidence_key']: p for p in old}
    if len(by_key) != len(evidence):
        raise ValueError('Duplicate immutable original receipt')
    retained = {}
    for c, current in zip(cases, evidence):
        existing = by_key.get(current['evidence_key'])
        published = old_by_case.get(c['case_key'])
        if existing is None or published is None:
            raise ValueError('Original receipt or prior public record absent')
        for field in ('evidence_key', 'case_key', 'source_kind', 'source_family',
                      'source_url', 'authority_url', 'latitude', 'longitude'):
            if existing.get(field) != current.get(field):
                raise ValueError('Original source identity or point geometry changed')
        if existing.get('evidence_status') not in ('staged', 'reviewed'):
            raise ValueError('Original private source receipt revoked')
        sha = existing.get('evidence_sha256')
        if (not isinstance(sha, str) or len(sha) != 64
            or published.get('evidence_sha256') != sha
            or published.get('latitude') != c['latitude']
            or published.get('longitude') != c['longitude']):
            raise ValueError('Published point no longer matches original evidence')
        retained[c['case_key']] = sha
    return retained


def run(publish=False,api=api_request,auditor=audited_private_points):
    proof=auditor(include_evidence=True)
    pts=proof.get('private_original_points')
    cases,evidence=make_receipts(proof)
    if (not isinstance(pts,list) or len(pts)!=12
        or len(cases)!=len(evidence) or len(cases)!=len(pts)):
        raise ValueError('Source-attributed point inventory no longer matches documented 12')
    canonical=fetch_all(api,
        'flock_camera_locations?select=record_key,jurisdiction_label,latitude,longitude'
        '&verification_status=eq.verified&location_accuracy=eq.exact&limit=100',
        'record_key',max_records=MAX_CANONICAL)
    if len(canonical)<316:
        raise ValueError('Public baseline unexpectedly incomplete')
    nearby=summarize([(x['lat'],x['lon']) for x in pts],
        [p for p in canonical if p['jurisdiction_label']=='Shelbyville, TN'])
    if nearby['possible_existing_nearby']!=0:
        raise ValueError('Published government camera overlap; lower tier held')
    previous=api('flock_source_attributed_map_points?select=case_key,latitude,longitude,'
          'evidence_sha256,publication_status&source_key=eq.'+SOURCE_KEY+'&limit=100')
    if not isinstance(previous,list) or len(previous)>len(cases):
        raise ValueError('Prior public source tier incomplete')
    retained={}
    try:
        hold_conflicting_staged_evidence(cases,evidence,api)
    except InventoryHeld as exc:
        if str(exc)!='Private source proof changed; independent review required':
            raise
        # City page bytes may change while its live exact ArcGIS link,
        # original publisher, geometry and old attestation remain the same.
        # Only previously published, unchanged, unrevoked lower-tier cases
        # can be rechecked; no new row or evidence tier can be promoted.
        retained=retain_immutable_provenance_if_page_changed(
            cases,evidence,previous,api)
    current={r['case_key']:(r,e) for r,e in zip(cases,evidence)}
    for row in previous:
        expected=current.get(row['case_key'])
        if expected is None:
            raise ValueError('Prior source point missing in latest government-associated inventory')
        c,e=expected
        if (row['latitude']!=c['latitude'] or row['longitude']!=c['longitude']
                or row['evidence_sha256']!=retained.get(row['case_key'],e['evidence_sha256'])):
            raise ValueError('Original source fingerprint drift; public refresh held')
    rows=[{
        'case_key':c['case_key'],'source_key':SOURCE_KEY,
        'label':'City-associated GIS Flock map observation (not device verified)',
        'jurisdiction_label':c['jurisdiction_label'],
        'latitude':c['latitude'],'longitude':c['longitude'],
        'source_url':c['source_url'],'evidence_sha256':retained.get(c['case_key'],e['evidence_sha256']),
        'source_checked_at':None, 'publication_status':'active',
        'caveat':DISCLAIMER
    } for c,e in zip(cases,evidence)]
    # Use server-owned verified time, not a local untrusted clock.
    if publish:
        from datetime import datetime,timezone
        checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
        for r in rows:r['source_checked_at']=checked
        response=api('flock_source_attributed_map_points?on_conflict=case_key',
           method='POST',payload=rows,
           prefer='resolution=merge-duplicates,return=minimal')
        if response is not None:raise ValueError('Unexpected attributed map publication response')
    print('ATTRIBUTED GIS complete original source positions',len(rows))
    print('ATTRIBUTED GIS original publisher proof rechecked',True)
    print('ATTRIBUTED GIS immutable original receipt preserved after harmless HTML drift',bool(retained))
    print('ATTRIBUTED GIS public lower-confidence points refreshed',len(rows) if publish else 0)
    print('ATTRIBUTED GIS government verified cameras newly published',0)
    return len(rows)

# Public diagnostic allowlist: messages below originate only from our own
# InventoryHeld checks, never from API bodies, HTTP exceptions or map points.
# A new failure reason remains opaque until its wording is manually reviewed.
SAFE_INVENTORY_REASONS = {
    'layer URL not allowlisted public ArcGIS FeatureServer': 'invalid_source_url',
    'unreviewed Flock layer name': 'layer_name_not_allowlisted',
    'invalid original ObjectID field': 'invalid_id_field',
    'Flock original point-layer metadata or parent changed': 'source_layer_metadata_changed',
    'original typed ObjectID absent': 'typed_object_id_missing',
    'declared ObjectID identity mismatch': 'declared_object_id_changed',
    'original ObjectID inventory unavailable': 'source_inventory_unavailable',
    'empty, duplicate, truncated or malformed original inventory': 'source_inventory_invalid',
    'original geometry page missing or incomplete': 'source_geometry_unavailable',
    'original feature missing metadata or point': 'source_feature_malformed',
    'original individual ObjectID missing': 'source_object_id_missing',
    'feature lacks valid US point geometry': 'source_geometry_invalid',
    'original layer omitted or duplicated requested features': 'source_page_inconsistent',
    'original camera inventory changed during audit': 'source_inventory_drift',
    'Cannot reconcile existing private source receipts': 'private_receipts_unavailable',
    'Unexpected private source receipt inventory': 'private_receipts_invalid',
    'Private source case changed; independent review required': 'private_case_drift',
    'Private source proof changed; independent review required': 'private_provenance_drift',
}

def safe_held_reason(error):
    """Classify a known internal inventory exception without logging raw data."""
    from audit_affiliated_flock_inventory import InventoryHeld
    if isinstance(error, InventoryHeld):
        code = SAFE_INVENTORY_REASONS.get(str(error))
        if code:
            return 'InventoryHeld:'+code
    return type(error).__name__

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--publish-source-attributed',action='store_true')
    opts=p.parse_args()
    try:run(opts.publish_source_attributed)
    except Exception as e:
        # Only literal, reviewed audit reason codes may reach public CI logs.
        # Never stringify a network exception, unexpected error, URL or GPS value.
        raise SystemExit('Source-attributed GIS publication held: ' +
                         safe_held_reason(e)) from None
