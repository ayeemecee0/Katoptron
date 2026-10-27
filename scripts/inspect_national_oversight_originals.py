#!/usr/bin/env python3
"""Original-only government oversight report preflight.

Exact official documents; read-only, no plate records, bulk logs, person-level
facts, private systems, unauthorized cross-host redirects, or fact promotion.
"""
import hashlib, io, json, urllib.parse, urllib.request
from pypdf import PdfReader

ORIGINALS={
 "san-mateo-ca-2026-grand-jury":{
  "state":"CA", "publisher":"San Mateo County Civil Grand Jury",
  "publisher_type":"independent_government_oversight",
  "url":"https://sanmateo.courts.ca.gov/system/files/grand-jury/auto-license-plate-readers-report.pdf",
  "anchors":{1:["is our flock of alpr cameras","2025-2026"],
             2:["automated license plate readers","policy"],
             3:["march 30, 2026","582"]}},
 "austin-tx-2025-city-auditor":{
  "state":"TX","publisher":"City of Austin Office of the City Auditor",
  "publisher_type":"independent_government_oversight",
  "url":"https://services.austintexas.gov/edims/document.cfm?id=452710",
  "anchors":{1:["apd license plate reader","may 2025"],
             2:["city of austin","flock safety"],
             3:["40 fixed cameras","axon"]}},
 "woodburn-or-2026-impact-assessment":{
  "state":"OR","publisher":"City of Woodburn Police Department",
  "publisher_type":"agency_authored_impact_assessment",
  "url":"https://www.woodburn-or.gov/DocumentCenter/View/3298/Flock-Impact-Assessment-FINAL-2-3-26",
  "anchors":{1:["flock safety cameras","impact assessment"],
             7:["november 11, 2025","march 3, 2025"]}},
}
MAX_BYTES=8_000_000
MAX_PAGES=100
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Original publisher redirected; hold for source re-review")

def allowed(key,url):
 source=ORIGINALS.get(key)
 if not source or url!=source["url"]:return False
 p=urllib.parse.urlsplit(url)
 return p.scheme=="https" and p.hostname in {"sanmateo.courts.ca.gov","services.austintexas.gov","www.woodburn-or.gov"} and p.netloc==p.hostname and not p.fragment and not p.username and not p.password

def fetch(key,opener=None):
 source=ORIGINALS[key]; url=source["url"]
 if not allowed(key,url):raise ValueError("Unapproved publisher original")
 opener=opener or urllib.request.build_opener(DenyRedirect())
 req=urllib.request.Request(url,headers={"Accept":"application/pdf","User-Agent":"Katoptron-PublicGovernmentAudits/1.0"})
 with opener.open(req,timeout=30) as r:
  if r.status!=200 or r.geturl()!=url:raise ValueError("Original publisher returned unexpected URL/status")
  raw=r.read(MAX_BYTES+1)
 if len(raw)<100 or len(raw)>MAX_BYTES or not raw.startswith(b"%PDF-"):raise ValueError("Original PDF outside bounded bytes")
 return raw

def inspect(key,raw,reader=PdfReader):
 if not isinstance(raw,bytes) or len(raw)<100 or len(raw)>MAX_BYTES or not raw.startswith(b"%PDF-"):
  raise ValueError("Invalid PDF bytes")
 pdf=reader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or not 1<=len(pdf.pages)<=MAX_PAGES:
  raise ValueError("Encrypted or too many pages")
 issues=[]
 for p,phrases in ORIGINALS[key]["anchors"].items():
  if p>len(pdf.pages):
   issues.append(f"page {p}: missing")
   continue
  text=" ".join((pdf.pages[p-1].extract_text() or "").lower().split())
  missing=[phrase for phrase in phrases if phrase not in text]
  if missing:issues.append(f"page {p}: anchor mismatch "+",".join(missing))
 return {"id":key,"publisher_type":ORIGINALS[key]["publisher_type"],
         "source_url":ORIGINALS[key]["url"],"sha256":hashlib.sha256(raw).hexdigest(),
         "bytes":len(raw),"pages":len(pdf.pages),
         "anchors_match":not bool(issues),"issues":issues[:3]}

def main():
 success=0
 for key in ORIGINALS:
  try:
   record=inspect(key,fetch(key))
   print("ORIGINAL_RECEIPT",json.dumps(record,sort_keys=True))
   success+=1 if record["anchors_match"] else 0
  except Exception as ex:
   print("ORIGINAL_HELD",key,type(ex).__name__,str(ex)[:140])
 print("VERIFIED_ANCHORED_ORIGINALS",success,"of",len(ORIGINALS),"AUTOMATIC_FACT_PUBLICATIONS 0")
if __name__=="__main__":main()
