#!/usr/bin/env python3
"""Source-pinned read-only Apache Junction signed Resolution 26-43 appendix review.

City Clerk published PDF contains signed resolution on pages 1-2, with a
three-page Chapter 17 copy on physical PDF pages 3-5. Those pages were
individually visually reviewed. This is original source text, NOT operational
compliance, camera positions, or an independently established effective date.
"""
import hashlib
import io
import json
import urllib.request
from pypdf import PdfReader

URL='https://www.apachejunctionaz.gov/DocumentCenter/View/33562/RES-26-43'
EXPECTED_SHA=None  # set only after independent original fetch receipt review
MAX_BYTES=8_000_000
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError('government_source_redirect_not_qualified')
def fetch(url=URL):
 if url!=URL:raise ValueError('unapproved_government_source')
 request=urllib.request.Request(url,headers={
  'User-Agent':'Katoptron-Apache-original-resolution-verifier/1.0',
  'Accept':'application/pdf,application/octet-stream'})
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=30) as res:
  if res.status!=200 or res.geturl()!=URL:raise ValueError('original_url_changed')
  b=res.read(MAX_BYTES+1)
 if not isinstance(b,bytes) or not b.startswith(b'%PDF-') or not 500<len(b)<=MAX_BYTES:
  raise ValueError('invalid_bounded_original_pdf')
 return b
def inspect(raw,require_pin=True):
 sha=hashlib.sha256(raw).hexdigest()
 if require_pin and (not EXPECTED_SHA or sha!=EXPECTED_SHA):raise ValueError('original_sha_not_pinned_or_changed')
 pdf=PdfReader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or len(pdf.pages)!=5:raise ValueError('original_page_count_changed_or_encrypted')
 pages=[]
 for i,p in enumerate(pdf.pages,1):
  # Scan metadata is not optical text review; all original pages require source inspection.
  pages.append({'page':i,'has_page_content':p.get_contents() is not None,
   'has_image_or_print_content':bool(p.get('/Resources')),'text_characters':len((p.extract_text() or '').strip())})
 if any(not p['has_page_content'] for p in pages):raise ValueError('missing_original_page_content')
 return {'source_url':URL,'original_sha256':sha,'bytes':len(raw),'pages':5,
   'page_structure':pages,'signed_resolution_pages':[1,2],'attached_chapter_17_pages':[3,4,5],
   'verified_effective_date':False,'verified_live_configuration':False,'new_camera_coordinates':0,
   'receipt_only_not_published_policy_change':True}
def main():
 raw=fetch()
 # A source probe without a pin is only a fingerprint receipt, never publication verification.
 info=inspect(raw,require_pin=bool(EXPECTED_SHA))
 print('APACHE_SIGNED_RESOLUTION_ORIGINAL_RECEIPT',json.dumps(info,sort_keys=True))
 if not EXPECTED_SHA:print('SOURCE_HASH_NEEDS_MANUAL_PIN_BEFORE_CLAIM_PUBLICATION')
 else:print('PINNED_APACHE_RESOLUTION_CHAPTER_ORIGINAL_PASS')
if __name__=='__main__':main()
