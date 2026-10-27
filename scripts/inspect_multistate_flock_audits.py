#!/usr/bin/env python3
"""Read-only bounded source preflight for publisher-authored public Flock ALPR audits.

No plates, timestamps for individual searches, private data or full PDFs saved.
This is independent of MN outside-auditor manifest: agency-written audits are
not rebranded as independent third-party audits.
"""
import hashlib, io, urllib.request, urllib.parse, json
from pypdf import PdfReader
DOCUMENTS={
 'san-bruno-ca-2025':('https://www.sanbruno.ca.gov/DocumentCenter/View/9280/SBPD-Flock-ALPR-Annual-Audit---2025','www.sanbruno.ca.gov'),
 'san-bruno-ca-2026':('https://www.sanbruno.ca.gov/DocumentCenter/View/9279/SBPD-Flock-ALPR-Audit-Q1-and-Q2-2026','www.sanbruno.ca.gov'),
 'green-bay-wi-2025':('https://www.greenbaywi.gov/DocumentCenter/View/18762/Green-Bay-PD-2025-Automated-License-Plate-Reader-ALPR-Annual-Audit','www.greenbaywi.gov'),
}
MAX_BYTES=3_000_000
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError('Publisher redirected')
def allowed(source_id,url):
 return (source_id in DOCUMENTS and url==DOCUMENTS[source_id][0] and
  urllib.parse.urlsplit(url).hostname==DOCUMENTS[source_id][1] and
  urllib.parse.urlsplit(url).scheme=='https')
def fetch(source_id,client=None):
 url=DOCUMENTS[source_id][0]
 if not allowed(source_id,url):raise ValueError('Original URL not allowlisted')
 op=client or urllib.request.build_opener(DenyRedirect())
 req=urllib.request.Request(url,headers={'User-Agent':'Katoptron-original-public-audit-provenance/1.0','Accept':'application/pdf'})
 with op.open(req,timeout=25) as r:
  if r.status!=200 or r.geturl()!=url:raise ValueError('Original publisher unavailable')
  body=r.read(MAX_BYTES+1)
 if not 100<len(body)<=MAX_BYTES or not body.startswith(b'%PDF-'):raise ValueError('Publisher PDF not supported within bounds')
 return body
def fingerprint(key,body,reader=PdfReader):
 if not allowed(key,DOCUMENTS[key][0]) or not isinstance(body,bytes) or len(body)>MAX_BYTES or not body.startswith(b'%PDF-'):
  raise ValueError('Untrusted public audit')
 pdf=reader(io.BytesIO(body),strict=True)
 if pdf.is_encrypted or not 1<=len(pdf.pages)<=25:raise ValueError('Original PDF not readable')
 return {'id':key,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'pages':len(pdf.pages)}
def main():
 good=0
 for key in DOCUMENTS:
  try:
   raw=fetch(key)
   v=fingerprint(key,raw)
   print('ORIGINAL',json.dumps(v,sort_keys=True))
   pdf=PdfReader(io.BytesIO(raw),strict=True)
   for i,page in enumerate(pdf.pages[:2]):
    text=' '.join((page.extract_text() or '').lower().split())
    for term in (['july 14th, 2026','january 5th, 2025','2025 annual audit','42 flock cameras','299 agencies','twenty-nine (29) searches','ncric','46','51']):
     if term in text:print('REVIEWED_ANCHOR',key,i+1,term)
   good+=1
  except Exception as ex:print('HELD',key,type(ex).__name__,str(ex)[:120])
 print('ORIGINAL_COUNT',good,'of',len(DOCUMENTS),'NO_FACTS_AUTOPUBLISHED')
if __name__=='__main__':main()
