#!/usr/bin/env python3
"""Strict recurring original-government verification for agency-authored ALPR
audits. These are never passed off as independent external reviews.
"""
import hashlib, io, json, re
from pathlib import Path
from urllib.parse import urlsplit
from pypdf import PdfReader
from inspect_multistate_flock_audits import DOCUMENTS,fetch
from verify_independent_audit_source import get_pdf

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/verified-agency-published-alpr-audits.json'
HOSTS={'www.lrl.mn.gov','www.sanbruno.ca.gov','www.greenbaywi.gov'}
ALLOWED_MN='https://www.lrl.mn.gov/docs/2019/mandated/191260.pdf'
ANCHORS={
 'hennepin-county-mn-internal-alpr-audit-2017':{
  1:['hennepin county','did not use fixed alprs'],
  2:['configured to purge data after 30 days','system-generated log','more than 60 days']},
 'san-bruno-ca-flock-audit-december-2025':{
  1:['january 5th, 2025','december 2025','1238','461,711','total cameras','operational']},
 'san-bruno-ca-flock-audit-first-half-2026':{
  1:['july 14th, 2026','twenty-nine (29) searches','ncric','removed ncric','operational']},
 'green-bay-wi-alpr-annual-audit-2025':{
  1:['may 8, 2026','42 flock cameras','50 patrol vehicles'],
  2:['299 agencies','purge data for 2025 is unavailable','national lookup'],
  3:['no misuse was reported in 2025']}
}
def allowed(report):
 if not isinstance(report,dict):return False
 url=report.get('source_url','')
 if not isinstance(url,str) or len(url)>600:return False
 try:
  v=urlsplit(url)
  if v.scheme!='https' or v.hostname not in HOSTS or v.netloc!=v.hostname or v.username or v.password or v.query or v.fragment:return False
 except (TypeError,ValueError):return False
 if report.get('id')=='hennepin-county-mn-internal-alpr-audit-2017':
  return url==ALLOWED_MN and report.get('publisher_type')=='agency_internal_audit'
 for key,(fixed_url,_) in DOCUMENTS.items():
  if key in report.get('id','') and url==fixed_url and report.get('publisher_type')=='agency_authored_audit':return True
 # The public source ID is intentionally mapped, never inferred from URL hostname.
 ident={
  'san-bruno-ca-flock-audit-december-2025':'san-bruno-ca-2025',
  'san-bruno-ca-flock-audit-first-half-2026':'san-bruno-ca-2026',
  'green-bay-wi-alpr-annual-audit-2025':'green-bay-wi-2025'
 }.get(report.get('id'))
 return bool(ident and url==DOCUMENTS[ident][0] and report.get('publisher_type')=='agency_authored_audit')
def records(data):
 if not isinstance(data,dict) or data.get('schema_version')!=1 or not isinstance(data.get('reports'),list) or not 1<=len(data['reports'])<=80:
  raise ValueError('Invalid bounded official agency-authored audit catalog')
 seen=set()
 for r in data['reports']:
  if not allowed(r) or r.get('id') in seen or r.get('id') not in ANCHORS:raise ValueError('Unapproved government publisher audit identity')
  seen.add(r['id'])
  if not re.fullmatch(r'[0-9a-f]{64}',r.get('content_sha256','')):raise ValueError('Original public PDF hash required')
  if not r.get('findings') or len(r['findings'])>12:raise ValueError('Unbounded curator findings')
  if not set(ANCHORS[r['id']]).issubset(set(r.get('pages_reviewed',[]))):raise ValueError('Original pages not reviewed')
  for f in r['findings']:
   if not isinstance(f.get('page'),int) or f['page'] not in r['pages_reviewed'] or not 40<=len(f.get('statement',''))<800:
    raise ValueError('Missing page citation or bounded statement')
 return data['reports']
def verify(report,payload,reader=PdfReader):
 if not isinstance(payload,bytes) or len(payload)<100 or len(payload)>3_000_000 or not payload.startswith(b'%PDF-'):
  raise ValueError('Original source PDF invalid')
 if hashlib.sha256(payload).hexdigest()!=report['content_sha256']:
  raise ValueError('Government-authored original PDF changed, no automatic publication')
 doc=reader(io.BytesIO(payload),strict=True)
 if doc.is_encrypted or len(doc.pages)>25 or len(doc.pages)<max(report['pages_reviewed']):
  raise ValueError('Original source pages missing')
 for page,phrases in ANCHORS[report['id']].items():
  text=' '.join((doc.pages[page-1].extract_text() or '').lower().split())
  if not all(p in text for p in phrases):
   raise ValueError('Page-verified original agency finding changed '+report['id']+' page '+str(page)+' missing '+','.join(p for p in phrases if p not in text)[:115])
 return len(doc.pages)
def run():
 for report in records(json.loads(MANIFEST.read_text(encoding='utf-8'))):
  if report['id']=='hennepin-county-mn-internal-alpr-audit-2017':
   raw=get_pdf(report['source_url'])
  else:
   ident={'san-bruno-ca-flock-audit-december-2025':'san-bruno-ca-2025',
          'san-bruno-ca-flock-audit-first-half-2026':'san-bruno-ca-2026',
          'green-bay-wi-alpr-annual-audit-2025':'green-bay-wi-2025'}[report['id']]
   raw=fetch(ident)
  print('SOURCE VERIFIED',report['state'],report['id'],verify(report,raw),
        hashlib.sha256(raw).hexdigest(),'PUBLISHER',report['publisher_type'])
 print('ALL OFFICIAL AGENCY REPORT HASHES AND PAGES PASS; no plates, raw PDFs or private movements retained')
if __name__=='__main__':
 try:run()
 except Exception as e:raise SystemExit('ORIGINAL AGENCY SOURCE HELD: '+type(e).__name__+': '+str(e)[:160]) from None
