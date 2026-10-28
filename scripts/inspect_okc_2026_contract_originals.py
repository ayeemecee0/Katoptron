#!/usr/bin/env python3
"""Read-only exact government original contract documents for OKC's 2026 renewal.

The city's own publication distinguishes a staff memorandum, a proposed
contract amendment, an approved renewal letter and an encumbering funds
certificate. PDF availability and content are checked separately; metadata
does not silently assert signatures, actual implementation or camera GPS.
"""
import hashlib,io,json,re,urllib.request
from pypdf import PdfReader

BASE="https://www.okc.gov/files/assets/city/v/1/police/documents/flock/"
SOURCES={
 "okc-2026-flock-council-memo":("flock-council-memo-august-2026.pdf",1_000_000),
 "okc-2026-flock-amendment":("flock-amendment-august-2026.pdf",2_000_000),
 "okc-2026-flock-renewal-letter":("flock-renewal-letter-august-2026.pdf",8_000_000),
 "okc-2026-funds-certificate":("availability-of-funds-certificate-august-2026.pdf",1_000_000),
 "okc-2026-police-presentation":("okcpd-alpr-presentation-august-2026.pdf",2_500_000),
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("original_redirect")
def retrieve(source):
 if source not in SOURCES:raise ValueError("Unknown government original identity")
 file,limit=SOURCES[source];url=BASE+file
 req=urllib.request.Request(url,headers={"Accept":"application/pdf",
  "User-Agent":"Katoptron-OKC-public-original-contract-document-evidence-review/1.0"})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as r:
   if r.status!=200 or r.geturl()!=url:raise ValueError("original_url_changed")
   data=r.read(limit+1)
 except urllib.error.HTTPError:raise ValueError("original_http_error") from None
 if not isinstance(data,bytes) or not 100<len(data)<=limit:raise ValueError("original_too_large_or_empty")
 if not data.startswith(b"%PDF-"):raise ValueError("original_not_pdf")
 return data
def inspect(source,raw):
 if source not in SOURCES or not isinstance(raw,bytes) or len(raw)>SOURCES[source][1] or not raw.startswith(b"%PDF-"):raise ValueError("Untrusted original")
 reader=PdfReader(io.BytesIO(raw),strict=True)
 if reader.is_encrypted or not 1<=len(reader.pages)<=75:raise ValueError("Unreadable original")
 visible=[]
 for i,p in enumerate(reader.pages,1):
  text=" ".join((p.extract_text() or "").split())
  if re.search(r"flock|270,000|federal agency|master services agreement|license plate reader|seven days|7 days|signatures?",text,re.I):
   visible.append({"page":i,"character_count":len(text),
    "original_content_excerpt":text[:min(850,len(text))]})
 return {"source_id":source,"source_url":BASE+SOURCES[source][0],
  "sha256":hashlib.sha256(raw).hexdigest(),"original_bytes":len(raw),
  "page_count":len(reader.pages),"text_page_count":sum(bool((p.extract_text() or "").strip()) for p in reader.pages),
  "sample_original_page_anchors":visible[:5],
  "policy_adopted_verified":False,"signed_agreement_verified":False,
  "current_camera_locations_verified":False}
def run():
 res=[]
 for source in SOURCES:
  try:res.append({**inspect(source,retrieve(source)),"status":"original_document_retrieved_needs_page_review"})
  except Exception as e:res.append({"source_id":source,"source_url":BASE+SOURCES[source][0],
    "status":"held_original_pdf_preflight","error_type":type(e).__name__,
    "error_reason":str(e)[:80],"policy_adopted_verified":False,
    "signed_agreement_verified":False,"current_camera_locations_verified":False})
 return res
if __name__=="__main__":
 results=run()
 for x in results:print("OKC_2026_ORIGINAL_DOCUMENT_PREFLIGHT",json.dumps(x,sort_keys=True))
 print("OKC_2026_ORIGINAL_DOCUMENT_TOTALS",json.dumps({
  "sources":len(results),"retrievable":sum(x["status"].startswith("original_") for x in results),
  "held":sum(x["status"].startswith("held_") for x in results),
  "approved_contracts_inferred":0,"camera_points_inferred":0},sort_keys=True))
