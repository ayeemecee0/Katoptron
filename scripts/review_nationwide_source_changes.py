#!/usr/bin/env python3
"""Editorial qualification of nationwide government ORIGINAL document changes.

A changed URL hash or an ALPR keyword is only a source-review candidate.
A publishable documentary-difference lead requires two original document
versions, numbered page anchors, an individual editorial determination
and a source-pinned before/after claim. No automated legal/adoption conclusions.
"""
import argparse,datetime as dt,json,re
from pathlib import Path
from urllib.parse import urlsplit
import watch_nationwide_government_originals as monitor

ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/".katoptron-ci/nationwide-monitor-snapshot.json"
APPROVALS=ROOT/"data/nationwide-original-document-difference-approvals.json"
OUT=ROOT/".katoptron-ci/nationwide-documentary-difference-review.json"
PUBLIC=ROOT/".katoptron-ci/nationwide-approved-documentary-differences.json"
SHA=re.compile(r"^[a-f0-9]{64}$")
TYPES={"contract_text_difference","retention_policy_text_difference",
 "access_or_sharing_text_difference","council_decision_documentary_difference",
 "government_procurement_documentary_difference"}

def original_page(value):
 try:
  p=urlsplit(value)
  return bool(p.scheme=="https" and (p.hostname or "").endswith(".gov") and
   not p.username and not p.password and not p.fragment and not p.port and len(p.path)>1)
 except ValueError:return False

def review(snapshot,approval):
 if snapshot.get("schema_version")!=2 or not isinstance(snapshot.get("receipts"),list):
  raise ValueError("Validated national source fingerprint snapshot required")
 rows=snapshot["receipts"]
 index={r.get("source_id"):r for r in rows}
 if len(index)!=len(rows):raise ValueError("Duplicate original publisher")
 candidates=[]
 for s in rows:
  if s.get("change")!="source_bytes_changed_review_required":continue
  if not SHA.fullmatch(str(s.get("previous_usable_sha256",""))) or not SHA.fullmatch(str(s.get("current_observation_sha256",""))) or s["previous_usable_sha256"]==s["current_observation_sha256"]:
   raise ValueError("Before and after original publisher fingerprints required")
  candidates.append({"source_id":s["source_id"],"state":s["state"],
   "government_source_url":s["source_url"],
   "before_sha256":s["previous_usable_sha256"],
   "after_sha256":s["current_observation_sha256"],
   "reason":"original_government_page_bytes_changed_no_fact_yet",
   "review_needed":["Acquire publisher-authentic before and after original documents",
      "Locate exact page anchors and publisher dates",
      "Check adopted versus proposed versus terminated status from original action",
      "Confirm material wording difference and unresolved questions"],
   "editorial_status":"held_original_content_review"})
 if not isinstance(approval,dict) or approval.get("schema_version")!=1 or not isinstance(approval.get("approvals"),list):
  raise ValueError("Verified reviewer approval ledger unavailable")
 seen=set();accepted=[]
 for item in approval["approvals"]:
  ident=item.get("source_id")
  if ident in seen:raise ValueError("Duplicate editor approval")
  seen.add(ident)
  row=index.get(ident)
  if not row or row.get("change")!="source_bytes_changed_review_required":
   raise ValueError("Editorial approval has no detected original content difference")
  if (item.get("before_sha256")!=row.get("previous_usable_sha256") or
      item.get("after_sha256")!=row.get("current_observation_sha256")):
   raise ValueError("Editorial citation does not match monitored before/after hashes")
  if not original_page(item.get("before_original_url")) or not original_page(item.get("after_original_url")):
   raise ValueError("Two government originals required")
  if item["before_original_url"]==item["after_original_url"]:
   raise ValueError("Permanent separately retrievable version originals required")
  if (not isinstance(item.get("before_pdf_page"),int) or not 1<=item["before_pdf_page"]<=500 or
      not isinstance(item.get("after_pdf_page"),int) or not 1<=item["after_pdf_page"]<=500):
   raise ValueError("Page-cited original document versions required")
  for field in ["before_excerpt","after_excerpt","reviewer","reviewed_on","government_issuer",
    "legal_status_caveat","why_significant","unverified_questions","title"]:
   v=item.get(field)
   if not isinstance(v,str) or not 15<=len(v)<=1500:
    raise ValueError("Complete original-source claim review is required: "+field)
  if item["before_excerpt"]==item["after_excerpt"] or len(item["unverified_questions"])<30:
   raise ValueError("Material documentary difference not established")
  if not item.get("editorial_approved") is True or item.get("not_proof_of_misconduct") is not True:
   raise ValueError("Human editorial verification and uncertainty safeguards required")
  accepted.append({"id":"approved_docdiff:"+ident+":"+row["current_observation_sha256"][:12],
   "state":row["state"],"source_id":ident,"title":item["title"],
   "evidence_classification":"reviewer_confirmed_original_document_wording_difference",
   "before":{"government_url":item["before_original_url"]+"#page="+str(item["before_pdf_page"]),
     "source_quote":item["before_excerpt"],"sha256_of_observed_publisher_page":item["before_sha256"]},
   "after":{"government_url":item["after_original_url"]+"#page="+str(item["after_pdf_page"]),
     "source_quote":item["after_excerpt"],"sha256_of_observed_publisher_page":item["after_sha256"]},
   "why_it_may_matter":item["why_significant"],"what_remains_unknown":item["unverified_questions"],
   "legal_status_caveat":item["legal_status_caveat"],
   "reviewed_on":item["reviewed_on"],"editorial_status":"approved_documentary_difference_only",
   "automatically_approved_wrongdoing":False,"current_camera_operation_verified":False})
 return {"schema_version":1,"observed_on":snapshot.get("observed_on"),
   "changed_publisher_pages":len(candidates),"publisher_hash_changes_pending_editorial_review":candidates,
   "approved_original_document_differences":len(accepted),
   "unreviewed_claims_automatically_published":0,
   "limitations":"Hash changes alone do not prove contract, policy, access or camera changes. Approval requires two original signed/page-cited versions and authenticated editorial review."},accepted

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--snapshot",type=Path,default=SNAP)
 parser.add_argument("--approvals",type=Path,default=APPROVALS)
 parser.add_argument("--review-output",type=Path,default=OUT)
 parser.add_argument("--approved-output",type=Path,default=PUBLIC)
 a=parser.parse_args()
 result,accepted=review(json.loads(a.snapshot.read_text()),json.loads(a.approvals.read_text()))
 for path,output in [(a.review_output,result),(a.approved_output,{
   "schema_version":1,"observed_on":result["observed_on"],
   "reviewed_original_document_differences":accepted,
   "automatically_published_watch_events":0})]:
  dest=path.resolve()
  if not dest.is_relative_to(ROOT):raise ValueError("Unsafe artifact destination")
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(json.dumps(output,indent=2)+"\n",encoding="utf8")
 print("NATIONWIDE_EDITORIAL_DOCUMENT_DIFFS",json.dumps({
  "changed_publisher_pages":result["changed_publisher_pages"],
  "approved_original_document_differences":len(accepted),
  "automatically_published_watch_events":0},sort_keys=True))
if __name__=="__main__":main()
