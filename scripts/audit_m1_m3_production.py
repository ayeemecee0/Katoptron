"""Read-only M1-M3 live acceptance: evidence identities, tiers, lifecycle.

No writes, no location logging, no new source approval, no public trust changes.
A green result certifies these machine-checkable properties only, NOT national
inventory completeness, installed hardware or ALPR activity.
"""
import argparse
import datetime as dt
import hashlib
import math
import re
from collections import Counter

from auto_verify_flock_agenda import api_request
from paged_supabase import fetch_all

HEX = re.compile(r'^[0-9a-f]{64}$')
SAFE_URL = re.compile(r'^https://[A-Za-z0-9.-]+/')
ALLOWED_LIFECYCLE = {
    'resolved_existing_trusted', 'rejected_source', 'parked_specific_agency_evidence',
    'parked_same_government_jurisdiction', 'investigate_original_agency',
    'needs_review',
}
CANONICAL_LIMIT = 5000
SOURCE_RECHECK_MAX_AGE = dt.timedelta(days=365)
ATTRIBUTED_RECHECK_MAX_AGE = dt.timedelta(days=14)
CLOCK_SKEW = dt.timedelta(minutes=10)
# Owner-reviewed original GIS layer classification. New sources remain
# unconfirmed until explicitly reviewed and added; a city using Flock is not
# proof that every generic camera in its GIS inventory is Flock hardware.
FLOCK_SOURCE_KEYS = frozenset({
    'agency_alachua_fl','elpaso_co','lawrenceville_ga',
    'monroe_wa','newport_beach_ca','peoria_az','webster_tx',
})


def snapshot(api=api_request):
    canonical=fetch_all(api,
      'flock_camera_locations?select=record_key,label,jurisdiction_label,latitude,'
      'longitude,source_url,evidence_sha256,evidence_summary,verification_status,'
      'location_accuracy,verification_method,last_source_recheck_at,source_flock_label_status'
      '&verification_status=eq.verified&location_accuracy=eq.exact&limit=100',
      'record_key',max_records=CANONICAL_LIMIT)
    sources=fetch_all(api,
      'trusted_flock_gis_sources?select=source_key,gis_layer_url,jurisdiction_label,'
      'source_status&limit=100','source_key',max_records=500)
    low=fetch_all(api,
      'flock_source_attributed_map_points?select=case_key,source_key,source_url,'
      'jurisdiction_label,latitude,longitude,evidence_sha256,caveat,'
      'publication_status,source_checked_at&limit=100',
      'case_key',max_records=5000)
    policy=fetch_all(api,
      'flock_attributed_source_policies?select=source_key,gis_layer_url,'
      'jurisdiction_label,policy_status&limit=100','source_key',max_records=500)
    candidates=fetch_all(api,
      'flock_gis_source_candidates?select=gis_layer_url,trust_status&limit=100',
      'gis_layer_url',max_records=500)
    lifecycle=fetch_all(api,
      'flock_gis_candidate_lifecycle?select=gis_layer_url,disposition,'
      'next_review_after&limit=100','gis_layer_url',max_records=500)
    return canonical,sources,low,policy,candidates,lifecycle


