"""Import independently sourced community-tagged Flock ALPR points from OSM.

The original-government 293-point canonical table is NEVER modified.
Everything here is labeled 'community_osm' under ODbL, not verified by Flock.
Free-tier bounded batches; no mass vendor API requests. Reruns are idempotent.
"""
import argparse
import datetime as dt
import gzip
import hashlib
from collections import Counter
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode

# Fail closed before removing a material fraction of a previously published source.
MAX_SOURCE_SHRINK_FRACTION=0.03
MAX_SOURCE_ID_CHURN_FRACTION=0.05

SOURCE='https://data.dontgetflocked.com/cameras.geojson.gz'
MAX_SOURCE_BYTES=50_000_000
MAX_DECODED_BYTES=140_000_000
MAX_BATCH=400
MIN_FLOCK=90_000
MAX_FLOCK=200_000
MAX_DB_SIZE_MB=350


def is_flock(value):
    if not isinstance(value,str):return False
    tag=value.strip().lower()
    return tag.startswith(('flock','floc')) and len(tag)<=90


def normalize(feature,source_day):
    if not isinstance(feature,dict):return None
    p=feature.get('properties')
    g=feature.get('geometry')
    if not isinstance(p,dict) or not is_flock(p.get('brand')):return None
    if not isinstance(g,dict) or g.get('type')!='Point':return None
    coords=g.get('coordinates')
    if not isinstance(coords,list) or len(coords)<2:return None
    lon,lat=coords[:2]
    if (type(lon) not in (int,float) or type(lat) not in (int,float)
        or not (math.isfinite(lon) and math.isfinite(lat))
        or not (17<=lat<=72 and -180<=lon<=-64)):
        return None
    osm_type=p.get('osmType')
    osm_id=p.get('osmId')
    if osm_type not in ('node','way') or type(osm_id) is not int or osm_id<=0:
        return None
    timestamp=p.get('osmTimestamp')
    if not isinstance(timestamp,str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT[0-9:.+-]{8,20}Z?',timestamp):
        timestamp=None
    return dict(osm_key=f'{osm_type}/{osm_id}',latitude=round(lat,7),
                longitude=round(lon,7),source_timestamp=timestamp,
                source_snapshot_date=source_day)


def download_source():
    req=urllib.request.Request(SOURCE,headers={
        'User-Agent':'Katoptron-OSM-open-data-ingest/1.0',
        'Accept':'application/geo+json,application/json'})
    with urllib.request.urlopen(req,timeout=90) as response:
        if response.status!=200 or response.geturl()!=SOURCE:
            raise ValueError('Open data source changed or redirected')
        data=response.read(MAX_SOURCE_BYTES+1)
    if not 100_000<len(data)<=MAX_SOURCE_BYTES:
        raise ValueError('Open data download empty or unbounded')
    if data[:2]==b'\x1f\x8b':
        data=gzip.decompress(data)
    if len(data)>MAX_DECODED_BYTES:
        raise ValueError('Decoded nationwide open data unexpectedly large')
    fc=json.loads(data)
    if not isinstance(fc,dict) or fc.get('type')!='FeatureCollection':
        raise ValueError('OpenStreetMap source is not a FeatureCollection')
    features=fc.get('features')
    if not isinstance(features,list) or not 100_000<len(features)<400_000:
        raise ValueError('Incomplete nationwide open ALPR inventory')
    return features


def prepare_rows(features,day):
    rows={}
    count=0
    for feature in features:
        if not isinstance(feature,dict):continue
        props=feature.get('properties')
        if isinstance(props,dict) and is_flock(props.get('brand')):count+=1
        record=normalize(feature,day)
        if record:
            old=rows.get(record['osm_key'])
            if old and (old['latitude']!=record['latitude'] or
                        old['longitude']!=record['longitude']):
                raise ValueError('Conflicting duplicate source identity')
            rows[record['osm_key']]=record
    if not MIN_FLOCK<=count<=MAX_FLOCK:
        raise ValueError('Flock-branded nationwide source count outside bounds')
    if len(rows)<int(count*0.98):
        raise ValueError('Too many Flock-labeled observations lack safe geometry or OSM ID')
    return [rows[k] for k in sorted(rows)]


def post_batch(batch):
    base=os.environ['SUPABASE_URL'].rstrip('/')
    if base!='https://bpvkapswslmgfazbzpsv.supabase.co':
        raise ValueError('Supabase project differs from pinned Katoptron production')
    key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
    body=json.dumps(batch,separators=(',',':')).encode()
    req=urllib.request.Request(
        base+'/rest/v1/flock_osm_community_points?on_conflict=osm_key',
        data=body,method='POST',headers={
            'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json',
            'Prefer':'resolution=merge-duplicates,return=minimal'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=40) as response:
                if response.status not in (200,201,204):
                    raise ValueError('Unexpected import HTTP response')
                if response.read(1024):
                    raise ValueError('Unexpected private import response content')
                return
        except urllib.error.HTTPError as err:
            if err.code not in (408,429,500,502,503,504) or attempt==2:
                raise ValueError('Source-labeled community import rejected HTTP '+str(err.code)) from None
            time.sleep(2**attempt)


def read_count(query=None):
    """Exact PostgREST count from RLS-publicly readable OSM community table."""
    base=os.environ['SUPABASE_URL'].rstrip('/')
    if base!='https://bpvkapswslmgfazbzpsv.supabase.co':
        raise ValueError('Unexpected data destination')
    key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
    endpoint='flock_osm_community_points?select=osm_key&limit=1'
    if query:
        endpoint+='&'+urlencode(query)
    req=urllib.request.Request(
        base+'/rest/v1/'+endpoint,
        headers={'apikey':key,'Authorization':'Bearer '+key,
                 'Prefer':'count=exact','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=45) as response:
        if response.status not in (200,206):
            raise ValueError('Community row-count request failed')
        content_range=response.headers.get('Content-Range','')
        if len(response.read(4000))>4000:
            raise ValueError('Count query returned excessive data')
    match=re.fullmatch(r'(?:[0-9]+-[0-9]+|[*])/([0-9]+)',content_range)
    if not match:
        raise ValueError('Community exact count missing: refusing reconciliation')
    return int(match.group(1))


def reconcile(previous_count,expected_count,stamp):
    """Only retire OSM IDs absent from a verified COMPLETE source snapshot.

    No deletion can happen if upload stopped early, an exact current-run
    source count differs, or a large number of original records disappeared.
    """
    if (not isinstance(previous_count,int) or previous_count<0
        or expected_count<MIN_FLOCK
        or (previous_count and expected_count <
            previous_count*(1-MAX_SOURCE_SHRINK_FRACTION))):
        raise ValueError('Unexpected source shrink; community removal held')
    complete=read_count([('last_seen_sync_at','eq.'+stamp)])
    if complete!=expected_count:
        raise ValueError('Full-source import count mismatch; stale rows retained')
    stale=read_count([('last_seen_sync_at','neq.'+stamp)])
    if previous_count and stale>previous_count*MAX_SOURCE_ID_CHURN_FRACTION:
        raise ValueError('Excessive OSM identity churn; stale rows retained')
    base=os.environ['SUPABASE_URL'].rstrip('/')
    key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
    query=urlencode([('last_seen_sync_at','neq.'+stamp)])
    req=urllib.request.Request(
        base+'/rest/v1/flock_osm_community_points?'+query,
        method='DELETE',
        headers={'apikey':key,'Authorization':'Bearer '+key,
                 'Prefer':'return=minimal'})
    with urllib.request.urlopen(req,timeout=90) as response:
        if response.status not in (200,204):
            raise ValueError('Unexpected community retirement response')
        if response.read(1024):
            raise ValueError('Unexpected community retirement body')
    if read_count()!=expected_count:
        raise ValueError('Community sync post-check failed; manual investigation required')
    print('COMMUNITY FLOCK RECONCILE previous_count',previous_count)
    print('COMMUNITY FLOCK RECONCILE current_count',expected_count)
    print('COMMUNITY FLOCK RECONCILE retired_absent_records',stale)
    print('COMMUNITY FLOCK RECONCILE verified government rows changed: 0')


def build_quality_snapshot(rows,stamp,day):
    """Compute source-edit freshness and co-location, never physical uptime."""
    if not rows or not MIN_FLOCK<=len(rows)<=MAX_FLOCK:
        raise ValueError('Incomplete source cannot become quality snapshot')
    observed=dt.datetime.fromisoformat(stamp)
    if observed.tzinfo is None:
        raise ValueError('Quality snapshot timestamp must have timezone')
    cutoff=observed-dt.timedelta(days=365)
    coords=Counter((r['latitude'],r['longitude']) for r in rows)
    missing=0
    old=0
    for r in rows:
        raw=r.get('source_timestamp')
        if not raw:
            missing+=1
            continue
        try:
            changed=dt.datetime.fromisoformat(raw.replace('Z','+00:00'))
            if changed.tzinfo is None:
                missing+=1
                continue
            if changed>observed+dt.timedelta(days=1):
                raise ValueError('Future OSM edit timestamp not credible')
            if changed<cutoff:
                old+=1
        except (TypeError,ValueError) as exc:
            if 'Future OSM edit' in str(exc):
                raise
            missing+=1
    unique=len(coords)
    data={
        'sync_at':stamp,'source_snapshot_date':day,
        'osm_observations':len(rows),
        'distinct_coordinates':unique,
        'colocated_extra_observations':len(rows)-unique,
        'colocated_coordinate_groups':sum(1 for n in coords.values() if n>1),
        'osm_edits_older_365d':old,
        'osm_edit_timestamp_missing':missing
    }
    receipt=json.dumps(data,sort_keys=True,separators=(',',':'))
    data['measurement_receipt_sha256']=hashlib.sha256(receipt.encode()).hexdigest()
    return data


def publish_quality_snapshot(item):
    """Append dated aggregates ONLY after successful full-source reconciliation."""
    base=os.environ['SUPABASE_URL'].rstrip('/')
    if base!='https://bpvkapswslmgfazbzpsv.supabase.co':
        raise ValueError('Unexpected quality destination')
    key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
    req=urllib.request.Request(
        base+'/rest/v1/flock_osm_quality_snapshots?on_conflict=sync_at',
        method='POST',data=json.dumps([item],separators=(',',':')).encode(),
        headers={
            'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json',
            'Prefer':'resolution=ignore-duplicates,return=minimal'
        })
    with urllib.request.urlopen(req,timeout=40) as response:
        if response.status not in (200,201,204) or response.read(1024):
            raise ValueError('Cannot confirm dated community quality snapshot')
    print('COMMUNITY FLOCK QUALITY observations',item['osm_observations'])
    print('COMMUNITY FLOCK QUALITY distinct mapped coordinates',item['distinct_coordinates'])
    print('COMMUNITY FLOCK QUALITY co-located extras',item['colocated_extra_observations'])
    print('COMMUNITY FLOCK QUALITY OSM edits older than one year',item['osm_edits_older_365d'])


def refresh_public_osm_render_cache():
    """Only a fully reconciled, authenticated OSM import can update public canvas bytes.

    The public viewer RPC reads this existing materialization, not 116k source
    rows for every visitor. Failed refreshes leave the previously good cache.
    """
    base=os.environ['SUPABASE_URL'].rstrip('/')
    if base!='https://bpvkapswslmgfazbzpsv.supabase.co':
        raise ValueError('Unexpected national OSM cache publisher')
    key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
    req=urllib.request.Request(
        base+'/rest/v1/rpc/katoptron_refresh_osm_exact_snapshot_cache',
        data=b'{}',method='POST',
        headers={'apikey':key,'Authorization':'Bearer '+key,
                 'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=90) as response:
        if response.status!=200:
            raise ValueError('Public original-coordinate cache refresh rejected')
        raw=response.read(64)
    count=json.loads(raw)
    if type(count) is not int or not MIN_FLOCK<=count<=MAX_FLOCK:
        raise ValueError('Public OSM cache lacks a fully reconciled coordinate count')
    print('COMMUNITY FLOCK ORIGINAL CANVAS refreshed_exact_observations',count)


def import_rows(rows,max_points,api=post_batch,run_stamp=None):
    if max_points<=0 or max_points>200_000:raise ValueError('Invalid bounded import batch size')
    if run_stamp is None:
        run_stamp=dt.datetime.now(dt.timezone.utc).isoformat(timespec='microseconds')
    if not isinstance(run_stamp,str) or not run_stamp.endswith('+00:00'):
        raise ValueError('Only UTC source sync markers are accepted')
    subset=[dict(row,last_seen_sync_at=run_stamp) for row in rows[:max_points]]
    for offset in range(0,len(subset),MAX_BATCH):
        api(subset[offset:offset+MAX_BATCH])
        if (offset//MAX_BATCH)%25==0:
            print('COMMUNITY FLOCK IMPORT safe_source_batches_completed',
                  offset//MAX_BATCH+1)
    print('COMMUNITY FLOCK IMPORT fetched_Flock_records',len(rows))
    print('COMMUNITY FLOCK IMPORT source_labeled_records_submitted',len(subset))
    print('COMMUNITY FLOCK IMPORT canonical_government_camera_changes',0)
    return len(subset)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--max-points',type=int,default=1000)
    p.add_argument('--dry-run',action='store_true')
    args=p.parse_args()
    features=download_source()
    day=dt.datetime.now(dt.timezone.utc).date().isoformat()
    rows=prepare_rows(features,day)
    print('COMMUNITY FLOCK IMPORT source_features',len(features))
    print('COMMUNITY FLOCK IMPORT valid_explicitly_Flock_records',len(rows))
    if args.dry_run:
        print('COMMUNITY FLOCK IMPORT dry_run_no_writes')
        return
    if not 0<args.max_points<=MAX_FLOCK:
        raise SystemExit('Requested import ceiling is invalid')
    # In a partial manual run, do not retire anything. Only a validated
    # complete source run can reconcile removals, moves and brand changes.
    whole=(args.max_points>=len(rows))
    prior=read_count() if whole else None
    if (whole and prior and
        len(rows)<prior*(1-MAX_SOURCE_SHRINK_FRACTION)):
        raise ValueError('Suspiciously large Flock source contraction')
    stamp=dt.datetime.now(dt.timezone.utc).isoformat(timespec='microseconds')
    import_rows(rows,min(args.max_points,len(rows)),run_stamp=stamp)
    if whole:
        reconcile(prior,len(rows),stamp)
        publish_quality_snapshot(build_quality_snapshot(rows,stamp,day))
        refresh_public_osm_render_cache()
    else:
        print('COMMUNITY FLOCK RECONCILE skipped: deliberately partial import')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Source contents, OSM identities and API credentials never appear in logs.
        raise SystemExit('Community import held: '+type(exc).__name__+' ('+str(exc)[:90]+')') from None
