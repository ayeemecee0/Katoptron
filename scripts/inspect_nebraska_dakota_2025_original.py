#!/usr/bin/env python3
"""Inspect public Nebraska 2025 original aggregate ALPR report without plate data.

Original is government-hosted, one page, and visually reviewed independently.
This script prints field-value structure only for the selected original source;
it never accesses ALPR vehicle-level records, agency user credentials or logs.
"""
import hashlib,io,json,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL="https://ncc.nebraska.gov/sites/default/files/Dakota%20County%20FLOCK%20REPORT%202025%20TO%20STATE.pdf"
CAP=1_500_000
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("unexpected government redirect")
def fetch():
 req=urllib.request.Request(URL,headers={"Accept":"application/pdf","User-Agent":"Katoptron-Nebraska-public-aggregate-source-review/1.0"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as response:
  if response.status!=200 or response.geturl()!=URL:raise ValueError("original government source moved")
  data=response.read(CAP+1)
 if not 500<=len(data)<=CAP or not data.startswith(b"%PDF-"):raise ValueError("Original report not bounded PDF")
 return data
def inspect(raw):
 import fitz
 d=fitz.open(stream=raw,filetype="pdf")
 if d.page_count!=1:raise ValueError("Unexpected state government original page count")
 page=d[0]
 widgets=[]
 for w in page.widgets() or []:
  name=str(w.field_name or "")[:70]
  value=str(w.field_value or "")[:70]
  # Only bounded, public aggregate report field labels/values; never full page
  # body or plate-level data.
  if value and (value.isdecimal() or value in ("NCIC","01/01/2025-12/31/2025") or "DAKOTA" in value.upper()):
   widgets.append({"name":name,"value":value})
 pix=page.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False)
 return {"page_count":1,"sha256":hashlib.sha256(raw).hexdigest(),
  "original_bytes":len(raw),"render_png_sha256":hashlib.sha256(pix.tobytes("png")).hexdigest(),
  "form_widgets":len(list(page.widgets() or [])),"bounded_public_aggregate_form_values":widgets}
def main():
 out=inspect(fetch())
 print("NEBRASKA_DAKOTA_2025_OFFICIAL_AGGREGATE_INSPECTION",json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
