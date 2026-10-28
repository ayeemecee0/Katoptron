#!/usr/bin/env python3
"""Read-only original independent Minnesota ALPR audit acquisition.

Separate the 2025 FLOCK audit from the 2026 AXON audit. Document dates,
audit scopes and equipment counts are historical, not today's status.
"""
import hashlib,io,json,urllib.request
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
ORIGINALS={
 "flock_2025":"https://www.lrl.mn.gov/docs/2025/mandated/251675.pdf",
 "axon_2026":"https://www.lrl.mn.gov/docs/2026/mandated/260189.pdf"
}
ANCHORS={
 "flock_2025":{
  1:["2025 alpr audit (flock system)","october 23, 2025"],
  2:["2025 flock alpr audit executive summary","two active stationary flock","no mobile flock","30-day retention"],
  3:["flock backend server application","inter-agency requests"],
  4:["flock alpr system","first alpr audit of the new flock system"],
  5:["minnesota security consortium","dimitrios hilton"]
 },
 "axon_2026":{
  1:["2026 alpr audit (axon system)","january 29, 2026"],
  2:["2026 axon alpr audit executive summary","11 active mobile axon alpr units","30-day retention"],
  3:["axon backend server application"],
  4:["axon alpr system","first alpr audit of the new axon system"],
  5:["minnesota security consortium"]
 }
}
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Original government PDF publisher redirect")
def fetch(label):
 if label not in ORIGINALS:raise ValueError("Original PDF source not allowlisted")
 url=ORIGINALS[label]
 req=urllib.request.Request(url,headers={"Accept":"application/pdf","User-Agent":"Katoptron-original-MN-ALPR-audit-review/1.0"})
 with urllib.request.build_opener(DenyRedirect()).open(req,timeout=28) as response:
  if response.status!=200 or response.geturl()!=url:
   raise ValueError("Government original source changed")
  raw=response.read(5_000_001)
 if not 1000<=len(raw)<=5_000_000 or not raw.startswith(b"%PDF-"):
  raise ValueError("Government audit not a bounded original PDF")
 return raw
def inspect(label,raw):
 if label not in ORIGINALS or not isinstance(raw,bytes) or not raw.startswith(b"%PDF-"):
  raise ValueError("Unknown original")
 reader=PdfReader(io.BytesIO(raw),strict=True)
 if reader.is_encrypted or len(reader.pages)!=5:
  raise ValueError("Historical government audit original page count changed")
 pages=[]
 for p,terms in ANCHORS[label].items():
  text=" ".join((reader.pages[p-1].extract_text() or "").lower().split())
  missing=[term for term in terms if term not in text]
  if missing:raise ValueError("Historical original page anchor missing: "+label+" page "+str(p)+" "+str(missing))
  pages.append(p)
 return {
  "id":label,"source_url":ORIGINALS[label],
  "sha256":hashlib.sha256(raw).hexdigest(),
  "bytes":len(raw),"page_count":5,"anchor_pages":pages,
  "individual_vehicle_data_ingested":False,
  "current_camera_configuration_verified":False,
  "flock_and_axon_separated":True,
  "historic_audit_scope":"flock_nov2023_to_sep2025" if label=="flock_2025" else "axon_jan2024_to_dec2025",
  "public_findings_automatically_published":0
 }
def main():
 results=[]
 for label in ORIGINALS:
  try:
   raw=fetch(label)
   r=inspect(label,raw)
   results.append(r)
   print("ROBBINSDALE_ORIGINAL_ALPR_AUDIT",json.dumps(r,sort_keys=True))
  except Exception as exc:
   results.append({"id":label,"status":"held_source_or_anchor_changed",
    "error_type":type(exc).__name__,"public_findings_automatically_published":0})
   print("HELD_ROBBINSDALE_ORIGINAL",label,type(exc).__name__,str(exc)[:130])
 output=ROOT/".katoptron-ci"/"robbinsdale-original-audit-source-review.json"
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps({"schema_version":1,"reports":results},indent=2)+"\n",encoding="utf8")
 if not all(r.get("sha256") for r in results):
  raise SystemExit("Original audit source held; do not publish new findings")
if __name__=="__main__":main()
