#!/usr/bin/env python3
"""Reverify SHA-pinned Apache Junction government original PDFs before any
page-specific claims. Distinguish council AGENDA attachments from the
City Clerk's SCANNED adopted ordinance (which remains a visual-review hold).
"""
import hashlib
import io
import json
from pathlib import Path
from pypdf import PdfReader
import inspect_apache_junction_originals as inspector

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data"/"apache-junction-original-chapter-and-map-receipts-2026-10-27.json"
EXPECTED={
 "apache-junction-2026-alpr-chapter-17-legistar-attachment":(
  inspector.ORIGINALS["legistar_adopted_chapter_17_attachment"],
  "ed2411b178181c2bca37e71fcb7c5678ba77f51e7363a6d9f155dc266ac5d724",
  {1:("chapter 17", "17-1-1"),2:("17-1-3",),3:("30 consecutive calendar days","17-1-5","17-1-6")}
 ),
 "apache-junction-2026-ordinance-1579-agenda-unsigned":(
  inspector.ORIGINALS["legistar_agenda_ordinance_1579"],
  "11cbba99aafd376b194c112368988c4073acebbd0726abb218d806b27eb11244",
  {1:("ordinance no. 1579",),2:("adopted", "chapter 17"),3:("passed and adopted","20 ___","mayor")}
 )
}
HELD={
 "id":"apache-junction-clerk-ordinance-1579-scanned",
 "url":inspector.ORIGINALS["city_clerk_ordinance_1579"],
 "sha":"9d4f0ff58b906c65112abd3cf725b00d95e3418a843cd5df0c9e30e9ea9a7e93"
}
def validate_manifest(raw):
 if raw.get("schema_version")!=1 or raw.get("verified_on")!="2026-10-27" or len(raw.get("source_page_reviewed",[]))!=2 or len(raw.get("source_review_held",[]))!=1:
  raise ValueError("Government original receipt record incomplete")
 for doc in raw["source_page_reviewed"]:
  x=EXPECTED.get(doc["id"])
  if not x or doc["source_url"]!=x[0] or doc["pdf_sha256"]!=x[1] or doc["page_count"]!=3 or doc["reviewed_pages"]!=[1,2,3] or doc["effective_date"] is not None or doc["document_date"] is not None:
   raise ValueError("Original city agenda attachment was altered")
  if "not_" not in doc["publication_status"] and "unsigned_" not in doc["publication_status"]:
   raise ValueError("No originally proposed government text may silently become final signed")
 h=raw["source_review_held"][0]
 if h["id"]!=HELD["id"] or h["source_url"]!=HELD["url"] or h["original_sha256"]!=HELD["sha"] or h["page_count"]!=3 or "visual_page_review_pending" not in h["status"]:
  raise ValueError("City Clerk scanned adopted original still requires independent visual comparison")
 return raw
def validate_pdf(doc,raw):
 x=EXPECTED[doc["id"]]
 if hashlib.sha256(raw).hexdigest()!=x[1]:
  raise ValueError("Original government PDF SHA drift")
 pdf=PdfReader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or len(pdf.pages)!=3:
  raise ValueError("Original government PDF pagination changed")
 for page,terms in x[2].items():
  s=" ".join((pdf.pages[page-1].extract_text() or "").lower().split())
  for term in terms:
   if term not in s:
    raise ValueError("Original government page anchor changed: "+doc["id"]+" p"+str(page)+" "+term)
 return len(pdf.pages)
def verify(fetch=inspector.fetch):
 manifest=validate_manifest(json.loads(LEDGER.read_text(encoding="utf8")))
 result={"documents_verified":[], "held_city_clerk_visual_review":True,
  "enacted_chapter_text_verified":False,"exact_camera_gis_points_added":0}
 for doc in manifest["source_page_reviewed"]:
  raw,_=fetch(doc["source_url"])
  count=validate_pdf(doc,raw)
  result["documents_verified"].append({"id":doc["id"],"pages":count,"original_sha256":doc["pdf_sha256"],
   "status":"page_verified_agenda_attachment_NOT_final_enacted_copy"})
 h=manifest["source_review_held"][0]
 payload,_=fetch(h["source_url"])
 if hashlib.sha256(payload).hexdigest()!=HELD["sha"] or len(PdfReader(io.BytesIO(payload),strict=True).pages)!=3:
  raise ValueError("City Clerk original SHA or page count changed; visual review still required")
 return result
def main():
 try:
  result=verify()
  for r in result["documents_verified"]:
   print("APACHE_ORIGINAL_PAGE_ANCHORS_PASS",r["id"],r["original_sha256"])
  print("CITY_CLERK_SCANNED_ORIGINAL_HELD_FOR_VISUAL_REVIEW",result["held_city_clerk_visual_review"])
  print("ENACTED_CHAPTER_TEXT_VERIFIED",result["enacted_chapter_text_verified"])
  print("CAMERA_GIS_POINTS_ADDED",result["exact_camera_gis_points_added"])
 except Exception as exc:
  raise SystemExit("Apache original verification held: "+type(exc).__name__+": "+str(exc)[:160]) from None
if __name__=="__main__":main()
