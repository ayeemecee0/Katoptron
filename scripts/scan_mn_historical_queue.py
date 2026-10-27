#!/usr/bin/env python3
"""Prepare bounded machine receipts for newly discoverable original Minnesota
ALPR audits. No automatic factual promotion and no database writes.

Inputs: original state index + already independently reviewed local JSON.
Output: JSON metadata and SHA/page receipts only, never PDF bytes, snippets,
personal data, plate records, proprietary credentials or compliance verdicts.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess

from import_mn_alpr_audit_registry import fetch_index, index_rows
from fingerprint_mn_flock_audits import fetch_bounded
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
MAX_CANDIDATES=80
MAX_FETCH=12
MAX_PDF_PAGES=20
OUTPUT=ROOT/".katoptron-ci"/"historical-alpr-review-queue.json"

def build(rows,manifest,runner=None):
 payload=json.dumps({"rows":rows,"manifest":manifest},separators=(",",":"))
 if len(payload)>800_000:raise ValueError("Unbounded public-state input")
 if runner is None:
  runner=lambda source:subprocess.run(
   ["node",str(ROOT/"scripts"/"build_mn_historical_queue.cjs")],
   input=source,text=True,capture_output=True,check=True,timeout=25,cwd=ROOT).stdout
 data=json.loads(runner(payload))
 if data.get("schema_version")!=1 or not isinstance(data.get("candidates"),list):
  raise ValueError("Invalid historical source review queue")
 if len(data["candidates"])>MAX_CANDIDATES:raise ValueError("Unbounded historical review queue")
 if any(c.get("examination_status")!="official_registry_metadata_only_pending_independent_pdf_review"
        for c in data["candidates"]):
  raise ValueError("Metadata cannot be promoted into original-source fact by a queue")
 return data

def inspect(candidate,fetcher=fetch_bounded,reader=PdfReader):
 from fingerprint_mn_flock_audits import pdf_url_allowed,MAX_PDF
 url=candidate.get("source_url")
 if not pdf_url_allowed(url):raise ValueError("Non-government source")
 body=fetcher(url)
 if not isinstance(body,bytes) or len(body)<150 or len(body)>MAX_PDF or not body.startswith(b"%PDF-"):
  raise ValueError("Invalid or unbounded original PDF")
 doc=reader(io.BytesIO(body),strict=True)
 if doc.is_encrypted or not 1<=len(doc.pages)<=MAX_PDF_PAGES:
  raise ValueError("Unreadable or unbounded official audit")
 # No PDF text is ever extracted, rendered, persisted or automatically
 # converted into a report about installed ALPR systems.
 return {"source_url":url,"sha256":hashlib.sha256(body).hexdigest(),
         "pages":len(doc.pages),"bytes":len(body),
         "examination_status":"machine_original_receipt_only_no_page_facts"}

def scan(index,manifest,fetcher=fetch_bounded,reader=PdfReader,runner=None):
 queue=build(index,manifest,runner)
 results=[]
 for candidate in queue["candidates"][:MAX_FETCH]:
  try:
   results.append({**inspect(candidate,fetcher,reader),
      "report_id":candidate["report_id"],"priority":candidate["priority"]})
  except Exception as exc:
   results.append({"source_url":candidate["source_url"],
    "report_id":candidate["report_id"],"priority":candidate["priority"],
    "examination_status":"unavailable_needs_recheck",
    "error_type":type(exc).__name__})
 return {"schema_version":1,"scope":"original_state_registry_and_machine_receipts_only",
   "generated_at":dt.datetime.now(dt.timezone.utc).isoformat(),
   "queue":queue,"inspection_limit":MAX_FETCH,
   "machine_receipts":results,
   "independently_published_new_facts":0}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,default=OUTPUT)
 options=p.parse_args()
 rows=index_rows(fetch_index())
 manifest=json.loads((ROOT/"data"/"verified-independent-audits.json").read_text(encoding="utf-8"))
 result=scan(rows,manifest)
 target=options.out.resolve()
 if not target.is_relative_to(ROOT):raise ValueError("Review-queue artifact must remain in repository runner tree")
 target.parent.mkdir(exist_ok=True,parents=True)
 target.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 good=sum(r["examination_status"]=="machine_original_receipt_only_no_page_facts"
          for r in result["machine_receipts"])
 print("OFFICIAL REGISTRY REPORTS",len(rows))
 print("INDEPENDENT ORIGINALS ALREADY CURATED",result["queue"]["curated_reports"])
 print("FLOCK-TITLE PDFS WAITING FOR INDEPENDENT REVIEW",result["queue"]["flock_titles_unreviewed"])
 print("ADDITIONAL EXACT-AGENCY HISTORICAL TITLES",result["queue"]["exact_agency_historical_candidates"])
 print("ORIGINAL PDF MACHINE RECEIPTS",good,"of",len(result["machine_receipts"]))
 print("MACHINE RECEIPT FAILURES",len(result["machine_receipts"])-good,"(unknown availability, not removal)")
 for report in result["machine_receipts"]:
  if report["examination_status"]=="unavailable_needs_recheck":
   print("MACHINE RECEIPT NEEDS RECHECK",report["report_id"],report["error_type"])

 print("QUEUE ARTIFACT",target.relative_to(ROOT))
 print("NEW ORIGINAL-DOCUMENT FACTS AUTOMATICALLY PUBLISHED: 0")

if __name__=="__main__":
 try:main()
 except Exception as exc:
  raise SystemExit("MN historical review scanning held: "+type(exc).__name__+
   (": "+str(exc)[:140] if isinstance(exc,ValueError) else "")) from None
