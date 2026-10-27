#!/usr/bin/env python3
"""Strict, read-only review of nine AGO-pinned policy PDFs mentioning Flock Safety.

Only publicly published policy documents, only exact versioned links in the
original WA AGO registration and original 71-source receipt. No plate reads,
private-person information or entire policy text. Source-content preview is
review input, NOT automatic publication or installed-camera proof.
"""
import hashlib,io,json,re,urllib.request
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
REG=json.loads((ROOT/"data"/"wa-original-agency-alpr-registrations.json").read_text(encoding="utf8"))
INS=json.loads((ROOT/"data"/"wa-ago-original-policy-source-inspection.json").read_text(encoding="utf8"))
NAMES=("Arlington Police Department","Des Moines Police Department",
 "Federal Way Police Department","Mukilteo Police Department",
 "Prosser Police Department","Sedro-Woolley Police Department",
 "Sultan Police Department","Walla Walla Police Department",
 "Whitman County Sheriff's Office")
assert REG["source_url"]=="https://www.atg.wa.gov/ALPR"
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Unreviewed redirect")
def fetch(url):
 assert url.startswith("https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/")
 assert url.count("VersionId=")==1 and len(url)<=950
 req=urllib.request.Request(url,headers={"User-Agent":"Katoptron-public-government-source-policy-page-review/1.0","Accept":"application/pdf"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as response:
  if response.status!=200 or response.geturl()!=url:raise ValueError("Original government-linked URL changed")
  raw=response.read(8_000_001)
 assert 100<len(raw)<=8_000_000 and raw.startswith(b"%PDF-")
 return raw
def safe_preview(t,maxchars=1850):
 t=" ".join(t.split())
 t=re.sub(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b","[contact withheld]",t)
 t=re.sub(r"(?i)(?:\+1\s?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}","[contact withheld]",t)
 return t[:maxchars]
def main():
 registrations={r["agency_name"]:r for r in REG["registrations"]}
 receipts={r["agency_name"]:r for r in INS["receipts"]}
 for name in NAMES:
  original=registrations[name]
  meta=receipts[name]
  assert meta["inspection_status"]=="exact_pdf_text_detected" and meta["potential_flock_term_pages"]
  url=original["policy_links_from_official_ago_page"][0]
  assert url==meta["policy_source_url"]
  try:
   raw=fetch(url)
   assert hashlib.sha256(raw).hexdigest()==meta["sha256"]
   pdf=PdfReader(io.BytesIO(raw),strict=True)
   assert not pdf.is_encrypted and len(pdf.pages)==meta["page_count"]
   print("POLICY_SOURCE",json.dumps({"agency":name,"sha256":meta["sha256"],"pages":meta["page_count"],"submitted_on":original["submitted_on"],"url":url},ensure_ascii=False))
   print("PAGE_HEADER",name,json.dumps(safe_preview(pdf.pages[0].extract_text() or "",1500),ensure_ascii=False))
   for p in meta["potential_flock_term_pages"]:
    body=" ".join((pdf.pages[p-1].extract_text() or "").split())
    matches=list(re.finditer(r"(?i)flock\s+safety",body))
    assert matches,("Term removed",name,p)
    for m in matches[:3]:
     print("FLOCK_CONTEXT",name,"PAGE",p,json.dumps(safe_preview(body[max(0,m.start()-340):m.end()+800],1140),ensure_ascii=False))
   for word in ["retention","sharing","audit"]:
    pages=[]
    for i,page in enumerate(pdf.pages):
     t=" ".join((page.extract_text() or "").lower().split())
     if word in t:pages.append(i+1)
    print("POLICY_TOPIC_PAGES",name,word,pages[:16])
  except Exception as e: print("HELD_POLICY_SOURCE",name,type(e).__name__,str(e)[:110])
if __name__=="__main__":main()
