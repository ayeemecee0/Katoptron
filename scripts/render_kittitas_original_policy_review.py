#!/usr/bin/env python3
"""Render only the four already-pinned Kittitas AGO policy scan pages for review.

No policy finding is automatically verified or published. OCR (when installed)
is candidate keyword indexing only; extracted personal details are not logged.
"""
import hashlib,io,json,os,re,subprocess,urllib.request
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data"/"wa-held-original-policy-diagnostics.json"
REGISTRY=ROOT/"data"/"wa-original-agency-alpr-registrations.json"
OUT=ROOT/".katoptron-ci"/"kittitas-original-page-review"
EXPECTED_SHA="8b6bb93e69589f7459cb4bc5adbd7991043e59687fa1b91180c149e5fc19368f"
PAGES=4
MAX_BYTES=3_500_000
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Source redirect denied")
def check_source():
 d=json.loads(SOURCE.read_text(encoding="utf8"))
 entry=next(x for x in d["entries"] if x["agency_name"]=="Kittitas Police Department")
 registry=json.loads(REGISTRY.read_text(encoding="utf8"))
 r=next(x for x in registry["registrations"] if x["agency_name"]=="Kittitas Police Department")
 url=entry["source_url"]
 if (not url.startswith("https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/") or
  r["policy_links_from_official_ago_page"]!=[url] or
  entry["sha256_complete_original"]!=EXPECTED_SHA or
  entry["page_count_structurally_readable"]!=PAGES or
  entry["policy_page_content_verified"] is not False):
  raise ValueError("AGO source identity or review boundary changed")
 return url
def fetch(url):
 req=urllib.request.Request(url,headers={"Accept":"application/pdf",
  "User-Agent":"Katoptron-public-AG-original-scanned-policy-review/1.0"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Original state-linked URL moved")
  raw=res.read(MAX_BYTES+1)
 if not 100<len(raw)<=MAX_BYTES or not raw.startswith(b"%PDF-"):
  raise ValueError("Bounded original scan unavailable")
 if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:raise ValueError("Original document hash changed")
 pdf=PdfReader(io.BytesIO(raw),strict=False)
 if pdf.is_encrypted or len(pdf.pages)!=PAGES:raise ValueError("Original page count changed")
 if any((page.extract_text() or "").strip() for page in pdf.pages):
  raise ValueError("Expected scanned original has changed text layer")
 return raw
def render(raw):
 # Use a separate renderer to render the byte-pinned original even though pypdf
 # strict parser cannot recover it. Rendered PNGs are QA artifacts, not facts.
 import fitz
 pdf=fitz.open(stream=raw,filetype="pdf")
 if pdf.page_count!=PAGES:raise ValueError("Independent renderer page count mismatch")
 OUT.mkdir(parents=True,exist_ok=True)
 keywords=["flock","21 day","21-day","retention","audit","access","sharing","immigration","policy","camera"]
 receipts=[]
 for i,page in enumerate(pdf):
  pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False)
  if not 200<=pix.width<=3500 or not 200<=pix.height<=3500:
   raise ValueError("Rendered page outside bounded size")
  dest=OUT/("source-page-%02d.png"%(i+1))
  pix.save(str(dest))
  q={"page":i+1,"width":pix.width,"height":pix.height,
     "png_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
     "rendered":True,"ocr_used":False,"candidate_keyword_flags":[]}
  if os.environ.get("KATOPTRON_OCR_CANDIDATES")=="1":
   result=subprocess.run(["tesseract",str(dest),"stdout","-l","eng","--psm","6"],
    capture_output=True,text=True,timeout=35,check=True)
   corpus=" ".join(result.stdout.casefold().split())
   q["ocr_used"]=True
   q["candidate_keyword_flags"]=[k for k in keywords if k in corpus]
  receipts.append(q)
 return receipts
def main():
 raw=fetch(check_source())
 receipts=render(raw)
 result={"schema_version":1,"original_source_sha256":EXPECTED_SHA,
  "original_pages":PAGES,"extraction_type":"unreviewed_ocr_keyword_candidates_only",
  "agency":"Kittitas Police Department",
  "warning":"Rendered scans and OCR keyword flags are not reviewed policy assertions or verified Flock deployment.",
  "pages":receipts}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"source-review-receipts.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
 print("KITTITAS_IMAGE_ORIGINAL_RENDERED",json.dumps({"source_sha":EXPECTED_SHA,
  "pages":PAGES,"candidate_flags_by_page":[{"page":p["page"],"flags":p["candidate_keyword_flags"]} for p in receipts]},sort_keys=True))
if __name__=="__main__":main()
