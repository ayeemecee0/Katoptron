"""Reconcile exact Flock portal links on already reviewed city-program pages.

A direct hyperlink is separate from individual camera verification and never
authorizes a camera position or vendor-reported operational count.
"""
from datetime import datetime, timezone
from urllib.parse import quote
from collections import Counter
from auto_verify_flock_agenda import api_request
from discover_government_gis_links import fetch_government_page
from discover_official_vendor_portals import direct_vendor_portals
from paged_supabase import fetch_all

def inspect(program, api=api_request, fetch=fetch_government_page):
    key=program['program_key']
    document,digest=fetch(program['official_evidence_url'])
    discovered={x['portal_url'] for x in direct_vendor_portals(
        document,program['official_evidence_url'],digest)}
    if len(discovered)>8:raise ValueError('Too many linked vendor portals')
    old=api('flock_government_vendor_directory?select=portal_url&program_key=eq.'+
            quote(key,safe='')+'&limit=20')
    if not isinstance(old,list) or len(old)>8:
        raise ValueError('Previously linked source set incomplete')
    previous={x['portal_url'] for x in old}
    if len(previous)!=len(old):raise ValueError('Duplicate source identities')
    stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
    for url in sorted(discovered):
        item=dict(program_key=key,portal_url=url,government_page_sha256=digest,
                  checked_at=stamp,link_status='direct_government_link')
        reply=api('flock_government_vendor_directory?on_conflict=program_key,portal_url',
                  method='POST',payload=[item],
                  prefer='resolution=merge-duplicates,return=minimal')
        if reply is not None:raise ValueError('Unexpected source write response')
    for url in sorted(previous-discovered):
        reply=api('flock_government_vendor_directory?program_key=eq.'+
                  quote(key,safe='')+'&portal_url=eq.'+quote(url,safe=''),
                  method='PATCH',payload={'link_status':'withdrawn'},
                  prefer='return=minimal')
        if reply is not None:raise ValueError('Unexpected revocation response')
    return len(discovered)

def run(api=api_request,fetch=fetch_government_page):
    records=fetch_all(api,'flock_documented_programs?select=program_key,official_evidence_url'
        '&record_status=eq.verified&limit=100','program_key',max_records=1000)
    counts=Counter()
    for program in records:
        try:
            counts['links']+=inspect(program,api,fetch)
            counts['pages_rechecked']+=1
        except Exception as error:
            counts['held']+=1
            print('Official vendor-link source held',type(error).__name__)
    print('GOVERNMENT LINK DIRECTORY successful_original_pages',counts['pages_rechecked'])
    print('GOVERNMENT LINK DIRECTORY direct_vendor_portals',counts['links'])
    print('GOVERNMENT LINK DIRECTORY held_pages',counts['held'])
    print('Vendor cameras published: 0')
    return counts

if __name__=='__main__':run()
