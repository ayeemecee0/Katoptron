"""Read-only nationwide *possible* OpenStreetMap overlap audit.

Candidate pairs are distinct OSM IDs with distinct coordinates within 15 m.
They are not verified duplicate physical cameras and NEVER trigger deletions.
All input is from the same already-published bounded ODbL-derived source.
"""
import argparse
import csv
import datetime as dt
import math
from collections import defaultdict

from import_osm_community_flock import download_source, prepare_rows

EARTH_RADIUS_M=6371000.0
MAX_PROXIMITY_M=15.0
# At the northern input boundary (72°), a 15 m longitude displacement is
# <0.000437°. Thus +/-1 of 0.0005° cells covers all possible 15 m pairs.
GRID_DEGREES=0.0005
MAX_PAIRS=250000
MAX_POINTS_PER_GRID_CELL=5000


def meters(a,b):
    lat1,lon1=a
    lat2,lon2=b
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    x=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*EARTH_RADIUS_M*math.asin(min(1,math.sqrt(x)))


def candidates(rows):
    """Exact geodesic threshold after a conservative coarse spatial hash."""
    buckets=defaultdict(list)
    pairs=[]
    ids=set()
    for row in rows:
        key=row['osm_key']
        if key in ids:raise ValueError('Duplicate OSM identity in audit source')
        ids.add(key)
        lat,lon=float(row['latitude']),float(row['longitude'])
        if not (math.isfinite(lat) and math.isfinite(lon) and
                17<=lat<=72 and -180<=lon<=-64):
            raise ValueError('Invalid public OSM camera geometry')
        y=math.floor(lat/GRID_DEGREES)
        x=math.floor(lon/GRID_DEGREES)
        for cy in (y-1,y,y+1):
            for cx in (x-1,x,x+1):
                for other_key,other_lat,other_lon in buckets.get((cy,cx),()):
                    if lat==other_lat and lon==other_lon:continue  # reported separately
                    distance=meters((lat,lon),(other_lat,other_lon))
                    if 0 < distance <= MAX_PROXIMITY_M:
                        left,right=sorted((key,other_key))
                        pairs.append((left,right,round(distance,2)))
                        if len(pairs)>MAX_PAIRS:
                            raise ValueError('Unexpectedly many OSM proximity candidates; audit held')
        bucket=buckets[(y,x)]
        if len(bucket)>=MAX_POINTS_PER_GRID_CELL:
            raise ValueError('Unexpectedly dense community observation cell; audit held')
        bucket.append((key,lat,lon))
    pairs.sort(key=lambda p:(p[2],p[0],p[1]))
    return pairs


def summarize(pairs):
    observed={k for a,b,_ in pairs for k in (a,b)}
    return dict(nearby_different_coordinate_pairs=len(pairs),
      source_records_in_nearby_pairs=len(observed),
      pairs_within_5m=sum(1 for _,_,d in pairs if d<=5),
      pairs_5_to_15m=sum(1 for _,_,d in pairs if 5<d<=15))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,help='Local artifact CSV destination')
    parser.add_argument('--publish',action='store_true',help='Stage only into the separately labeled ODbL Supabase audit; publish after full count')
    args=parser.parse_args()
    source_day=dt.datetime.now(dt.timezone.utc).date().isoformat()
    rows=prepare_rows(download_source(),source_day)
    pairs=candidates(rows)
    stats=summarize(pairs)
    with open(args.output,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['osm_key_a','osm_key_b','distance_m','interpretation'])
        for a,b,m in pairs:
            w.writerow([a,b,f'{m:.2f}','possible_geographic_overlap_only'])
    print('OSM NATIONAL POSSIBLE OVERLAP AUDIT source_rows',len(rows))
    for k,v in stats.items():print('OSM NATIONAL POSSIBLE OVERLAP AUDIT',k,v)
    print('OSM NATIONAL POSSIBLE OVERLAP AUDIT no records merged/deleted or promoted')
    print('OSM NATIONAL POSSIBLE OVERLAP AUDIT ODbL 1.0 © OpenStreetMap contributors')
    if args.publish:
        from publish_osm_nearby import publish
        publish(source_day,len(rows),pairs)


if __name__=='__main__':main()
