#!/usr/bin/env python3
"""Verify precise source pages of an archived independent historical audit."""
import hashlib,io,json,re
from pathlib import Path
from pypdf import PdfReader
from inspect_robbinsdale_external_flock_audit import URL
from inspect_robbinsdale_external_flock_audit import inspect as inspect_original
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data"/"verified-robbinsdale-2025-independent-flock-audit.json"
SHA="5374d507c1853a37df377cfab5068a24f36df04935b0fd5d66c79a9e3740c010"
ANCHORS={
 2:("two active stationary flock alpr units","default 30-day retention period"),
 3:("inter-agency requests","requesting party and case number"),
 4:("sample reports from the past two months","biennial public accountability audit"),
 5:("conducted and attested","senior auditor")}
def verified(fetcher):
 d=json.loads(LEDGER.read_text(encoding="utf8"))
 if (d["source_url"]!=URL or d["sha256"]!=SHA or d["page_count"]!=5 or
     d["source_date"]!="2025-10-23" or d["audit_period_end"]!="2025-09-30" or
     d["pages_reviewed"]!=[2,3,4,5] or
     d["current_operating_equipment_verified"] is not False or
     d["live_directed_sharing_edges_verified"]!=0 or
     d["exact_camera_coordinates_added"]!=0):
  raise ValueError("Independent original source ledger invalid")
 raw=fetcher()
 if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("State archived external original hash drift")
 pdf=PdfReader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or len(pdf.pages)!=5:raise ValueError("Auditor original pagination changed")
 for page,words in ANCHORS.items():
  s=" ".join((pdf.pages[page-1].extract_text() or "").casefold().split())
  for word in words:
   if word not in s:raise ValueError("Audit original page anchor changed")
 return {"independent_source_original_pages_verified":4,"historical_audit_date":"2025-10-23",
  "source_sha256":SHA,"new_current_camera_positions":0}
if __name__=="__main__":
 from inspect_robbinsdale_external_flock_audit import urllib,PdfReader,io
 def get():
  req=urllib.request.Request(URL,headers={"Accept":"application/pdf"})
  with urllib.request.urlopen(req,timeout=24) as f:
   return f.read(2_000_001)
 print("ROBBINSDALE_EXTERNAL_AUDIT",json.dumps(verified(get)))
