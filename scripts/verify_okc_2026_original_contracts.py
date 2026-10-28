#!/usr/bin/env python3
"""Verify four page-reviewed original OKC Flock government council documents.

Original PDF bytes and every visually-reviewed page rendering are pinned. Fail
closed if a document changes; a source headline or Council memo cannot alone
upgrade the separate signed amendment, city renewal or funding evidence tier.
"""
import hashlib,json,re
from pathlib import Path
import fitz
from inspect_okc_2026_contract_originals import retrieve,SOURCES
from render_okc_2026_original_contract_review import ORIGINALS

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"verified-okc-2026-original-flock-contract-review.json"
IDENTITY={
"okc-2026-signed-flock-amendment":("okc-2026-flock-amendment",
 "signed_city_and_vendor_amendment_original",[1,2]),
"okc-2026-approved-flock-renewal":("okc-2026-flock-renewal-letter",
 "city_approved_vendor_concurred_renewal_original",[1]),
"okc-2026-council-staff-memo":("okc-2026-flock-council-memo",
 "original_staff_recommendation_not_vote_record",[1,2]),
"okc-2026-city-funds-certificate":("okc-2026-funds-certificate",
 "signed_availability_of_funds_certification_not_payment",[1])
}
EXPECTED_PNGS={
"okc-2026-signed-flock-amendment":{1:"56acb662b5a723fa42e231f882ff4dd88fe51ce5983018ad1c02d233fccab558",2:"aa3fa98c6f4d32528700484e8a48716dd0bc15853ac70749e598e8a2a8172e30"},
"okc-2026-approved-flock-renewal":{1:"b7b545b579de545bcd26010c9c8fb6499a8db01f4a709f29ac34465f261ee032"},
"okc-2026-council-staff-memo":{1:"d96756c761c0c0d9c5ea931d538d6b001714d02f4c2c68ef568ef42cdea4e385",2:"d53a2598bf5cc5b5255efa43f75dd9d4b1d09e8d414019817416e6889d051e46"},
"okc-2026-city-funds-certificate":{1:"46616307a268cc99a92d83861efb859000cfb3909a29525e7a463052e7cd2866"}}
TEXT_ANCHORS={
"okc-2026-signed-flock-amendment":{1:["amendment no. 1","federal","flock","agreement"],2:["approved","council","august","city clerk"]},
"okc-2026-approved-flock-renewal":{1:["flock group","renewal","c241032"]},
"okc-2026-council-staff-memo":{1:["flock group","270,000","renewal","c241032"],2:["270,000","police sales tax fund"]},
"okc-2026-city-funds-certificate":{1:["availability of funds certificate","270,000","police sales tax fund"]}
}
DISALLOWED={"verified_camera_coordinates","live_flock_network_access_verified","actual_federal_access_verified",
 "independently_audited_sharing_partners","actual_payment_spend_verified"}
def validate(data):
 if (not isinstance(data,dict) or data.get("schema_version")!=1 or
  data.get("scope")!="visually_reviewed_original_okc_flock_council_contract_documents_no_live_camera_or_sharing_verification" or
  data.get("state")!="OK" or data.get("city")!="Oklahoma City" or
  len(data.get("documents",[]))!=4 or data.get("city_original_program_page")!="https://www.okc.gov/Services/Public-Safety/Police/Flock-Safety-license-plate-reader-LPR-usage-in-Oklahoma-City"):
  raise ValueError("Oklahoma City original source evidence set changed")
 ids=set()
 for r in data["documents"]:
  ident=r.get("id")
  if ident not in IDENTITY or ident in ids:raise ValueError("Unknown or duplicated Oklahoma original")
  ids.add(ident)
  source,expected_kind,pages=IDENTITY[ident]
  url="https://www.okc.gov/files/assets/city/v/1/police/documents/flock/"+SOURCES[source][0]
  sha,npage,rendered=ORIGINALS[source]
  if (r.get("status")!=expected_kind or r.get("source_url")!=url or
   r.get("source_sha256")!=sha or r.get("pages")!=npage or
   r.get("pages_visually_reviewed")!=pages or
   r.get("png_sha256_by_page")!={str(p):EXPECTED_PNGS[ident][p] for p in pages} or
   r.get("event_date")!="2026-08-18" or
   not isinstance(r.get("source_bytes"),int) or not 100<r["source_bytes"]<=SOURCES[source][1] or
   not isinstance(r.get("findings"),list) or not len(r["findings"])>=1 or
   any(not isinstance(f,dict) or f.get("page") not in pages or
    not isinstance(f.get("statement"),str) or not 110<=len(f["statement"])<=700 for f in r["findings"]) or
   any(k in r for k in DISALLOWED)):
   raise ValueError("Original OKC legal or source/page evidence changed")
 if ids!=set(IDENTITY):raise ValueError("Missing original Oklahoma city record")
 report=data.get("city_self_report",{})
 if (report.get("source_kind")!="city_authored_2026_program_webpage_not_external_independent_audit" or
  report.get("city_2026_flock_readers_reported")!=90 or
  report.get("partner_agencies_reported_as_of_2026_08_18")!=109 or
  report.get("reported_default_data_retention_days")!=7 or
  report.get("reported_council_vote_date")!="2026-08-18" or
  report.get("reported_approved_annual_renewal_usd")!=270000 or
  report.get("reported_renewal_through")!="2027-06-30" or
  "not independently measured" not in report.get("interpretation","")):
  raise ValueError("City-reported counts must not become independently audited network facts")
 if (data.get("unreviewed_source_note",{}).get("evidence_status")!="original_machine_inspected_presentation_not_independent_program_verification" or
  data.get("unreviewed_source_note",{}).get("page_count")!=9):
  raise ValueError("Original agency presentation was improperly source-reviewed")
 return data["documents"]
def inspect_bytes(row):
 source,_,pages=IDENTITY[row["id"]]
 b=retrieve(source)
 if len(b)!=row["source_bytes"] or hashlib.sha256(b).hexdigest()!=row["source_sha256"]:
  raise ValueError("Original government PDF byte drift; review before publication")
 pdf=fitz.open(stream=b,filetype="pdf")
 if pdf.page_count!=row["pages"]:raise ValueError("Government original page count drift")
 for p in pages:
  page=pdf[p-1]
  bpng=page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).tobytes("png")
  if hashlib.sha256(bpng).hexdigest()!=EXPECTED_PNGS[row["id"]][p]:
   raise ValueError("Visual source-page changed; review signatures/legal terms")
  text=" ".join((page.get_text() or "").casefold().split())
  missing=[anchor for anchor in TEXT_ANCHORS[row["id"]][p] if anchor.casefold() not in text]
  if missing:
   raise ValueError(f"Legal original page text anchor no longer matches: {row['id']} page={p} missing={missing}")
 return True
def main():
 documents=validate(json.loads(DATA.read_text(encoding="utf8")))
 for row in documents:
  inspect_bytes(row)
  print("OKC_ORIGINAL_PAGE_AND_SIGNATURE_REVIEW_PASS",json.dumps({"id":row["id"],"page_count":row["pages"],
   "reviewed_pages":row["pages_visually_reviewed"],"sha256":row["source_sha256"],
   "status":row["status"],"no_live_equipment_or_payment_inferred":True},sort_keys=True))
if __name__=="__main__":main()
