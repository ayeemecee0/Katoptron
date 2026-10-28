#!/usr/bin/env python3
"""Page-indexed original public government policy PDFs from new states.

Receipt creation only. Without an exact original SHA and independently selected
page anchors there is no published factual policy status. No plate events,
personal-level records, private database queries, or camera coordinates fetched.
"""
import hashlib,io,json,re,urllib.parse,urllib.request
from pypdf import PdfReader
SOURCES={
 "idaho-falls-id-flock-supplemental-procedure-127":{
  "url":"https://www.idahofallsidaho.gov/DocumentCenter/View/20519/Automated-License-Plate-Readers",
  "state":"ID","pages":2},
 "columbia-mo-surveillance-oversight-ordinance-025792":{
  "url":"https://www.como.gov/archive/2024/10/ordinance-025792.pdf",
  "state":"MO","pages":9}
}
MAX_BYTES=8_000_000
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,request,fp,code,msg,headers,url):
  orig=urllib.parse.urlsplit(request.full_url);dst=urllib.parse.urlsplit(url)
  if dst.scheme!="https" or dst.hostname!=orig.hostname:
   raise ValueError("Source left the original government publisher")
  return super().redirect_request(request,fp,code,msg,headers,url)
def fetch(url):
 if url not in {x["url"] for x in SOURCES.values()}:
  raise ValueError("Unknown original government policy URL")
 req=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-original-governance-policy-page-verification/1.0",
  "Accept":"application/pdf"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=26) as response:
  if response.status!=200:raise ValueError("Original government response unavailable")
  raw=response.read(MAX_BYTES+1)
 if not 100<len(raw)<=MAX_BYTES or not raw.startswith(b"%PDF-"):
  raise ValueError("Original government PDF size or format invalid")
 return raw
def inspect(fetcher=fetch):
 output=[]
 for ident,source in SOURCES.items():
  data=fetcher(source["url"])
  if not 100<len(data)<=MAX_BYTES or not data.startswith(b"%PDF-"):
   raise ValueError("PDF receipt invalid")
  doc=PdfReader(io.BytesIO(data),strict=True)
  if doc.is_encrypted or len(doc.pages)!=source["pages"]:
   raise ValueError("Original city-published document page count changed: "+ident)
  pages=[]
  for index,page in enumerate(doc.pages):
   text=" ".join((page.extract_text() or "").split())
   pages.append({
    "page":index+1,
    "readable_character_count":len(text),
    "review_excerpt":text[:850],
    "page_has_extractable_text":bool(text)
   })
  output.append({
   "id":ident,"original_url":source["url"],
   "source_state":source["state"],
   "source_sha256":hashlib.sha256(data).hexdigest(),
   "page_count":len(doc.pages),"page_receipts":pages,
   "evidence_tier":"government_PDF_original_retrieved_needs_individual_page_claim_qualification",
   "agency_policy_adoption_verified":False,
   "current_operational_platform_verified":False,
   "camera_locations_published":0
  })
 return output
if __name__=="__main__":
 for row in inspect():
  print("M11_PUBLIC_POLICY_ORIGINAL",json.dumps(row,sort_keys=True))
