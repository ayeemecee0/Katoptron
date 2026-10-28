#!/usr/bin/env python3
"""Recheck three AGO-linked ALPR original PDF Flock-word candidates by source hash.
Page excerpts are review leads, not adopted policies or operating deployments.
"""
import hashlib,io,json,re,urllib.request
from pathlib import Path
from pypdf import PdfReader
from acquire_remaining_wa_ag_policy_originals import fetch
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"wa-ago-remaining-original-acquisition-2026-10-27.json"
TARGETS={"Bonney Lake Police Department","Enumclaw Police Department","Sultan Police Department"}
def inspect(fetcher=fetch):
 d=json.loads(DATA.read_text(encoding="utf8"))
 selected=[x for x in d["receipts"] if x["agency"] in TARGETS]
 if len(selected)!=3:raise ValueError("Three distinct original candidate agencies not found")
 out=[]
 for r in selected:
  if not r["flock_keyword_seen_in_sample"] or r["acquisition_status"]!="retrieved_unreviewed_original_pdf":raise ValueError("Missing original acquisition receipt")
  payload=fetcher(r["source_url"])
  if hashlib.sha256(payload).hexdigest()!=r["sha256"]:raise ValueError("Original PDF changed since acquisition; hold")
  pdf=PdfReader(io.BytesIO(payload),strict=True)
  if pdf.is_encrypted or len(pdf.pages)!=r["pdf_pages"]:raise ValueError("Original PDF changed page count")
  pages=[]
  for i,page in enumerate(pdf.pages[:min(4,len(pdf.pages))]):
   text=" ".join((page.extract_text() or "").split())
   # Only a short public policy evidence context around the keyword is displayed;
   # do not log raw full policy text or individual plate records.
   occurrences=list(re.finditer(r"\bflock(?:\s+safety)?\b",text,re.I))
   for m in occurrences[:3]:
    excerpt=text[max(0,m.start()-180):min(len(text),m.end()+260)]
    pages.append({"page":i+1,"keyword_context":excerpt,"source_page_read":True,
      "policy_adopted_verified":False,"deployment_verified":False})
  out.append({"agency":r["agency"],"source_url":r["source_url"],
    "sha256":r["sha256"],"page_count":len(pdf.pages),"candidate_page_contexts":pages,
    "current_flock_deployment_verified":False,
    "legal_adoption_verified":False,"new_camera_coordinates":0})
 return {"schema_version":1,"count":3,"entries":out,
  "scope":"source_sha_page_context_review_not_legal_or_operational_claim"}
if __name__=="__main__":
 d=inspect()
 for record in d["entries"]:
  print("WA_VERIFIED_ORIGINAL_PDF_PAGE_REVIEW_CANDIDATE",json.dumps(record,ensure_ascii=False))
