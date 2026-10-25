"""Discover exact Flock portal hyperlinks from reviewed agency webpages.

This crawler ONLY fetches exact pre-reviewed original agency pages. It NEVER
fetches Flock Safety portal content, its APIs or their search indexes. Links
become PRIVATE non-authoritative leads and cannot publish a camera or metric.
"""
import argparse
from collections import Counter
import datetime as dt
import re
from urllib.parse import urljoin, urlsplit, quote

from auto_verify_flock_agenda import api_request
from discover_government_gis_links import (
    fetch_government_page, normalized_url, get_seed_pages,
    original_camera_disclosure
)
from government_domain_registry import load_approved_domains
from paged_supabase import fetch_all

MAX_PAGES=20
VENDOR_HOST='transparency.flocksafety.com'
PORTAL_PATH=re.compile(r'^/[a-z0-9-]+/?$')


def portal_url(value):
    url=normalized_url(value) if isinstance(value,str) else None
    if not url:return None
    part=urlsplit(url)
    if (part.scheme!='https' or part.hostname!=VENDOR_HOST or
        part.port is not None or part.username or part.password or
        part.query or part.fragment or not PORTAL_PATH.fullmatch(part.path)):
        return None
    return url.rstrip('/')


def reviewed_original_pages(api=api_request):
    # No internet search hits, third-party ArcGIS title pages or discovered
    # arbitrary domains can become input to this collector.
    rows=fetch_all(api,
        'flock_documented_programs?select=program_key,official_evidence_url'
        '&record_status=eq.verified&limit=100',
        'program_key',max_records=1000)
    seeds,_=get_seed_pages(load_approved_domains())
    pages={url for url,_ in seeds}
    # Original Live Oak police Flock page was independently live-checked and links
    # its municipal camera map and first-party Flock vendor portal directly.
    pages.add('https://www.liveoaktx.net/departments/police/flock-safety')
    # Bexar County's official Sheriff Flock page directly discloses its portal.
    # Its source is a program link, not proof of any exact camera positions.
    pages.add('https://www.bexar.org/4072/Flock-Safety')
    for item in rows:
        original=normalized_url(item.get('official_evidence_url') or '')
        if original:pages.add(original)
    if len(pages)>1000:
        raise ValueError('Unbounded original reviewed agency source registry')
    ordered=sorted(pages)
    if not ordered:return []
    # Bound daily original-agency requests and rotate to reach all sources
    # across runs, instead of starving late-sorted municipalities.
    start=(dt.datetime.now(dt.timezone.utc).date().toordinal()*MAX_PAGES)%len(ordered)
    return [ordered[(start+i)%len(ordered)]
            for i in range(min(MAX_PAGES,len(ordered)))]


def direct_vendor_portals(document,page,page_hash):
    if not re.fullmatch(r'[a-f0-9]{64}',page_hash):
        raise ValueError('Original government page proof malformed')
    if not original_camera_disclosure(document):
        return []
    unique=set()
    for raw,label in document.anchors:
        if not isinstance(raw,str) or len(raw)>1500:continue
        portal=portal_url(urljoin(page,raw))
        if portal:unique.add(portal)
    return [
        {'government_source_url':page,'portal_url':url,
         'government_page_sha256':page_hash}
        for url in sorted(unique)
    ][:30]


def stage(item,api=None):
    api=api or api_request
    # A changed source webpage never silently replaces an old receipt.
    params=('flock_vendor_portal_source_leads?select=government_source_url,'
            'portal_url,government_page_sha256&government_source_url=eq.'+
            quote(item['government_source_url'],safe='')+
            '&portal_url=eq.'+quote(item['portal_url'],safe='')+'&limit=2')
    prev=api(params)
    if not isinstance(prev,list) or len(prev)>1:
        raise ValueError('Cannot reconcile original vendor portal hyperlink receipt')
    if prev:
        if (prev[0].get('government_source_url')!=item['government_source_url'] or
            prev[0].get('portal_url')!=item['portal_url'] or
            prev[0].get('government_page_sha256')!=item['government_page_sha256']):
            raise ValueError('Original agency portal hyperlink receipt changed; hold')
        return False
    result=api('flock_vendor_portal_source_leads?on_conflict=government_source_url,portal_url',
        method='POST',payload=[item],
        prefer='resolution=ignore-duplicates,return=minimal')
    if result is not None:
        raise ValueError('Unexpected private portal lead staging response')
    return True


def scan(dry_run=False,pages=None):
    pages=reviewed_original_pages() if pages is None else pages
    counts=Counter()
    for page in pages:
        try:
            source,digest=fetch_government_page(page)
            counts['original_pages_read']+=1
            records=direct_vendor_portals(source,page,digest)
            counts['direct_vendor_portal_links']+=len(records)
            if not dry_run:
                for record in records:
                    if stage(record):counts['new_private_leads']+=1
        except Exception as exc:
            counts['original_pages_held']+=1
            print('Original agency vendor portal discovery held:',
                  type(exc).__name__,urlsplit(page).hostname)
    for k in ('original_pages_read','original_pages_held',
              'direct_vendor_portal_links','new_private_leads'):
        print('Original agency vendor portal discovery '+k+':',counts[k])
    print('Vendor portal pages / Flock APIs fetched: 0')
    print('Newly approved vendor metrics or camera points: 0')
    return counts


if __name__=='__main__':
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('--dry-run',action='store_true')
    result=scan(dry_run=args.parse_args().dry_run)
    if result['original_pages_read']==0:
        raise SystemExit('No original reviewed agency pages available for portal research')
