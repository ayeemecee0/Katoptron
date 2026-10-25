"""Discover original government Flock disclosures that link ArcGIS camera apps.

Public govt Flock context + exact government hyperlink + real ArcGIS item
constitute a PRIVATE discovery lead only. Neither item titles nor raw ArcGIS
publisher names can approve camera points. Rotates reviewed city sources.
"""
import argparse
import datetime as dt
import re
from collections import Counter
from urllib.parse import parse_qs,urljoin,urlsplit,quote

from auto_verify_camera_gis import get_official_json
from auto_verify_flock_agenda import api_request
from discover_government_gis_links import (
    fetch_government_page,original_camera_disclosure,normalized_url)
from discover_official_vendor_portals import reviewed_original_pages
from paged_supabase import fetch_all

ITEM='https://www.arcgis.com/sharing/rest/content/items/'
ID=re.compile(r'^[a-fA-F0-9]{32}$')
HOST=re.compile(r'^[a-z0-9-]+[.]maps[.]arcgis[.]com$')
APP_PATH=re.compile(
    r'^/apps/(?:instant/[A-Za-z0-9_-]{2,35}/index[.]html|'
    r'webappviewer/index[.]html|mapviewer/index[.]html)$',re.I)
APP_TYPES={'Web Mapping Application','Web Experience','Dashboard','StoryMap','Web Map'}
MAX_PAGES=50
MAX_LINKS=15
EXACT_CITY_PAGES=('https://www.liveoaktx.net/departments/police/flock-safety',)

def map_app_url(value):
    if not isinstance(value,str) or len(value)>900:return None
    clean=normalized_url(value)
    if not clean:return None
    p=urlsplit(clean)
    if (p.scheme!='https' or not p.hostname or not HOST.fullmatch(p.hostname)
        or not APP_PATH.fullmatch(p.path) or p.fragment or p.port not in (None,443)):
        return None
    query=parse_qs(p.query,keep_blank_values=True)
    field='webmap' if p.path.lower()=='/apps/mapviewer/index.html' else 'appid'
    if set(query)!={field} or len(query[field])!=1 or not ID.fullmatch(query[field][0]):
        return None
    return clean,query[field][0].lower()

def proposed(document,page,digest,fetch_item=get_official_json):
    if not isinstance(digest,str) or not re.fullmatch(r'[a-f0-9]{64}',digest):
        raise ValueError('Original-government page proof invalid')
    if not original_camera_disclosure(document):return []
    links={}
    for href,label in document.anchors:
        if not isinstance(href,str) or len(href)>1500:continue
        candidate=map_app_url(urljoin(page,href))
        if not candidate:continue
        # The original agency page must call this a camera/map and not
        # merely host a generic city planning map alongside Flock prose.
        title=' '.join((label or '').lower().split())
        if ('map' not in title or not any(word in title for word in
            ('flock','camera','alpr','license plate','lpr'))):
            continue
        url,item_id=candidate
        links[url]=item_id
    if len(links)>MAX_LINKS:raise ValueError('Government camera-app links unusually broad')
    result=[]
    for url,item_id in sorted(links.items()):
        meta=fetch_item(ITEM+item_id+'?f=json')
        if (not isinstance(meta,dict) or str(meta.get('id','')).lower()!=item_id
            or meta.get('type') not in APP_TYPES
            or not isinstance(meta.get('owner'),str)):
            continue
        result.append(dict(
          government_page_url=page,app_url=url,arcgis_app_id=item_id,
          agency_page_sha256=digest,arcgis_item_type=meta['type']))
    return result

