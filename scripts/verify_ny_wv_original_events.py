#!/usr/bin/env python3
"""Verify first-party NY historical Flock disclosures and WV legislative hearing.

An original county program status in 2025 is NOT present-day status after
its April 2026 termination decision. A West Virginia hearing is NOT a law or
proof of agency deployment. Never publishes plate records or camera points.
"""
import hashlib,json,re
from pathlib import Path
from preflight_ny_wv_original_flock_records import SOURCES,retrieve,inspect
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"verified-ny-wv-original-flock-events.json"
EXPECTED={
"ny-tompkins-sheriff-july2025-flock-disclosure":("ny-tompkins-sheriff-july2025-report",
 "agency_authored_historical_flock_use_and_sharing_policy_self_report",
 "2025_government_original_page_7_flock_use_no_live_status","2025-07-31","a44d7a11f61c62508936cbc43ff1233cad2849929e81afd482046e6f47f94988",1162207),
"ny-tompkins-county-april2026-termination-resolution":("ny-tompkins-april2026-termination",
 "county_legislature_approved_flock_contract_termination_resolution",
 "approved_12_to_1_termination_decision_actual_deactivation_not_independently_proven",
 "2026-04-14","ed1d19e3f788785ea3da740340e4309693aa0aced711b6f4ae79ef86d9c590e1",139111),
"wv-joint-government-organization-flock-agenda-2026":("wv-august2026-official-agenda",
 "official_proposed_public_hearing_agenda","meeting_agenda_not_enacted_flock_regulation",
 "2026-08-09","c013382be5fec14882c056e0316246fae5615519fd3983666b273cf9b2d5fec3",30028),
"wv-joint-government-organization-august2026-hearing-report":("wv-august2026-legislature-flock-hearing",
 "state_legislature_retrospective_public_hearing_report",
 "committee_discussion_reported_no_enacted_bill_or_deployment_inferred",
 "2026-08-10","b95e81371586fe272ed4d77b1e99712a2210ed47533ce17f23d75959ddf88e57",244510)}
PDF_PAGE_SHA="c6ff5f1eb968dcad8ae4e602ec41b7229ad8074fba38030fd2ab2ff7718c8a2a"
RESTRICTED={"camera_coordinates","operational_camera_count","live_partner_edges",
 "finished_camera_removal_verified","flock_vendor_technical_access_verified","enacted_wv_flock_statute"}
def validate(data):
 if (not isinstance(data,dict) or data.get("schema_version")!=1 or data.get("source_count")!=4 or
  data.get("scope")!="historical_first_party_ny_flock_usage_termination_and_wv_legislative_hearing_not_live_surveillance" or
  not isinstance(data.get("records"),list) or len(data["records"])!=4 or
  "No new camera coordinates" not in data.get("limits","")):
  raise ValueError("Incomplete or unsafe NY/WV original event ledger")
 seen=set()
 for row in data["records"]:
  key=row.get("id")
  if key not in EXPECTED or key in seen:raise ValueError("Unknown or duplicate original government source")
  seen.add(key)
  src,kind,status,date,sha,nbytes=EXPECTED[key]
  original=SOURCES[src]
  if (row.get("state")!=original["state"] or row.get("kind")!=kind or
      row.get("status")!=status or row.get("source_date")!=date or
      row.get("source_type")!=original["type"] or
      row.get("source_url")!=original["source_url"] or
      row.get("content_sha256")!=sha or row.get("original_bytes")!=nbytes or
      not isinstance(row.get("agency"),str) or len(row["agency"])<12 or
      not isinstance(row.get("publisher_role"),str) or
      not isinstance(row.get("findings"),list) or not len(row["findings"])>=1 or
      any(not isinstance(f.get("statement"),str) or not 125<=len(f["statement"])<=750 or
       not isinstance(f.get("kind"),str) for f in row["findings"]) or
      any(k in row for k in RESTRICTED)):
   raise ValueError("Government source status, date, identity or evidence claim altered")
  if original["type"]=="pdf":
   if (row.get("page_count")!=8 or row.get("visually_reviewed_page")!=7 or
    row.get("source_page_png_sha256")!=PDF_PAGE_SHA or
    any(f.get("page")!=7 for f in row["findings"]) or
    "not verified issue date" not in row.get("source_date_note","")):
    raise ValueError("Original NY historical report source/page incorrectly claimed")
  else:
   if any("page" in f for f in row["findings"]):raise ValueError("HTML cannot claim numbered original PDF pages")
 if seen!=set(EXPECTED):raise ValueError("Missing original government source")
 return data["records"]
def verify_sources(records):
 for row in records:
  source=EXPECTED[row["id"]][0]
  raw=retrieve(source)
  observed=inspect(source,raw)
  if row["source_type"]=="pdf":
   if observed["sha256"]!=row["content_sha256"] or observed["bytes"]!=row["original_bytes"] or observed["pages"]!=8:
    raise ValueError("NY July 2025 original government PDF contents changed")
   import fitz
   pdf=fitz.open(stream=raw,filetype="pdf")
   png=pdf[6].get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).tobytes("png")
   if hashlib.sha256(png).hexdigest()!=PDF_PAGE_SHA:raise ValueError("Original NY county Flock report page seven changed")
  else:
   # Government CMS HTML includes navigation/timestamps; unchanged topical
   # anchor content is rechecked even if template wrapper changes.
   if observed["sha256"]!=row["content_sha256"]:
    print("NY_WV_ORIGINAL_GOVERNMENT_HTML_WRAPPER_DRIFT_REVIEW_LEAD",row["id"])
  print("NY_WV_FIRST_PARTY_EVENT_VERIFIED",json.dumps({"id":row["id"],"status":row["status"],
    "sha256_at_original_review":row["content_sha256"],
    "original_pdf_byte_stable":row["source_type"]=="pdf",
    "document_claims_not_current_device_compliance":True},sort_keys=True))
if __name__=="__main__":
 verify_sources(validate(json.loads(DATA.read_text(encoding="utf8"))))
