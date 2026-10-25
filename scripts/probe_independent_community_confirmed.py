"""Read-only national independent community-confirmed camera feed qualification.

Never confuses community sighting with original government verification.
Records may be ALPR of other brands; only the explicit Flock Safety subset is
eligible for Katoptron. Never print camera coordinates, private submitter
notes, names, or street addresses. Public CC BY 4.0 export endpoint only.
"""
import csv
import io
import re
import urllib.request
from collections import Counter

URL='https://flocklocations.com/api/cameras/export?format=csv&confirmed=true'
MAX_BYTES=6_000_000
REQUIRED={'id','lat','lng','camera_type','confirmation_status','confirm_count'}
MAX_ROWS=8000

def read_export(open_url=urllib.request.urlopen):
    req=urllib.request.Request(URL,headers={
      'User-Agent':'KatoptronPublicOpenDataResearch/1.0',
      'Accept':'text/csv'})
    with open_url(req,timeout=25) as response:
        raw=response.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('Community export size over limit')
    data=raw.decode('utf-8-sig',errors='strict')
    source=csv.DictReader(io.StringIO(data))
    if not source.fieldnames or not REQUIRED.issubset(set(source.fieldnames)):
        raise ValueError('Independent community feed schema unexpectedly changed')
    counts=Counter();seen=set()
    for row in source:
        counts['all_confirmed_feed_records']+=1
        if counts['all_confirmed_feed_records']>MAX_ROWS:
            raise ValueError('Unbounded independent source record count')
        identifier=str(row.get('id') or '')
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,90}',identifier) or identifier in seen:
            raise ValueError('Source record IDs malformed or duplicated')
        seen.add(identifier)
        import math
        try:
            latitude=float(row['lat']);longitude=float(row['lng'])
            confirmed=int(row['confirm_count'])
        except (TypeError,ValueError) as exc:
            raise ValueError('Public community source location/confirmation invalid') from exc
        if not math.isfinite(latitude) or not math.isfinite(longitude) or not 17<=latitude<=72 or not -180<=longitude<=-64:
            counts['out_of_scope_or_invalid_geometry']+=1
            continue
        if confirmed<1 or str(row['confirmation_status']).strip().lower()!='community confirmed':
            counts['unsupported_community_confirmation']+=1
            continue
        if str(row.get('camera_type') or '').strip().lower() not in ('flock safety','flock'):
            counts['non_flock_or_undetermined_vendor']+=1
            continue
        counts['explicit_flock_community_confirmed']+=1
    if counts['all_confirmed_feed_records']==0:
        raise ValueError('Community source empty; do not claim no cameras')
    return counts

if __name__=='__main__':
    try:
        stats=read_export()
        for key,value in sorted(stats.items()):print('INDEPENDENT NATIONAL COMMUNITY FEED',key,value)
        print('Government verified camera locations published by feed: 0')
    except Exception as e:
        raise SystemExit('Independent national community source held: '+type(e).__name__) from None