def sync_original_page(page,records,api=api_request):
    query='flock_government_camera_map_app_leads?select=app_url,agency_page_sha256,evidence_status' + (
       '&government_page_url=eq.'+quote(page,safe='')+'&limit=100')
    old=api(query)
    if not isinstance(old,list) or len(old)>MAX_LINKS:
        raise ValueError('Original source map-app registry truncated')
    previous={r['app_url']:r for r in old}
    if len(previous)!=len(old):raise ValueError('Source registry has duplicate map apps')
    fresh={r['app_url']:r for r in records}
    if len(fresh)!=len(records):raise ValueError('Multiple inconsistent source app receipts')
    stats=Counter()
    for url,proof in fresh.items():
        if url not in previous:
            ret=api('flock_government_camera_map_app_leads?on_conflict=government_page_url,app_url',
                    method='POST',payload=[proof],
                    prefer='resolution=ignore-duplicates,return=minimal')
            if ret is not None:raise ValueError('Unexpected private app lead insert response')
            stats['new_private_apps']+=1
        else:
            old_row=previous[url]
            changed=old_row['agency_page_sha256']!=proof['agency_page_sha256']
            status='held' if changed and old_row['evidence_status']=='reviewed' else old_row['evidence_status']
            ret=api('flock_government_camera_map_app_leads?government_page_url=eq.'+
                    quote(page,safe='')+'&app_url=eq.'+quote(url,safe=''),
                    method='PATCH',payload={
                        'last_checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),
                        'agency_page_sha256':proof['agency_page_sha256'],
                        'evidence_status':status},prefer='return=minimal')
            if ret is not None:raise ValueError('Unexpected private app recheck response')
            stats['source_apps_rechecked']+=1
            if status=='held':stats['held_due_to_evidence_change']+=1
        receipt={
            'government_page_url':page,'app_url':url,
            'agency_page_sha256':proof['agency_page_sha256']}
        ret=api('flock_government_camera_map_app_receipts?on_conflict=government_page_url,app_url,agency_page_sha256',
                method='POST',payload=[receipt],
                prefer='resolution=ignore-duplicates,return=minimal')
        if ret is not None:raise ValueError('Private immutable source fingerprint not recorded')
    for url,old_row in previous.items():
        if url not in fresh and old_row['evidence_status']!='held':
            ret=api('flock_government_camera_map_app_leads?government_page_url=eq.'+
                    quote(page,safe='')+'&app_url=eq.'+quote(url,safe=''),
                    method='PATCH',payload={'evidence_status':'held'},
                    prefer='return=minimal')
            if ret is not None:raise ValueError('Removed source app hold not recorded')
            stats['removed_links_held']+=1
    return stats

def all_reviewed_pages(api=api_request,partial=reviewed_original_pages):
    # Include ALL recorded official deployment and GIS source pages each
    # cycle, not just the vendor registry's rotating 20-page window.
    programmes=fetch_all(api,
      'flock_documented_programs?select=program_key,official_evidence_url'
      '&record_status=eq.verified&limit=100',
      'program_key',max_records=1000)
    source_roots=fetch_all(api,
      'trusted_flock_gis_sources?select=source_key,government_evidence_url'
      '&source_status=eq.verified&limit=100',
      'source_key',max_records=500)
    pages=[*EXACT_CITY_PAGES,*partial()]
    pages.extend(row['official_evidence_url'] for row in programmes)
    pages.extend(row['government_evidence_url'] for row in source_roots)
    dedup=sorted({page for page in pages if isinstance(page,str)
                  and normalized_url(page)==page})
    if len(dedup)>1000:raise ValueError('Unbounded vetted camera-map search pages')
    if len(dedup)<=MAX_PAGES:return dedup
    start=(dt.datetime.now(dt.timezone.utc).date().toordinal()*MAX_PAGES)%len(dedup)
    return [dedup[(start+i)%len(dedup)] for i in range(MAX_PAGES)]


def run(dry_run=False,pages=None,fetch=fetch_government_page,
        fetch_item=get_official_json,api=api_request):
    page_list=list(dict.fromkeys(pages if pages is not None
        else all_reviewed_pages(api)))[:MAX_PAGES]
    stats=Counter()
    for page in page_list:
        try:
            doc,digest=fetch(page)
            records=proposed(doc,page,digest,fetch_item)
            stats['government_pages_checked']+=1
            stats['camera_map_apps_discovered']+=len(records)
            if not dry_run:stats.update(sync_original_page(page,records,api))
        except Exception as error:
            stats['government_pages_held']+=1
            print('ORIGINAL GOV APP page held',type(error).__name__)
    for key in ('government_pages_checked','government_pages_held',
                'camera_map_apps_discovered','new_private_apps',
                'source_apps_rechecked','removed_links_held',
                'held_due_to_evidence_change'):
        print('ORIGINAL GOV APP',key,stats[key])
    print('ORIGINAL GOV APP public cameras automatically verified',0)
    return stats

if __name__=='__main__':
    opts=argparse.ArgumentParser(description=__doc__)
    opts.add_argument('--dry-run',action='store_true')
    arguments=opts.parse_args()
    if run(dry_run=arguments.dry_run)['government_pages_checked']==0:
        raise SystemExit('No original reviewed city camera-map pages accessible')
