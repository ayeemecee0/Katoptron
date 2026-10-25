"""Safely stage 12 city-linked Shelbyville GIS locations in private evidence ONLY.

Independent original city map -> exact ArcGIS publisher organization; exact
Flock point layer/ID inventory; no nearby published point. Never authorizes
trusted GIS sources, reviews, or public camera records. Rechecks old immutable
receipts before idempotent insertion; HTML drift holds until reviewed.
"""
import argparse
import hashlib
import json

from auto_verify_flock_agenda import api_request
from paged_supabase import fetch_all
from probe_peoria_overlap import summarize
from probe_shelbyville_overlap import audited_private_points, GIS, CITY
from stage_reviewed_publisher_camera_candidates import hold_conflicting_staged_evidence

JURISDICTION = 'Shelbyville, TN'
FAMILY = 'shelbyville.municipal.arcgis'
MAX_CANONICAL = 5000


def make_receipts(proof):
    ids = set()
    cases, attestations = [], []
    points = proof['private_original_points']
    if not 1 <= len(points) <= 100:
        raise ValueError('Unbounded Shelbyville original inventory')
    for item in points:
        oid, lat, lon = item['id'], item['lat'], item['lon']
        if type(oid) is not int or oid <= 0 or oid in ids:
            raise ValueError('Original source contains duplicate point identity')
        ids.add(oid)
        digest = hashlib.sha256((GIS + ':' + str(oid)).encode()).hexdigest()[:32]
        case_key = 'tier_' + digest
        evidence_key = 'proof_' + digest
        fingerprint = hashlib.sha256(json.dumps(
            {'url': GIS, 'oid': oid, 'latitude': lat, 'longitude': lon,
             'city_page_sha256': proof['gov_page_sha256'],
             'arcgis_org_id': proof['arcgis_org_id']},
            sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        cases.append({
            'case_key': case_key,
            'label': 'City-affiliated published Flock GIS point; unreviewed',
            'jurisdiction_label': JURISDICTION,
            'latitude': lat, 'longitude': lon,
            'source_url': GIS,
            'evidence_summary': (
                'Original Shelbyville city page independently links a map owned '
                'by the same ArcGIS publisher as a public Flock Cameras layer. '
                'Complete original point inventory independently rechecked. '
                'Police deployment and active status are NOT independently proven.'
            ),
        })
        attestations.append({
            'evidence_key': evidence_key, 'case_key': case_key,
            'source_kind': 'government_arcgis_organization',
            'source_family': FAMILY,
            'source_url': GIS, 'authority_url': CITY,
            'latitude': lat, 'longitude': lon,
            'evidence_sha256': fingerprint,
            'source_excerpt': (
                'Original city-linked ArcGIS map organization and exact public '
                'Flock camera point-layer owner match; city endorsement of each '
                'installed device not independently confirmed.'
            ),
        })
    return cases, attestations


def run(stage_private=False, api=api_request, audited=audited_private_points):
    proof = audited(include_evidence=True)
    points = proof['private_original_points']
    canonical = fetch_all(api,
        'flock_camera_locations?select=record_key,latitude,longitude'
        '&verification_status=eq.verified&location_accuracy=eq.exact&limit=100',
        'record_key', max_records=MAX_CANONICAL)
    if len(canonical) < 293:
        raise ValueError('Canonical inventory incomplete')
    overlap = summarize([(x['lat'], x['lon']) for x in points], canonical)
    if overlap['possible_existing_nearby']:
        raise ValueError('Possible existing published camera; hold entire private stage')
    cases, evidence = make_receipts(proof)
    if len(cases) != len(points):
        raise ValueError('Original GIS inventory differs from private evidence cases')
    if stage_private:
        hold_conflicting_staged_evidence(cases, evidence, api)
        for table, rows, key in (
            ('flock_point_evidence_cases', cases, 'case_key'),
            ('flock_point_evidence_attestations', evidence, 'evidence_key')):
            result = api(table + '?on_conflict=' + key,
                         method='POST', payload=rows,
                         prefer='resolution=ignore-duplicates,return=minimal')
            if result is not None:
                raise ValueError('Unexpected private evidence staging response')
    print('SHELBYVILLE original city-linked point inventory:', len(points))
    print('SHELBYVILLE independent publisher association: checked')
    print('SHELBYVILLE possible published camera proximity conflicts: 0')
    print('SHELBYVILLE private candidate cases staged:', len(cases) if stage_private else 0)
    print('SHELBYVILLE public verified camera records written: 0')
    return len(cases)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage-private', action='store_true')
    args = p.parse_args()
    try:
        run(stage_private=args.stage_private)
    except Exception as e:
        # Do not emit unpublished source coordinates or service error bodies.
        raise SystemExit('Shelbyville source evidence held: ' + type(e).__name__) from None
