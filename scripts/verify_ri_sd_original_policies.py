#!/usr/bin/env python3
"""Verify exact original police policy PDF bytes and reviewed page render anchors.

Providence's original is a text PDF; Brookings is scanned image-only. Neither
is surveillance telemetry. A changed source fails rather than silently changing
published retention, policy adoption, vendor, sharing or camera claims.
"""
import hashlib,json
from pathlib import Path
from inspect_ri_sd_alpr_original_policies import fetch,SOURCES

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"verified-ri-sd-original-alpr-policies.json"
EXPECTED={
"providence-ri-general-order-35005-sept2026":{
 "source":"providence-ri-police-350-05-2026","sha":"74b04c3c5b3f7c6fba013ea205e23279213efd20247be9039acb8cd8e7716f46","bytes":235578,
 "pages":10,"kind":"department_published_effective_general_order","issued":"2026-09-04","effective":"2026-09-04",
 "image":{1:"1a3debe282cdc8128c473c3cf3ab43c4303f7456cff7cc30d12d46032cf0ede7",7:"31a5a1342b59c5ce87686dce4bae0ee690511794517ccd0aef541e92c4f894c1",8:"05792cd61271a5f02f575d6793212cf950ac482bf55b7e5a1f88e4f41f658cae",9:"f1e3874b5acb4e8329c27f9204734498a256263958ce9443e815ea0f3e068687"}},
"brookings-sd-policy-13d1-revised-sept2026":{
 "source":"brookings-sd-police-13d1-2026","sha":"2c47881c232c5cb46dd110bf687770371982821798bcb47feebbcb5fc3553df2",
 "bytes":330030,"pages":6,"kind":"department_published_chief_signed_policy_revision","issued":"2024-04-24",
 "effective":"2026-09-22","image":{1:"3eea1e1369c28cb9418148e3bdd0fe8576062fbbfb9cea61145c0ab02ce0bf14",5:"1717481cdd2d3ea4fa678153a8f3a937a455c50db907ed5d1e195502862d1c30",6:"c07437fdc865a4f2299978ccb3c8698cf8d8cac2dd160aa8875003eb0b9fcbc5"}}}
ANCHORS={
 1:["350.05","9/4/2026"],
 7:["flock safety","thirty (30) days"],
 8:["transparency portal","quarterly basis"],
 9:["federal immigration enforcement","alpr data"]}
def validate(d):
 if (not isinstance(d,dict) or d.get("schema_version")!=1 or
  d.get("source_count")!=2 or
  d.get("scope")!="two_original_page_reviewed_department_published_policy_versions_not_telemetry_or_external_audits" or
  not isinstance(d.get("documents"),list) or len(d["documents"])!=2 or
  "Neither document independently verifies" not in d.get("limits","")):
  raise ValueError("Original state policy review manifest invalid")
 seen=set()
 for r in d["documents"]:
  ident=r.get("id")
  if ident not in EXPECTED or ident in seen:raise ValueError("Untrusted or duplicate original policy")
  seen.add(ident);exp=EXPECTED[ident];src=SOURCES[exp["source"]]
  if (r.get("source_url")!=src["source_url"] or
   r.get("agency")!=src["agency"] or r.get("state")!=src["state"] or
   r.get("kind")!=exp["kind"] or r.get("original_sha256")!=exp["sha"] or
   r.get("original_bytes")!=exp["bytes"] or r.get("page_count")!=exp["pages"] or
   r.get("source_issue_date")!=exp["issued"] or
   r.get("source_effective_date")!=exp["effective"] or
   r.get("pages_visually_reviewed")!=list(exp["image"]) or
   r.get("original_png_sha256")!={str(k):v for k,v in exp["image"].items()} or
   not isinstance(r.get("official_policies_index"),str) or
   not r["official_policies_index"].startswith("https://") or
   not isinstance(r.get("findings"),list) or len(r["findings"])<3 or
   any(f.get("page") not in exp["image"] or not isinstance(f.get("statement"),str) or
       not 110<len(f["statement"])<=700 for f in r["findings"]) or
   any(k in r for k in ("camera_coordinates","camera_count","actual_data_sharing_verified","independent_audit_completed","live_retention_verified"))):
   raise ValueError("Police policy, effective date or image source evidence changed")
 return d["documents"]
def verify_original(r):
 import fitz
 exp=EXPECTED[r["id"]]
 b=fetch(exp["source"])
 if len(b)!=exp["bytes"] or hashlib.sha256(b).hexdigest()!=exp["sha"]:
  raise ValueError("Original state police policy changed bytes")
 pdf=fitz.open(stream=b,filetype="pdf")
 if pdf.page_count!=exp["pages"]:raise ValueError("Original state police policy page count changed")
 for num,sha in exp["image"].items():
  p=pdf[num-1]
  digest=hashlib.sha256(p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).tobytes("png")).hexdigest()
  if sha!=digest:raise ValueError("Reviewed government policy original page image changed")
  if r["state"]=="RI":
   text=" ".join((p.get_text() or "").casefold().split())
   if any(a not in text for a in ANCHORS[num]):
    raise ValueError(f"Original Providence policy page {num} legal text changed")
  elif (p.get_text() or "").strip():
   raise ValueError("Scanned Brookings policy now has text layer: visually re-review")
 return True
def main():
 for r in validate(json.loads(DATA.read_text(encoding="utf8"))):
  verify_original(r)
  print("ORIGINAL_RI_SD_POLICE_POLICY_VERIFIED",json.dumps({"id":r["id"],"sha256":r["original_sha256"],
    "pages_reviewed":r["pages_visually_reviewed"],"status":r["kind"],"camera_coordinates_inferred":False},sort_keys=True))
if __name__=="__main__":main()
