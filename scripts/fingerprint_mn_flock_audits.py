#!/usr/bin/env python3
"""Fingerprint Minnesota's official Flock-title audit PDF set.

All entries are *machine receipt only*. SHA, size, pages and boolean keyword
indicators may enter the PRIVATE queue; no PDF prose, personal data, legal
conclusions, camera coordinates, or verified claims are auto-published.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import re
import urllib.request

from import_mn_alpr_audit_registry import (
 index_rows, fetch_index, normal_pdf_url, NoRedirect, REGISTRY, rest,
)
from pypdf import PdfReader

MAX_PDF=2_500_000
MAX_PAGES=20
MAX_REPORTS=40
MAX_EXTRACTED_CHARS=80_000
TABLE="flock_private_mn_flock_audit_pdf_receipts"
FLAGS={
 "mentions_flock":re.compile(r"\bflock\b",re.I),
 "retention_topic_present":re.compile(r"\bretention\b",re.I),
 "sharing_topic_present":re.compile(r"\bshar(?:e|ed|ing)\b",re.I),
 "auditing_topic_present":re.compile(r"\baudit(?:ing|s)?\b",re.I),
 "access_topic_present":re.compile(r"\baccess control\b",re.I),
}

def pdf_url_allowed(url):
 if not isinstance(url,str):return False
 m=re.fullmatch(r"https://www\.lrl\.mn\.gov/docs/(20[0-9]{2})/mandated/([0-9]{6})\.pdf",url)
 return bool(m) and m.group(1)[-2:]==m.group(2)[:2]

def fetch_bounded(url, opener=None):
 if not pdf_url_allowed(url):raise ValueError("Government archive PDF not allowed")
 request=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-original-independent-audit-fingerprint/1.0",
  "Accept":"application/pdf"})
 client=opener or urllib.request.build_opener(NoRedirect())
 with client.open(request,timeout=20) as response:
  if response.status!=200 or response.geturl()!=url:
   raise ValueError("Changed/redirected original state government report")
  if "pdf" not in response.headers.get("Content-Type","").lower():
   raise ValueError("Original archive did not return PDF content type")
  payload=response.read(MAX_PDF+1)
 if len(payload)>MAX_PDF:raise ValueError("Original archive PDF exceeds size limit")
 return payload

def receipt(archive_row,payload,reader=PdfReader):
 if archive_row.get("title_scope")!="flock_named_in_title" or not pdf_url_allowed(archive_row.get("source_url")):
  raise ValueError("Not a state-listed Flock-name audit")
 if not isinstance(payload,bytes) or len(payload)<150 or len(payload)>MAX_PDF or not payload.startswith(b"%PDF-"):
  raise ValueError("PDF bytes invalid or unbounded")
 doc=reader(io.BytesIO(payload),strict=True)
 if doc.is_encrypted or not 1<=len(doc.pages)<=MAX_PAGES:
  raise ValueError("Encrypted or unbounded report pages")
 pieces=[]
 for p in doc.pages:
  piece=p.extract_text() or ""
  if not isinstance(piece,str):raise ValueError("Original PDF text unavailable")
  pieces.append(piece[:MAX_EXTRACTED_CHARS//MAX_PAGES])
 text=" ".join(pieces)[:MAX_EXTRACTED_CHARS]
 flags={key:bool(rex.search(text)) for key,rex in FLAGS.items()}
 flags["machine_text_readable"]=bool(text.strip())
 return {
  "source_url":archive_row["source_url"],
  "source_sha256":hashlib.sha256(payload).hexdigest(),
  "file_bytes":len(payload),"pages":len(doc.pages),
  "state_archive_title":archive_row["report_title"],
  "machine_flags":flags,
  "examination_status":"machine_receipt_only_needs_independent_review",
 }

def pick(rows):
 candidates=[r for r in rows if r.get("title_scope")=="flock_named_in_title"]
 if not 1<=len(candidates)<=MAX_REPORTS:
  raise ValueError("Unbounded or empty Flock-titled report candidate set")
 if len(set(r["source_url"] for r in candidates))!=len(candidates):
  raise ValueError("Duplicate state archive source")
 return candidates

def observe(rows,fetcher=fetch_bounded,reader=PdfReader):
 result=[];failed=[]
 for row in pick(rows):
  try:result.append(receipt(row,fetcher(row["source_url"]),reader))
  except Exception as exc:failed.append((row["report_id"],type(exc).__name__))
 if failed:
  # Atomic scan: network/unreadable/altered source fails closed. NO partial
  # public review and NO authoritative assertion that its source was withdrawn.
  raise ValueError("One or more original PDFs held; no data written: "+repr(failed[:20]))
 return result

def save(receipts,api,key):
 if not api.startswith("https://") or not key:
  raise ValueError("Private source receipt service credential missing")
 stamp=dt.datetime.now(dt.timezone.utc).isoformat()
 for i in range(0,len(receipts),50):
  batch=[{**r,"last_observed_at":stamp} for r in receipts[i:i+50]]
  rest(api,key,TABLE,method="POST",params={"on_conflict":"source_url"},body=batch,
       prefer="resolution=merge-duplicates,return=minimal")

def run(preflight):
 import os
 rows=index_rows(fetch_index())
 receipts=observe(rows)
 print("Original Flock-name archive reports fingerprinted:",len(receipts))
 for r in receipts:
  print("RECEIPT",r["source_url"].split("/")[-1],"sha256="+r["source_sha256"],
        "pages="+str(r["pages"]),"bytes="+str(r["file_bytes"]),
        "text_readable="+str(r["machine_flags"]["machine_text_readable"]))
 if preflight:
  print("DRY RUN: 0 database writes, 0 independently reviewed claims")
  return
 save(receipts,os.environ.get("SUPABASE_URL",""),
       os.environ.get("SUPABASE_SERVICE_ROLE_KEY",""))
 print("PRIVATE MACHINE RECEIPTS SAVED; 0 claims promoted or published")

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--preflight",action="store_true",
                help="No database writes; hashes/page counts displayed as public-source provenance")
 args=p.parse_args()
 try:run(args.preflight)
 except Exception as e:
  raise SystemExit("Official Minnesota audit fingerprinting held: "+
     type(e).__name__+": "+str(e)[:450]) from None