def check(data, min_camera=1, now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    canonical,sources,low,policies,candidates,lifecycle=data
    if len(canonical)<min_camera or len(canonical)>CANONICAL_LIMIT:
        raise ValueError('Published official inventory unexpectedly small or truncated')
    indexed={}
    for row in sources:
        if row['source_status']=='verified':
            key=(row['gis_layer_url'],row['jurisdiction_label'])
            if key in indexed:
                raise ValueError('Duplicate current source authority')
            indexed[key]=row['source_key']
    if not indexed:
        raise ValueError('No current independently approved source')
    seen=set()
    counts=Counter()
    source_labels=Counter()
    for p in canonical:
        key=p.get('record_key')
        authority=(p.get('source_url'),p.get('jurisdiction_label'))
        if (not isinstance(key,str) or key in seen or authority not in indexed
            or p.get('verification_status')!='verified'
            or p.get('location_accuracy')!='exact'
            or not SAFE_URL.match(p.get('source_url') or '')
            or not isinstance(p.get('evidence_sha256'),str)
            or not HEX.fullmatch(p['evidence_sha256'])
            or p.get('verification_method')!='official_georeferenced_camera_record_v1'
            or not p.get('last_source_recheck_at')):
            raise ValueError('Government source identity or provenance incomplete')
        seen.add(key)
        if not valid_point(p):
            raise ValueError('Malformed original government point geometry')
        if not recheck_is_fresh(p.get('last_source_recheck_at'),
                                SOURCE_RECHECK_MAX_AGE,now):
            raise ValueError('Government camera source freshness expired or future-dated')
        source_key=indexed[authority]
        label=p.get('source_flock_label_status')
        if label not in ('source_flock_identified','generic_lpr','unconfirmed'):
            raise ValueError('Unreviewed Flock-only source label is not classified')
        if label=='source_flock_identified' and source_key not in FLOCK_SOURCE_KEYS:
            raise ValueError('Flock source-labeled evidence requires original reviewed source key')
        if source_key=='live_oak_tx' and label!='generic_lpr':
            raise ValueError('Generic Live Oak LPR source cannot be upgraded to Flock-labeled evidence')
        if source_key in FLOCK_SOURCE_KEYS and label!='source_flock_identified':
            raise ValueError('Existing reviewed Flock source label unexpectedly changed')
        source_labels[label]+=1
        if source_key=='live_oak_tx':
            # These city-published LPR locations have generic equipment labels;
            # do not misrepresent them as per-device Flock hardware certification.
            summary=p.get('evidence_summary') or ''
            if 'NOT per-device manufacturer' not in summary:
                raise ValueError('Live Oak individual manufacturer certainty overstated')
        counts[indexed[authority]]+=1

    active_policies={
      p['source_key']:p for p in policies if p.get('policy_status')=='approved'
    }
    prior=set()
    verified_by_jur={}
    for p in canonical:
        verified_by_jur.setdefault(p['jurisdiction_label'],[]).append(p)
    for p in low:
        if p.get('publication_status')!='active':
            continue
        key=p.get('case_key')
        policy=active_policies.get(p.get('source_key'))
        if (not isinstance(key,str) or key in prior
            or policy is None or p.get('source_url')!=policy.get('gis_layer_url')
            or p.get('jurisdiction_label')!=policy.get('jurisdiction_label')
            or not isinstance(p.get('evidence_sha256'),str)
            or not HEX.fullmatch(p['evidence_sha256'])
            or not recheck_is_fresh(p.get('source_checked_at'),
                                    ATTRIBUTED_RECHECK_MAX_AGE,now)
            or 'NOT' not in (p.get('caveat') or '')):
            raise ValueError('Unconfirmed source-publication proof missing')
        if not valid_point(p):
            raise ValueError('Unconfirmed source geometry invalid')
        prior.add(key)
        if any(abs(p['latitude']-v['latitude'])<0.0003
               and abs(p['longitude']-v['longitude'])<0.0003
               for v in verified_by_jur.get(p['jurisdiction_label'],[])):
            raise ValueError('Unconfirmed map overlaps an official published point')

    queue={r.get('gis_layer_url'):r for r in lifecycle}
    if len(queue)!=len(lifecycle):
        raise ValueError('Duplicate source lifecycle identity')
    for row in candidates:
        key=row.get('gis_layer_url')
        if key not in queue:
            raise ValueError('Unclassified private GIS source awaiting disposition')
        state=queue[key].get('disposition')
        if state not in ALLOWED_LIFECYCLE:
            raise ValueError('Private source lifecycle disposition unknown')
        if state not in ('resolved_existing_trusted','rejected_source','needs_review'):
            if not queue[key].get('next_review_after'):
                raise ValueError('Parked or actionable research candidate has no revisit date')
    return {'source_labeled_flock_points':source_labels['source_flock_identified'],
            'generic_lpr_source_points':source_labels['generic_lpr'],
            'unconfirmed_source_points':source_labels['unconfirmed'],
            'verified_source_points':len(canonical),
            'trusted_source_count':len(indexed),
            'unconfirmed_source_points':len(prior),
            'private_lifecycle_count':len(lifecycle),
            'research_remaining':sum(x.get('disposition') in ('investigate_original_agency','needs_review')
                                     for x in lifecycle),
            'live_oak_source_positions':counts['live_oak_tx']}


def recheck_is_fresh(value,maximum_age,now):
    if not isinstance(value,str):
        return False
    try:
        checked=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:
        return False
    if checked.tzinfo is None or now.tzinfo is None:
        return False
    age=now-checked
    return -CLOCK_SKEW <= age <= maximum_age


def valid_point(p):
    lat,lon=p.get('latitude'),p.get('longitude')
    return (type(lat) in (float,int) and type(lon) in (float,int)
            and math.isfinite(lat) and math.isfinite(lon)
            and 17<=lat<=72 and -180<=lon<=-64)


def run(minimum):
    result=check(snapshot(),minimum)
    for k in sorted(result):
        print('M1-M3 PRODUCTION GATE',k,result[k])
    print('M1-M3 PRODUCTION GATE published records added 0')
    print('M1-M3 PRODUCTION GATE hardware/uptime/national completeness not certified')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--min-official-points',type=int,default=316)
    args=parser.parse_args()
    run(args.min_official_points)
