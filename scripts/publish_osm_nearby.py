"""Publish a full, bounded OSM nearby-candidate audit only after exact row verification.

The ODbL community inventory and original-government camera tables are
never modified. Public candidate visibility is atomic at the snapshot level:
rows stage unpublished until exact count validation and a final publish marker.
"""
import datetime as dt
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request

MAX_BATCH=350
SOURCE_BASE='https://bpvkapswslmgfazbzpsv.supabase.co'
EXPECTED_MIN_PAIRS=1000
EXPECTED_MAX_PAIRS=30000


def snapshot_id_for(day,pairs):
    if not isinstance(day,str) or len(day)!=10:
        raise ValueError('Source date missing')
    h=hashlib.sha256(b'Katoptron OSM nearby 15m v1\n')
    h.update(day.encode('ascii')+b'\n')
    for a,b,distance in pairs:
        h.update(f'{a}\t{b}\t{distance:.2f}\n'.encode('ascii'))
    return h.hexdigest()


def snapshot_meta(day,source_count,pairs):
    from osm_nearby_candidates import summarize
    summary=summarize(pairs)
    if not 90000<=source_count<=200000:
        raise ValueError('National source inventory incomplete')
    if not EXPECTED_MIN_PAIRS<=len(pairs)<=EXPECTED_MAX_PAIRS:
        raise ValueError('Nearby pair count changed outside conservative bounds')
    if len(set((a,b) for a,b,_ in pairs))!=len(pairs):
        raise ValueError('Conflicting duplicate OSM pair identities')
    if summary['source_records_in_nearby_pairs']>source_count:
        raise ValueError('Nearby source identity count impossible')
    if any(not (0<distance<=15) or not a<b for a,b,distance in pairs):
        raise ValueError('Invalid OSM proximity identity or distance')
    return dict(
        snapshot_id=snapshot_id_for(day,pairs),
        source_snapshot_date=day,
        source_observations=source_count,
        pair_count=len(pairs),
        source_records_in_pairs=summary['source_records_in_nearby_pairs'],
        pairs_within_5m=summary['pairs_within_5m'],
        pairs_5_to_15m=summary['pairs_5_to_15m'],
    )


def endpoint_key():
    base=os.environ.get('SUPABASE_URL','').rstrip('/')
    key=os.environ.get('SUPABASE_SERVICE_ROLE_KEY','')
    if base!=SOURCE_BASE or len(key)<20:
        raise ValueError('No verified Katoptron production destination and private worker credential')
    return key


def call(table,verb,query=None,body=None,prefer=None):
    key=endpoint_key()
    url=SOURCE_BASE+'/rest/v1/'+table
    if query:url+='?'+urllib.parse.urlencode(query,doseq=True)
    headers={'apikey':key,'Authorization':'Bearer '+key,
       'Accept':'application/json'}
    if prefer:headers['Prefer']=prefer
    if body is not None:
        headers['Content-Type']='application/json'
        body=json.dumps(body,separators=(',',':')).encode()
    req=urllib.request.Request(url,data=body,method=verb,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=55) as r:
            if r.status not in (200,201,204,206):
                raise ValueError('Unexpected database response status')
            payload=r.read(250000)
            return r.headers, json.loads(payload) if payload else None
    except urllib.error.HTTPError as e:
        raise ValueError('Private OSM proximity stage failed HTTP '+str(e.code)) from None


def read_exact_count(snapshot):
    headers,_=call('flock_osm_nearby_candidates','GET',
       [('select','osm_key_a'),('limit','1'),('snapshot_id','eq.'+snapshot)],
       prefer='count=exact')
    import re
    matched=re.fullmatch(r'(?:[0-9]+-[0-9]+|[*])/([0-9]+)',
       headers.get('Content-Range',''))
    if not matched:
        raise ValueError('Missing exact count; cannot publish partial candidate audit')
    return int(matched.group(1))


def publish(day,source_count,pairs,rest=call):
    metadata=snapshot_meta(day,source_count,pairs)
    snap=metadata['snapshot_id']
    # This call is deliberately separate from any camera inventory writes.
    _,previous=rest('flock_osm_nearby_snapshots','GET',
      [('select','snapshot_id,pair_count,published_at'),('snapshot_id','eq.'+snap)])
    if not isinstance(previous,list):
        raise ValueError('Existing OSM candidate audit state unavailable')
    if previous:
        if len(previous)!=1 or previous[0]['pair_count']!=len(pairs):
            raise ValueError('Candidate source digest conflicts with existing audit metadata')
        if previous[0]['published_at']:
            if read_exact_count(snap)!=len(pairs):
                raise ValueError('Published audit is incomplete; refusing to claim success')
            print('OSM NEARBY STAGED already_published_verified',len(pairs))
            return metadata
    else:
        rest('flock_osm_nearby_snapshots','POST',
          [('on_conflict','snapshot_id')],[metadata],
          'resolution=ignore-duplicates,return=minimal')
    for offset in range(0,len(pairs),MAX_BATCH):
        batch=[dict(snapshot_id=snap,osm_key_a=a,osm_key_b=b,distance_m=d)
          for a,b,d in pairs[offset:offset+MAX_BATCH]]
        rest('flock_osm_nearby_candidates','POST',
          [('on_conflict','snapshot_id,osm_key_a,osm_key_b')],batch,
          'resolution=ignore-duplicates,return=minimal')
    actual=read_exact_count(snap)
    if actual!=len(pairs):
        raise ValueError('Only '+str(actual)+' of '+str(len(pairs))+
          ' candidate rows staged; publication held')
    at=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    _,result=rest('flock_osm_nearby_snapshots','PATCH',
      [('snapshot_id','eq.'+snap),('published_at','is.null')],
      {'published_at':at},'return=representation')
    if not isinstance(result,list) or len(result)!=1 or result[0].get('snapshot_id')!=snap:
        raise ValueError('Cannot verify public snapshot publication')
    print('OSM NEARBY PUBLISHED records',actual)
    print('OSM NEARBY PUBLISHED source_rows',source_count)
    print('OSM NEARBY PUBLISHED snapshot',snap)
    print('OSM NEARBY PUBLISHED government_or_OSM_camera_inventory_changes',0)
    return metadata
