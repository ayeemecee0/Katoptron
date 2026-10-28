#!/usr/bin/env python3
"""Exact original public police ALPR policy review, RI and SD.

Explicit official publisher URLs; no redirect, private data, GPS map pins, or
automatic interpretation of vendor deployment from a generic ALPR policy.
"""
import hashlib,io,json,urllib.request

SOURCES={
 "providence-ri-police-350-05-2026":{
  "source_url":"https://ppd.providenceri.gov/350-05-automated-license-plate-readers-alpr-2/",
  "agency":"Providence Police Department","state":"RI","page_count":10,
  "pages_to_render":[1,7,8,9]},
 "brookings-sd-police-13d1-2026":{
  "source_url":"https://www.cityofbrookings-sd.gov/DocumentCenter/View/20501/Policy-13D1---Automated-License-Plate-Recognition-System",
  "agency":"Brookings Police Department","state":"SD","page_count":6,
  "pages_to_render":[1,5,6]}
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):raise ValueError("source_redirect_to:"+str(newurl)[:240])
def fetch(key):
 if key not in SOURCES:raise ValueError("Unapproved original")
 req=urllib.request.Request(SOURCES[key]["source_url"],headers={
  "User-Agent":"Katoptron-original-government-ALPR-policy-page-inspection/1.0",
  "Accept":"application/pdf"})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as r:
   if r.status!=200 or r.geturl()!=SOURCES[key]["source_url"]:raise ValueError("source_changed")
   raw=r.read(6_000_001)
 except urllib.error.HTTPError:raise ValueError("source_http_error") from None
 if not 200<len(raw)<=6_000_000 or not raw.startswith(b"%PDF-"):raise ValueError("unbounded_or_non_pdf_original")
 return raw
def inspect(key,b):
 import fitz  # Required only for original PDF visual run, not schema-only regressions.
 if key not in SOURCES or not isinstance(b,bytes) or not b.startswith(b"%PDF-"):raise ValueError("Original invalid")
 source=SOURCES[key]
 d=fitz.open(stream=b,filetype="pdf")
 if d.page_count!=source["page_count"] or d.is_encrypted:raise ValueError("Document page count drift")
 receipts=[]
 for i in source["pages_to_render"]:
  p=d[i-1];img=p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).tobytes("png")
  text=" ".join((p.get_text() or "").split())

  receipts.append({"page":i,"page_image_sha256":hashlib.sha256(img).hexdigest(),
   "text_layer_character_count":len(text),
   "contains_explicit_flock_text":"flock safety" in text.casefold(),
   "provisional_text_excerpt":text[:200]})
 return {"id":key,"agency":source["agency"],"state":source["state"],"source_url":source["source_url"],
  "original_sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),
  "pages":d.page_count,"review_page_receipts":receipts,
  "manufacturer_deployment_verified":False,"camera_locations_verified":False,
  "adopted_version_verified":False}
def main():
 for key in SOURCES:
  try:result={**inspect(key,fetch(key)),"status":"original_retrieved_visual_review_candidate"}
  except Exception as exc:result={"id":key,"status":"held_original","error_type":type(exc).__name__,"error_reason":str(exc)}
  print("RI_SD_ORIGINAL_POLICY",json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
