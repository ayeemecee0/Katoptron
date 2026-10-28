#!/usr/bin/env python3
"""Read-only acquisition probe for Apache Junction's actual ALPR ordinance and
adopted-by-reference code chapter, without creating policy-effective claims.

Never trust a mirror or silently turn an agenda attachment into enacted text.
No automatic public finding, location pin, or watch event is produced.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlsplit
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
MAX_BYTES=8_000_000
ORIGINALS={
 "city_clerk_ordinance_1579":
 "https://www.apachejunctionaz.gov/DocumentCenter/View/33565/ORD1579",
 "legistar_agenda_ordinance_1579":
 "https://apachejunction.legistar.com/View.ashx?GUID=19063BC4-C37B-4D4C-AE22-194276761219&ID=15974740&M=F",
 "legistar_adopted_chapter_17_attachment":
 "https://apachejunction.legistar.com/View.ashx?GUID=97D4D861-6CFF-42D3-AC9D-B716D9367148&ID=15953709&M=F",
 "city_published_camera_location_diagram":
 "https://apachejunctionaz.gov/DocumentCenter/View/33429"
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):
  raise ValueError("Publisher redirect held until independently reviewed")
def verified_url(url):
 p=urlsplit(url)
 return p.scheme=="https" and p.hostname in {
  "www.apachejunctionaz.gov","apachejunctionaz.gov","apachejunction.legistar.com"
 } and p.netloc==p.hostname and not p.fragment and not p.username
def fetch(url):
 if not verified_url(url) or url not in ORIGINALS.values():
  raise ValueError("Unknown original government publisher URL")
 opener=urllib.request.build_opener(NoRedirect())
 req=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-Apache-original-review/1.0",
  "Accept":"application/pdf,application/octet-stream"})
 with opener.open(req,timeout=24) as res:
  if res.status!=200 or res.geturl()!=url:
   raise ValueError("Original government URL changed")
  content_type=res.headers.get("Content-Type","").lower()
  data=res.read(MAX_BYTES+1)
 if not 200<len(data)<=MAX_BYTES or not data.startswith(b"%PDF-"):
  raise ValueError("Original is not a bounded PDF")
 return data,content_type
def preview(name,data,mimetype):
 pdf=PdfReader(io.BytesIO(data),strict=True)
 if pdf.is_encrypted or not 1<=len(pdf.pages)<=80:
  raise ValueError("Government original is encrypted or too large to review")
 pages=[]
 for i,page in enumerate(pdf.pages):
  text=" ".join((page.extract_text() or "").split())
  # Mask public contact identifiers; do not dump entire PDFs.
  text=re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}","[redacted]",text,flags=re.I)
  text=re.sub(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b","[redacted]",text)
  text=text[:1600] if name!="city_published_camera_location_diagram" else text[:300]
  pages.append({
   "page":i+1,"extractable_text_characters":len(text),
   "has_images":bool(page.images),
   "excerpt":text
  })
 return {"status":"retrieved_original_requires_individual_page_review",
  "source_url":ORIGINALS[name],
  "content_type":mimetype,
  "original_sha256":hashlib.sha256(data).hexdigest(),
  "pages":len(pdf.pages),"bytes":len(data),
  "page_previews":pages,
  "verified_adoption_or_effective_date":False,
  "new_camera_coordinates_published":0}
def investigate(fetcher=fetch):
 records={}
 for name,url in ORIGINALS.items():
  try:
   payload,mimetype=fetcher(url)
   records[name]=preview(name,payload,mimetype)
  except Exception as exc:
   records[name]={"status":"held_source_unavailable_or_unreviewed",
     "source_url":url,"hold_type":type(exc).__name__,
     "verified_adoption_or_effective_date":False,
     "new_camera_coordinates_published":0}
 return {"schema_version":1,
   "scope":"read_only_original_pdf_acquisition_and_individual_page_review_queue",
   "records":records,
   "automatically_verified_ordinance_text":0,
   "automatically_verified_effective_dates":0,
   "automatically_published_camera_coordinates":0}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--out",type=Path,default=ROOT/"apache-junction-original-review-queue.json")
 args=parser.parse_args()
 out=investigate()
 path=args.out.resolve()
 if not path.is_relative_to(ROOT):
  raise ValueError("Unsafe output location")
 path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 for name,row in out["records"].items():
  print("APACHE_JUNCTION_ORIGINAL",name,row["status"],
   "sha",row.get("original_sha256","HELD"),
   "pages",row.get("pages",0),"hold",row.get("hold_type",""))
  for page in row.get("page_previews",[]):
   if page["extractable_text_characters"]:
    print("PAGE_REVIEW_CANDIDATE",name,page["page"],
     json.dumps(page["excerpt"][:800],ensure_ascii=False))
 print("PUBLISHED_ORIGINAL_FACTS 0; EFFECTIVE_DATES 0; CAMERA_COORDINATES 0")
if __name__=="__main__":main()
