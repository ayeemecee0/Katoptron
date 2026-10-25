"""One private status ledger for all GIS sources and already-staged camera cases.

Runs after triage, not another geometry scraper. Archived leads are never
deleted; exact approved sources and already-published points cease counting as
new coverage. Repeated runs preserve original hold dates until facts change.
"""
from collections import Counter
from auto_verify_flock_agenda import api_request
from paged_supabase import fetch_all

MAX=200

def run(api=api_request):
    results={}
    for rpc in ('reconcile_flock_gis_candidate_lifecycle',
                'reconcile_flock_gis_point_case_dispositions'):
        r=api('rpc/'+rpc,method='POST',payload={})
        if not isinstance(r,dict):
            raise ValueError('Private GIS lifecycle reconciliation returned incomplete receipt')
        results[rpc]=r
    sources=fetch_all(api,
      'flock_gis_candidate_lifecycle?select=gis_layer_url,disposition,next_review_after'
      '&limit=100','gis_layer_url',max_records=MAX)
    cases=fetch_all(api,
      'flock_gis_point_case_dispositions?select=case_key,disposition,next_action_after'
      '&limit=100','case_key',max_records=MAX)
    if len(sources)<13 or len(cases)<62:
        raise ValueError('Original candidate lifecycle unexpectedly incomplete')
    categories=Counter(r['disposition'] for r in sources)
    case_categories=Counter(r['disposition'] for r in cases)
    for k,n in sorted(categories.items()):
        print('SOURCE LIFECYCLE',k,n)
    for k,n in sorted(case_categories.items()):
        print('POINT CASE LIFECYCLE',k,n)
    print('PRIVATE CANDIDATE LEDGER source_records',len(sources))
    print('PRIVATE CANDIDATE LEDGER point_records',len(cases))
    print('PUBLIC VERIFIED CAMERAS CREATED BY RECONCILIATION',0)
    return results

if __name__=='__main__':
    try:run()
    except Exception as exc:
        raise SystemExit('Private source reconciliation held: '+type(exc).__name__) from None
