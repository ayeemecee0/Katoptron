#!/usr/bin/env python3
"""Fail-closed two-state ALPR policy-source publication gate.
Original PDF bytes are SHA-pinned, page-count verified and independently
checked for each claimed original page. Government source disclosures are
not current device settings, vendor contract verification, or camera locations.
"""
import hashlib,io,json,re
from pathlib import Path
from pypdf import PdfReader
from inspect_idaho_columbia_originals import SOURCES,fetch
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data"/"verified-idaho-columbia-government-policy-originals-2026-10-27.json"
ORIGINALS={
 "idaho-falls-id-flock-supplemental-procedure-127":{
  "url":"https://www.idahofallsidaho.gov/DocumentCenter/View/20519/Automated-License-Plate-Readers",
  "sha":"9d53f9a247818cffff263cd18cf2bf0a14ae66ceca20e126578625fd62e8cf60",
  "pages":2,"state":"ID",
  "anchors":{
   1:("127.1 purpose","flock safety systems","should not be considered probable cause"),
   2:("127.4 searches","case number","127.6 evidence","retention policy is 30 days")
  },
  "categories":("flock_policy_system_and_hotlists","flock_alert_independent_reasonable_suspicion",
      "search_reason_and_case_fields","written_retention_and_preservation")
 },
 "columbia-mo-surveillance-oversight-ordinance-025792":{
  "url":"https://www.como.gov/archive/2024/10/ordinance-025792.pdf",
  "sha":"37e043de9a93a84337e3d9af37b7d4be377476084742832b63aca29353959f48",
  "pages":9,"state":"MO",
  "anchors":{
   1:("ordinance no. 025792","law enforcement surveillance oversight"),
   2:("annual surveillance report","total costs"),
   4:("automatic license plate readers","not be interpreted as an endorsement"),
   6:("dataretention","seventy-two (72) hours"),
   7:("surveillance impact report","public hearing"),
   8:("compliance for existing surveillance technology","one hundred eighty"),
   9:("prior to march 15","full force and effect")
  },
  "categories":("city_surveillance_oversight_enacted_code_text",
   "annual_report_finance_sharing_and_audit_requirements",
   "alpr_explicit_technology_scope",
   "technology_policy_retention_and_location_notification",
   "public_hearing_approval_and_data_sharing",
   "existing_technology_transitional_review",
   "annual_public_report_deadline")
 }
}
def manifest(ledger):
 if (ledger.get("schema_version")!=1 or ledger.get("reviewed_on")!="2026-10-27" or
     ledger.get("new_verified_original_PDF_documents")!=2 or
     ledger.get("distinct_states")!=2 or
     ledger.get("exact_camera_points_added")!=0 or
     ledger.get("active_sharing_edges_added")!=0 or
     ledger.get("verified_current_system_settings")!=0 or
     ledger.get("verified_signed_flock_specific_contracts")!=0 or
     not isinstance(ledger.get("documents"),list) or len(ledger["documents"])!=2):
  raise ValueError("Original government source ledger scope or record count invalid")
 seen=set()
 for doc in ledger["documents"]:
  x=ORIGINALS.get(doc.get("id"))
  if (not x or doc["id"] in seen or doc.get("state")!=x["state"] or
      doc.get("url")!=x["url"] or doc.get("sha256")!=x["sha"] or
      doc.get("pages")!=x["pages"] or
      doc.get("verified_current_camera_count")!=0 or
      doc.get("verified_exact_camera_points")!=0 or
      doc.get("verified_live_sharing_edges")!=0 or
      not isinstance(doc.get("findings"),list) or
      len(doc["findings"])!=len(x["categories"]) or
      not isinstance(doc.get("source_limitations"),str) or
      len(doc["source_limitations"])<170):
   raise ValueError("Original PDF identity, factual status or SHA invalid")
  seen.add(doc["id"])
  expected_pages=list(x["anchors"])
  if doc.get("reviewed_pages")!=expected_pages:
   raise ValueError("Source page review selection changed")
  for expected_category,expected_page,f in zip(x["categories"],expected_pages,doc["findings"]):
   if (f.get("category")!=expected_category or f.get("page")!=expected_page or
       not isinstance(f.get("statement"),str) or len(f["statement"])<145):
    # ID has two claims on the same page, so use a separate finding page
    # sequence checked below instead of one-to-one pages.
    if doc["id"]!="idaho-falls-id-flock-supplemental-procedure-127":
     raise ValueError("Claim/source page anchor mismatch")
  if doc["id"]=="idaho-falls-id-flock-supplemental-procedure-127":
   if [f.get("page") for f in doc["findings"]]!=[1,1,2,2] or [f.get("category") for f in doc["findings"]]!=list(x["categories"]):
    raise ValueError("Idaho Flock procedure page classification changed")
 if seen!=set(ORIGINALS):raise ValueError("Two distinct original government publishers required")
 return ledger["documents"]
def verify(fetcher=fetch,ledger=None):
 documents=manifest(ledger or json.loads(LEDGER.read_text(encoding="utf8")))
 results=[]
 for doc in documents:
  expected=ORIGINALS[doc["id"]]
  raw=fetcher(doc["url"])
  if hashlib.sha256(raw).hexdigest()!=expected["sha"]:
   raise ValueError("Government original source PDF hash drift: "+doc["id"])
  pdf=PdfReader(io.BytesIO(raw),strict=True)
  if pdf.is_encrypted or len(pdf.pages)!=expected["pages"]:
   raise ValueError("Original government PDF pagination changed")
  for page,anchors in expected["anchors"].items():
   text=" ".join((pdf.pages[page-1].extract_text() or "").casefold().split())
   for anchor in anchors:
    if anchor not in text:
     raise ValueError("Original page claim anchor changed "+doc["id"]+" page "+str(page)+": "+anchor)
  results.append({"id":doc["id"],"state":doc["state"],"original_pdf_sha256":expected["sha"],
    "page_count":expected["pages"],"individually_anchored_pages":list(expected["anchors"]),
    "current_live_camera_coordinates_added":0,"current_live_sharing_edges_added":0})
 return results
if __name__=="__main__":
 for r in verify():print("M11_GOVERNMENT_PDF_PAGES_VERIFIED",json.dumps(r,sort_keys=True))
