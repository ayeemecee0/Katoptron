#!/usr/bin/env python3
"""Source-pinned and original-page-visual Nebraska aggregate report verification."""
import hashlib,json
from pathlib import Path
from inspect_nebraska_dakota_2025_original import fetch,inspect,URL
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"verified-nebraska-original-aggregate-reports.json"
EXPECTED_SHA="441961503a77e7838717713448426df07cd59aec4146f92af01830d4e3817eae"
EXPECTED_PNG="02686973bfb2c942e98624048bdee0f9a3d54b241b2af432211c69506495fb27"
METRICS={"ncic_confirmed_matches":43,"ncic_noncorrelated_matches":0,
"manual_plate_numbers_entered":126,"manual_entry_confirmed_matches":19,
"manual_entry_noncorrelated_matches":1}
def validate(d):
 if d.get("schema_version")!=1 or d.get("scope")!="visually_reviewed_agency_authored_original_aggregate_not_independent_audit_or_flock_device_verification" or len(d.get("documents",[]))!=1:
  raise ValueError("Only one independently visually reviewed original government aggregate is approved")
 x=d["documents"][0]
 for k,val in {"id":"ne-dakota-county-sheriff-2025-state-alpr-aggregate",
  "state":"NE","agency_name":"Dakota County Sheriff's Office",
  "publisher":"Nebraska Commission on Law Enforcement and Criminal Justice",
  "source_url":URL,"source_sha256":EXPECTED_SHA,"source_render_png_sha256":EXPECTED_PNG,
  "source_bytes":136060,"page_count":1,"pages_reviewed":[1],
  "report_start":"2025-01-01","report_end":"2025-12-31",
  "original_report_type":"agency_authored_state_filed_alpr_aggregate",
  "verification_method":"original_pdf_sha256_and_original_page_visual_review",
  "vendor_status":"filename_mentions_flock_actual_equipment_manufacturer_not_proven_by_form",
  "metrics":METRICS}.items():
  if x.get(k)!=val:raise ValueError("Original report source, date, manufacturer or aggregate metrics changed")
 if not isinstance(x.get("source_note"),str) or "no raw plate reads" not in x["source_note"]:raise ValueError("Report lacks explicit evidence limitations")
 if any(k in x for k in ("camera_coordinates","installed_camera_count","actual_sharing_network","independent_audit","flock_vendor_verified")):
  raise ValueError("Unverified deployment or compliance claims")
 held=d.get("held_unverified_originals")
 if not isinstance(held,list) or len(held)!=1 or held[0].get("agency_name")!="Buffalo County Sheriff's Office" or held[0].get("can_publish_numeric_findings") is not False or held[0].get("issue")!="source_filename_2025_but_visually_rendered_page_empty_no_numeric_data":
  raise ValueError("Held blank Buffalo report promoted without verified content")
 return x
def verify():
 row=validate(json.loads(DATA.read_text(encoding="utf8")))
 raw=fetch()
 if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:raise ValueError("Original report bytes changed")
 details=inspect(raw)
 if (details["page_count"]!=1 or details["original_bytes"]!=136060 or
  details["render_png_sha256"]!=EXPECTED_PNG):
  raise ValueError("Original visually reviewed source-page rendering changed")
 print("NEBRASKA_DAKOTA_2025_AGGREGATE_ORIGINAL_VERIFIED",json.dumps({
  "source_sha256":EXPECTED_SHA,"page_png_sha256":EXPECTED_PNG,
  "page_count":1,"agency":row["agency_name"],"report_period":"2025",
  "independently_audited":False,"manufacturer_installed":False,
  "individual_plate_data_acquired":False},sort_keys=True))
if __name__=="__main__":verify()
