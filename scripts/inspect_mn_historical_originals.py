#!/usr/bin/env python3
"""Read-only first-pass inspection of every still-unreviewed exact-agency
Minnesota government audit. Never publish source contents automatically."""
import hashlib
import io
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader
from import_mn_alpr_audit_registry import fetch_index,index_rows
from fingerprint_mn_flock_audits import fetch_bounded
from scan_mn_historical_queue import build

ROOT=Path(__file__).resolve().parents[1]
TERM=re.compile(r"\b(?:flock|elsag|axon|vigilant|motorola|genetec|boss|mobile|stationary|squad|patrol|fixed|retention|system|vehicle|reader|sharing)\b",re.I)
def summarize(text):
 text=" ".join(text.split())
 # Only isolated public report passages; bounded and non-authoritative research aids.
 units=re.split(r"(?<=[.!?])\s+(?=[A-Z])",text)
 matches=[u[:440] for u in units if TERM.search(u) and 25<=len(u)<1500]
 return matches[:9]

def run():
 rows=index_rows(fetch_index())
 manifest=json.loads((ROOT/"data/verified-independent-audits.json").read_text(encoding="utf-8"))
 queue=build(rows,manifest)
 print("TOTAL",len(queue["candidates"]),"EXACT_AGENCY",queue["exact_agency_historical_candidates"])
 for r in queue["candidates"]:
  if not r.get("jurisdiction_key"):continue
  print("CANDIDATE",json.dumps({"report_id":r["report_id"],"agency":r["jurisdiction_key"],
    "title":r["report_title"],"url":r["source_url"],"scope":r["title_scope"],
    "publication_date":r["publication_date"],"listed_period":r["coverage_period"]}))
  try:
   data=fetch_bounded(r["source_url"])
   doc=PdfReader(io.BytesIO(data),strict=True)
   if doc.is_encrypted or not 1<=len(doc.pages)<=20:raise ValueError("page_limit")
   print("RECEIPT",r["report_id"],hashlib.sha256(data).hexdigest(),"PAGES",len(doc.pages),"BYTES",len(data))
   for i,page in enumerate(doc.pages[:4]):
    passages=summarize(page.extract_text() or "")
    print("PAGE",r["report_id"],i+1,json.dumps(passages[:7],ensure_ascii=False))
  except Exception as exc:
   print("HELD",r["report_id"],type(exc).__name__,str(exc)[:95])
 print("PUBLIC_FINDINGS_AUTOPUBLISHED 0")

if __name__=="__main__":run()
