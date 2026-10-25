"""Read-only privacy-safe Peoria source overlap audit against all canonical points.

No inserts, upgrades, source authorization, or individual coordinate logging.
Requires existing Supabase server-side credentials in the private CI environment.
"""
from paged_supabase import fetch_all
from auto_verify_flock_agenda import api_request
from probe_peoria_gis import inventory
from triage_gis_verification_backlog import near

MAX_EXISTING = 5000


def summarize(source_points, canonical):
    if not isinstance(source_points, list) or not isinstance(canonical, list):
        raise ValueError('Missing source or canonical inventory')
    if not source_points:
        raise ValueError('Original GIS inventory empty')
    if len(canonical) >= MAX_EXISTING:
        raise ValueError('Canonical inventory reached safety cap: incomplete possible')
    existing = []
    for row in canonical:
        lat, lon = row.get('latitude'), row.get('longitude')
        if type(lat) not in (int, float) or type(lon) not in (int, float):
            raise ValueError('Canonical location has invalid geometry')
        existing.append((lat, lon))
    nearby = sum(any(near(point, other) for other in existing)
                 for point in source_points)
    return {'source_points': len(source_points),
            'possible_existing_nearby': nearby,
            'no_existing_within_100m': len(source_points) - nearby}


def main():
    source = inventory(include_private_points=True)
    records = fetch_all(api_request,
        'flock_camera_locations?select=record_key,latitude,longitude'
        '&verification_status=eq.verified&location_accuracy=eq.exact&limit=100',
        'record_key', max_records=MAX_EXISTING)
    if len(records) < 293:
        raise ValueError('Existing canonical camera inventory incomplete')
    result = summarize(source['_private_points'], records)
    print('PEORIA read-only total original features', result['source_points'])
    print('PEORIA possible nearby already published', result['possible_existing_nearby'])
    print('PEORIA without existing point within 100 metres', result['no_existing_within_100m'])
    print('PEORIA proximity only does NOT establish device identity')
    print('PEORIA source status active/installed not established')
    print('PEORIA newly published 0')


if __name__ == '__main__':
    main()
