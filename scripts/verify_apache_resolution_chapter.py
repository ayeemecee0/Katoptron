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
EXPECTED_SHA='8173fcdc45105478522251a8a5d745ca4145767d438d4de91d4811e50907fc5a'
MAX_BYTES=8_000_000
from pathlib import Path
META=Path(__file__).resolve().parents[1]/'data'/'apache-junction-adopted-resolution-chapter-2026-10-28.json'
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
def validate_review_manifest(meta):
 if (meta.get('schema_version')!=1 or meta.get('source_url')!=URL or
     meta.get('original_sha256')!=EXPECTED_SHA or meta.get('original_bytes')!=119905 or
     meta.get('original_pdf_pages')!=5 or
     meta.get('signed_resolution_pages')!=[1,2] or
     meta.get('chapter_17_attachment_pages')!=[3,4,5] or
     meta.get('signed_resolution_adoption_date')!='2026-10-06' or
     meta.get('notices_table_resolution_date')!='2026-10-08' or
     meta.get('notices_date_agrees_with_signed_resolution') is not False or
     meta.get('legal_effective_date_verified') is not False or
     meta.get('original_council_agenda_appendix_exact_match_verified') is not False or
     meta.get('independent_operational_compliance_verified') is not False or
     meta.get('exact_camera_points_added')!=0 or
     not isinstance(meta.get('findings'),list) or
     {f.get('page') for f in meta['findings']}!={1,2,3,4,5} or
     not all(isinstance(f.get('statement'),str) and len(f['statement'])>=125 for f in meta['findings']) or
     'not yet been independently matched' not in meta.get('limitations','')):
  raise ValueError('Signed resolution page, date, comparison, or legal claims ungrounded')
 return meta

def main():
 meta=validate_review_manifest(json.loads(META.read_text(encoding='utf8')))
 raw=fetch()
 # A source probe without a pin is only a fingerprint receipt, never publication verification.
 info=inspect(raw,require_pin=True)
 if info['bytes']!=meta['original_bytes'] or info['original_sha256']!=meta['original_sha256']:
  raise ValueError('Source bytes no longer match reviewed manifest')
 print('APACHE_SIGNED_RESOLUTION_ORIGINAL_RECEIPT',json.dumps(info,sort_keys=True))
 print('PINNED_APACHE_RESOLUTION_CHAPTER_ORIGINAL_PASS')
if __name__=='__main__':main()
