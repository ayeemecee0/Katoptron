#!/usr/bin/env python3
"""Recheck Katoptron's ORIGINAL named Flock sharing publishers.

Original city or vendor-hosted permission lists are stronger than licensed
aggregator data. Rechecks must never assume an HTTP 403, lost section,
a changed page template or an incomplete source page means access revoked.
No raw ALPR records, camera geocodes, subscriber data or source HTML stored.
"""
import hashlib
import html
import json
import os
import re
import urllib.parse
import urllib.request
import urllib.error
from html.parser import HTMLParser

ALLOWED_HOSTS={'elkgrove.gov','www.cityofwoodland.gov',
               'transparency.flocksafety.com'}
LIMIT=5_000_000


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks=[]
        self.suppressed=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript'):self.suppressed+=1
        elif tag in ('li','p','td','div','h1','h2','h3','h4','br'):
            self.chunks.append(' ')
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript') and self.suppressed:
            self.suppressed-=1
        else:self.chunks.append(' ')
    def handle_data(self,data):
        if not self.suppressed:self.chunks.append(data)
    def get_text(self):
        return ' '.join(' '.join(self.chunks).split())


def normalize(value):
    return ' '.join(html.unescape(value).split()).casefold()


def evaluate(body,section,recipients):
    parser=Text()
    parser.feed(body.decode('utf8','replace'))
    text=normalize(parser.get_text())
    if not text or normalize(section) not in text:
        return 'source_section_unavailable',0
    count=sum(1 for name in recipients if
        re.search(r'(?<![a-z0-9])'+re.escape(normalize(name))+r'(?![a-z0-9])',text))
    return ('all_previously_published_names_still_present'
            if count==len(recipients) else 'publisher_list_changed_or_incomplete'),count


def permitted_url(url):
    p=urllib.parse.urlsplit(url)
    return p.scheme=='https' and p.hostname in ALLOWED_HOSTS and not p.username and not p.password


def original_page(url,opener=None):
    if not permitted_url(url):raise ValueError('Source host not independently allowlisted')
    opener=opener or urllib.request.urlopen
    req=urllib.request.Request(url,headers={
      'User-Agent':'Katoptron-Public-Source-Recheck/1.0',
      'Accept':'text/html'})
    with opener(req,timeout=25) as response:
        status=getattr(response,'status',200)
        # Only inspect content returned by the original source, not
        # unexpected cross-domain redirects to other renderers.
        resolved=response.geturl() if hasattr(response,'geturl') else url
        if not permitted_url(resolved):
            raise ValueError('Unexpected external source redirect')
        if status!=200:raise urllib.error.HTTPError(url,status,'Source unavailable',{},None)
        data=response.read(LIMIT+1)
        if len(data)>LIMIT:raise ValueError('Source HTML exceeds size bound')
        return data,status


def query(url,token,table,fields,extra=''):
    rows=[]
    for offset in range(0,15000,500):
        q=urllib.parse.urlencode({'select':fields,'limit':'500','offset':str(offset)})
        if extra:q+='&'+extra
        req=urllib.request.Request(url.rstrip('/')+'/rest/v1/'+table+'?'+q,
          headers={'apikey':token,'Authorization':'Bearer '+token})
        with urllib.request.urlopen(req,timeout=40) as response:batch=json.load(response)
        if not isinstance(batch,list):raise ValueError('Incomplete verification database response')
        rows.extend(batch)
        if len(batch)<500:return rows
    raise ValueError('First-party sharing source table too large')


def write(url,token,table,rows,method='POST',extra=''):
    if not rows:return
    endpoint=url.rstrip('/')+'/rest/v1/'+table
    if extra:endpoint+='?'+extra
    req=urllib.request.Request(endpoint,
      data=json.dumps(rows).encode(),method=method,
      headers={'apikey':token,'Authorization':'Bearer '+token,
               'Content-Type':'application/json',
               'Prefer':'return=minimal'})
    with urllib.request.urlopen(req,timeout=35) as response:
        if response.status not in (200,201,204):raise ValueError('Source check write failed')


def recheck_sources(sources,edges,fetcher=original_page):
    names={}
    for r in edges:names.setdefault(r['source_key'],[]).append(r['recipient_label'])
    results=[]
    for source in sources:
        expected=names.get(source['source_key'],[])
        if not expected:continue
        status=None;digest=None;matched=0
        try:
            data,http=fetcher(source['source_url'])
            status,count=evaluate(data,source['source_section'],expected)
            digest=hashlib.sha256(data).hexdigest()
            matched=count
        except urllib.error.HTTPError as err:
            status='source_fetch_unavailable';http=err.code
        except (TimeoutError,OSError,ValueError,UnicodeError):
            status='source_fetch_unavailable';http=None
        results.append({
            'source_key':source['source_key'],'check_result':status,
            'expected_names':len(expected),'matched_names':matched,
            'source_http_status':http,'page_sha256':digest
        })
    return results


def main():
    url=os.getenv('SUPABASE_URL')
    token=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not token:raise RuntimeError('Owner-only source review API unavailable')
    sources=query(url,token,'flock_original_sharing_sources',
                  'source_key,source_url,source_section')
    edges=query(url,token,'flock_original_sharing_edges',
                'source_key,recipient_label')
    results=recheck_sources(sources,edges)
    for x in results:
        write(url,token,'flock_original_sharing_rechecks',[x])
        if x['check_result']=='all_previously_published_names_still_present':
            params='source_key=eq.'+urllib.parse.quote(x['source_key'])
            write(url,token,'flock_original_sharing_sources',
                [{'last_successfully_rechecked_at':'now()'}],
                method='PATCH',extra=params)
    print('Original publisher source checks:',len(results),
          'complete=',sum(x['check_result']=='all_previously_published_names_still_present' for x in results),
          'changed_or_unrendered=',sum(x['check_result']=='publisher_list_changed_or_incomplete' for x in results),
          'source_unavailable=',sum(x['check_result']=='source_fetch_unavailable' for x in results),
          'section_unavailable=',sum(x['check_result']=='source_section_unavailable' for x in results))
    print('No automatically revoked sharing grants, anonymous privileges or camera locations changed.')


if __name__=='__main__':
    try:main()
    except Exception as e:
        raise SystemExit('Original sharing recheck held: '+type(e).__name__+': '+str(e)[:120]) from None
