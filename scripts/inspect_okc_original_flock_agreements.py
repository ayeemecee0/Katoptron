#!/usr/bin/env python3
"""Exact original Oklahoma City Flock agreement and council-document preflight.

Metadata and original-document heading fragments only. A city file path is
not an executed contract, enacted ordinance, or verified installed camera.
"""
import hashlib,io,json,re,urllib.parse,urllib.request
from pypdf import PdfReader
ROOT="https://www.okc.gov/files/assets/city/v/1/police/documents/flock/"
DOCS={
 "okc-flock-aug-2026-amendment":("flock-amendment-august-2026.pdf","candidate_contract_amendment"),
 "okc-flock-aug-2026-council-memo":("flock-council-memo-august-2026.pdf","candidate_city_council_staff_memo"),
 "okc-flock-aug-2026-renewal-letter":("flock-renewal-letter-august-2026.pdf","candidate_vendor_or_city_renewal_letter")
}
CAP=8_000_000
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("original_government_source_redirect")
def fetch(uri):
 if not isinstance(uri,str) or uri not in [ROOT+x[0] for x in DOCS.values()]:
  raise ValueError("Oklahoma government source URL must be exact approved original")
 req=urllib.request.Request(uri,headers={"Accept":"application/pdf",
 "User-Agent":"Katoptron-public-original-Oklahoma-contract-preflight/1.0"})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=24) as r:
   if r.status!=200 or r.geturl()!=uri:raise ValueError("changed_government_original")
   b=r.read(CAP+1)
 except urllib.error.HTTPError as e:
  raise ValueError("original_http_error") from None
 if len(b)>CAP:raise ValueError("source_exceeds_limit")
 if not 100<=len(b) or not b.startswith(b"%PDF-"):raise ValueError("original_is_not_pdf")
 return b
def analyze(id,raw):
 if id not in DOCS or not isinstance(raw,bytes) or len(raw)>CAP or not raw.startswith(b"%PDF-"):
  raise ValueError("Unapproved source")
 pdf=PdfReader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or not 1<=len(pdf.pages)<=80:raise ValueError("Original pages outside bounded review")
 textpages=0;terms={}
 for i,page in enumerate(pdf.pages,1):
  s=" ".join((page.extract_text() or "").casefold().split())
  if len(s)>=55:textpages+=1
  for x in ["flock safety","august 2026","city council","renewal","amendment","signature","execute","authorized","order form"]:
   if x in s:terms.setdefault(x,[]).append(i)
 return {"id":id,"publisher":"City of Oklahoma City","source_url":ROOT+DOCS[id][0],
  "review_candidate_type":DOCS[id][1],"original_sha256":hashlib.sha256(raw).hexdigest(),
  "original_bytes":len(raw),"pages":len(pdf.pages),
  "machine_text_pages":textpages,"keyword_page_candidates":terms,
  "source_evidence_tier":"original_pdf_byte_page_receipt_not_contract_execution_or_adoption_verified",
  "verified_executed_or_adopted":False,"current_vendor_operations_verified":False,
  "camera_locations_verified":False}
def main():
 for id,(filename,kind) in DOCS.items():
  try:
   result=analyze(id,fetch(ROOT+filename))
   print("OKC_ORIGINAL_GOVERNMENT_CONTRACT_PREFLIGHT",json.dumps(result,sort_keys=True))
  except Exception as e:
   print("OKC_ORIGINAL_DOCUMENT_HELD",json.dumps({"id":id,"original_url":ROOT+filename,
    "candidate_kind":kind,"status":"held_not_verified","error_type":type(e).__name__,
    "reason":str(e)[:85]},sort_keys=True))
if __name__=="__main__":main()
