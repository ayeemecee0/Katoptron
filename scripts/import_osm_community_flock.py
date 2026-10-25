"""Import independently sourced community-tagged Flock ALPR points from OSM.

The original-government 293-point canonical table is NEVER modified.
Everything here is labeled 'community_osm' under ODbL, not verified by Flock.
Free-tier bounded batches; no mass vendor API requests. Reruns are idempotent.
"""
import argparse
import datetime as dt
import gzip
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode

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
            'Prefer':'resolution=ignore-duplicates,return=minimal'})
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


def import_rows(rows,max_points,api=post_batch):
    if max_points<=0 or max_points>200_000:raise ValueError('Invalid bounded import batch size')
    subset=rows[:max_points]
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
    import_rows(rows,min(args.max_points,len(rows)))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Source contents, OSM identities and API credentials never appear in logs.
        raise SystemExit('Community import held: '+type(exc).__name__+' ('+str(exc)[:90]+')') from None
