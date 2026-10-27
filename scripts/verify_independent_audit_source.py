#!/usr/bin/env python3
"""Source freshness for curated original public independent audit reports.

Never republishes inferred audit conclusions or changes the content-reviewed
manifest; a failed fetch is UNAVAILABLE, not evidence of withdrawal, and must
be independently resolved. No private documents, account identifiers, or
ALPR records are retrieved.
"""
import io
import hashlib
import json
import re
import socket
import urllib.parse
import urllib.request
from pathlib import Path

MAX_BYTES=3*1024*1024
MAX_PAGES=30
AUDIT_HOSTS={"www.lrl.mn.gov"}
MANIFEST=Path(__file__).resolve().parents[1]/"data"/"verified-independent-audits.json"

class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):
  raise ValueError("Government audit moved; new source must be independently verified")

def allowed(url):
 if not isinstance(url,str) or len(url)>1500:return False
 try:
  u=urllib.parse.urlsplit(url)
  return u.scheme=="https" and u.netloc==u.hostname and u.hostname in AUDIT_HOSTS and (
   u.port is None) and not u.fragment and not u.username and not u.password and (
    u.path.startswith("/docs/") and u.path.endswith(".pdf")) and not u.query and not any(
     x in (".","..") for x in u.path.split("/"))
 except (TypeError,ValueError,AttributeError):
  return False

def manifest_rows(source):
 if not isinstance(source,dict) or source.get("schema_version")!=1:
  raise ValueError("Invalid source audit manifest")
 rows=source.get("reports")
 if not isinstance(rows,list) or len(rows)>25:raise ValueError("Unbounded original audit catalog")
 ids=set()
 for row in rows:
  if not isinstance(row,dict) or not allowed(row.get("source_url")):
   raise ValueError("Original government audit provenance invalid")
  key=row.get("id")
  if not isinstance(key,str) or not re.fullmatch(r"[a-z0-9-]{5,120}",key) or key in ids:
   raise ValueError("Duplicate or invalid audit ID")
  ids.add(key)
  if not isinstance(row.get("content_sha256"),str) or not re.fullmatch(r"[0-9a-f]{64}",row["content_sha256"]):
   raise ValueError("Verified source requires a pinned PDF digest")
  if not isinstance(row.get("findings"),list) or not row["findings"] or len(row["findings"])>25:
   raise ValueError("Invalid bounded original claims")
  if not all(isinstance(f,dict) and isinstance(f.get("page"),int) and
             f["page"] in row.get("pages_reviewed",[]) and
             isinstance(f.get("statement"),str) and 40<=len(f["statement"])<850
             for f in row["findings"]):
   raise ValueError("Unverified page references")
 return rows

def get_pdf(url,fetcher=None):
 if not allowed(url):raise ValueError("Unapproved source URL")
 if fetcher is not None:return fetcher(url)
 req=urllib.request.Request(url,headers={"Accept":"application/pdf","User-Agent":"Katoptron-PublicAudits/1.0"})
 opener=urllib.request.build_opener(DenyRedirect())
 with opener.open(req,timeout=15) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Original audit source unavailable or redirected")
  body=res.read(MAX_BYTES+1)
 if len(body)>MAX_BYTES or not body.startswith(b"%PDF-"):
  raise ValueError("PDF not bounded and readable")
 return body

def verify_pdf(report,payload,reader_class=None):
 if not isinstance(payload,bytes) or len(payload)>MAX_BYTES or not payload.startswith(b"%PDF-"):
  raise ValueError("Invalid original audit PDF bytes")
 if hashlib.sha256(payload).hexdigest()!=report.get("content_sha256"):
  raise ValueError("Original auditor PDF version changed; needs manual independent re-review")
 if reader_class is None:
  from pypdf import PdfReader
  reader_class=PdfReader
 pdf=reader_class(io.BytesIO(payload),strict=True)
 if pdf.is_encrypted or len(pdf.pages)<max(report["pages_reviewed"]) or len(pdf.pages)>MAX_PAGES:
  raise ValueError("Audited page range unavailable or encrypted")
 def normalized(page):
  return " ".join(str(pdf.pages[page-1].extract_text() or "").lower().split())
 if report["id"]=="shakopee-mn-alpr-independent-audit-2026":
  # These four textual anchors are limited to the five original pages
  # manually reviewed Oct 26, 2026. Content changes require renewed review.
  anchors={
   1:("shakopee police department","flock"),
   2:("flock","retention period"),
   4:("authorization to access data","audit"),
   5:("lynn lembcke","june 15, 2026"),
  }
  for page,phrases in anchors.items():
   text=normalized(page)
   if not all(p in text for p in phrases):
    raise ValueError("Original auditor page text differs; held for independent re-review")
 elif report["id"]=="stillwater-mn-independent-flock-alpr-audit-2026":
  anchors={
   2:("stillwater police department","17 stationary flock","default 30-day retention period"),
   3:("sharing among law enforcement agencies","out-of-state sharing","shared network section"),
  }
  for page,phrases in anchors.items():
   content=normalized(page)
   if not all(p in content for p in phrases):
    raise ValueError("Stillwater original auditor PDF page changed; hold for review")
 elif report["id"]=="hennepin-county-mn-independent-flock-alpr-audit-2025":
  anchors={
   2:("hennepin county","4 active stationary flock","default 30-day retention period"),
   3:("sharing among law enforcement agencies","agency command"),
  }
  for page,phrases in anchors.items():
   content=normalized(page)
   if not all(p in content for p in phrases):
    raise ValueError("Hennepin original auditor PDF page changed; hold for review")
 else:
  raise ValueError("New audit requires a scoped independent verifier")
 return len(pdf.pages)

def run():
 records=manifest_rows(json.loads(MANIFEST.read_text(encoding="utf-8")))
 for row in records:
  data=get_pdf(row["source_url"])
  pages=verify_pdf(row,data)
  print("Original independent audit source OK:",row["id"],"pages",pages,
        "SHA256",hashlib.sha256(data).hexdigest(),
        "manual findings retained only at their documented source dates")
 print("SOURCE CHECK PASS: original audit bytes checked; no raw plates, source file or private data retained")
if __name__=="__main__":
 try:run()
 except Exception as exc:
  raise SystemExit("SOURCE CHECK UNAVAILABLE OR DRIFTED: "+type(exc).__name__+": "+str(exc)) from None
