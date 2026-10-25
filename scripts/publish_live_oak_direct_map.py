"""Publish only fully rechecked original Live Oak police camera-map positions.

The city Flock Safety page itself links the precise camera map. Manufacturer
labels remain generic LPR Camera; evidence summaries must not claim that each
device's brand, installation date, or uptime is independently certified.
Any loss of the city link, GIS completeness or source policy fails closed.
"""
from auto_verify_flock_agenda import api_request
from paged_supabase import fetch_all
from probe_peoria_overlap import summarize
from verify_live_oak_direct_map import KEY,LAYER,authorize,qualify

def reviewed_authority(api=api_request):
    sources=api('trusted_flock_gis_sources?select=source_key,gis_layer_url,'
        'government_evidence_url,jurisdiction_label,expected_id_field,'
        'bounds_south,bounds_west,bounds_north,bounds_east,source_status'
        '&source_key=eq.live_oak_tx&limit=2')
    policies=api('gis_verification_profiles?select=source_key,profile_status,'
        'identity_mode,service_evidence_mode,expected_layer_name,camera_id_field,'
        'vendor_field&source_key=eq.live_oak_tx&limit=2')
    if (not isinstance(sources,list) or len(sources)!=1 or
        not isinstance(policies,list) or len(policies)!=1):
        raise ValueError('Exact municipal camera-map source not owner reviewed')
    authorize(sources[0],policies[0])
    return sources[0],policies[0]

def reconcile(publish=False,api=api_request,validate=qualify):
    source,policy=reviewed_authority(api)
    rows,held,n=validate(source,policy)
    if held or not 1<=n<=150 or len(rows)!=n:
        raise ValueError('Original city-linked map inventory not entirely verified')
    canonical=fetch_all(api,
        'flock_camera_locations?select=record_key,latitude,longitude,source_url'
        '&verification_status=eq.verified&location_accuracy=eq.exact&limit=100',
        'record_key',max_records=5000)
    # Compare only OTHER jurisdictions/sources. Rechecks must not count their
    # own previously published points as newly discovered duplicates.
    other=[x for x in canonical if x.get('source_url')!=LAYER]
    if len(canonical)<293:
        raise ValueError('Canonical inventory unexpectedly incomplete')
    near=summarize([(x['latitude'],x['longitude']) for x in rows],other)
    if near['possible_existing_nearby']:
        raise ValueError('Existing public point within 100m of original city map')
    if not publish:
        print('LIVE OAK source-qualified points',len(rows))
        print('LIVE OAK public records written',0)
        return len(rows)
    from auto_verify_camera_profiles import (
        fetch_existing,validate_reconciliation_delta,
        confirm_time_separated_withdrawals,publish_verified_batches)
    old=fetch_existing('gis-'+KEY+'-')
    missing=validate_reconciliation_delta(old,{r['record_key'] for r in rows})
    approved,pending=confirm_time_separated_withdrawals(KEY,missing)
    result=publish_verified_batches(rows,approved)
    print('LIVE OAK original government map source-qualified',len(rows))
    print('LIVE OAK new verified source points published',result['published'])
    print('LIVE OAK current points rechecked',result['rechecked'])
    print('LIVE OAK pending independent camera withdrawal',pending)
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--publish',action='store_true')
    args=p.parse_args()
    try:reconcile(publish=args.publish)
    except Exception as e:
        # Never print unverified GPS rows, requests, API response bodies or keys.
        raise SystemExit('Live Oak exact-source publication held: '+type(e).__name__) from None
