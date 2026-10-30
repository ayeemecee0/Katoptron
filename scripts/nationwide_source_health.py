#!/usr/bin/env python3
"""State-by-state operational original-source health and durable change receipts.

No extraction or publication of contract/policy contents; hash and accessibility
differences are REVIEW LEADS only. Failed fetches preserve last good fingerprints,
not fabricated 'unchanged' observations.
"""
import argparse,datetime as dt,json,re
from pathlib import Path
import watch_nationwide_government_originals as monitor

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/".katoptron-ci/nationwide-51-jurisdiction-original-source-watch.json"
SNAPSHOT=ROOT/".katoptron-ci/nationwide-monitor-snapshot.json"
HEALTH=ROOT/".katoptron-ci/nationwide-public-health.json"
BUILTIN=ROOT/"data/nationwide-original-government-source-receipts.json"

def validated(receipts,expected):
 if len(receipts)!=len(expected):raise ValueError("Missing monitored original-government source receipts")
 ids=set()
 for r in receipts:
  src=expected.get(r.get("source_id"))
  if not src or r["source_id"] in ids or r.get("state")!=src["state"] or r.get("source_url")!=src["source_url"] or r.get("kind")!=src["kind"]:
   raise ValueError("Source provenance mismatch or duplicate")
  ids.add(r["source_id"])
  if r.get("status") not in monitor.STATUS:raise ValueError("Source not clearly classified")
  h=r.get("original_sha256")
  if r["status"].startswith("original_"):
   if not isinstance(h,str) or not re.fullmatch("[0-9a-f]{64}",h):raise ValueError("Accessible source lacks fingerprint")
  elif h is not None:raise ValueError("Held source cannot claim accessible fingerprint")

def continuity(current,registry,existing,previous=None,day="2026-10-29"):
 jurisdiction,seeds,_=monitor.catalog(registry,existing)
 legacy=monitor.legacy_sources(existing)
 supplemental=monitor.recovery_sources()
 depth=monitor.agency_depth_sources()
 reviewed=monitor.reviewed_addition_sources()
 alternates=monitor.independent_issuer_alternatives(seeds+legacy+supplemental+depth+reviewed)
 underserved=monitor.underrepresented_government_originals()
 expected={s["id"]:s for s in seeds+legacy+supplemental+depth+reviewed+alternates+underserved}
 rows=current.get("all_source_receipts")
 if current.get("jurisdictions_total")!=51 or not isinstance(rows,list):raise ValueError("Not complete national retrieval")
 validated(rows,expected)
 previous=previous or {"receipts":[]}
 if isinstance(previous.get("receipts"),list) and previous.get("schema_version")==1:
  old={s["source_id"]:{
   "source_id":s["source_id"],"state":s["state"],"source_url":s["source_url"],"kind":s["kind"],
   "last_usable_sha256":s.get("sha256_at_observation"),"last_usable_on":previous.get("inspected_on")}
   for s in previous["receipts"] if s.get("sha256_at_observation") and s.get("status","").startswith("original_")}
 elif previous.get("schema_version")==2 and isinstance(previous.get("receipts"),list):
  old={s["source_id"]:s for s in previous["receipts"]}
 else:raise ValueError("Prior baseline not valid")
 items=[];changes=[];counts={}
 for row in rows:
  prev=old.get(row["source_id"])
  if prev and (prev["source_url"]!=row["source_url"] or prev["state"]!=row["state"] or prev["kind"]!=row["kind"]):
   raise ValueError("Government source changed identity; manual baseline review required")
  good=row["status"].startswith("original_")
  last_hash=prev.get("last_usable_sha256") if prev else None
  last_date=prev.get("last_usable_on") if prev else None
  new_hash=row["original_sha256"] if good else last_hash
  new_date=day if good else last_date
  if good and last_hash and row["original_sha256"]!=last_hash:change="source_bytes_changed_review_required"
  elif good and not last_hash:change="new_source_baseline_requires_review"
  elif not good and last_hash:change="previously_retrieved_source_currently_held"
  elif not good:change="source_unavailable_no_verified_baseline"
  else:change="source_fingerprint_unchanged_not_factual_verification"
  result={"source_id":row["source_id"],"state":row["state"],"source_url":row["source_url"],
   "kind":row["kind"],"status":row["status"],"change":change,
   "observed_on":day,"last_usable_sha256":new_hash,"last_usable_on":new_date,
   "previous_usable_sha256":last_hash,"current_observation_sha256":row["original_sha256"] if good else None,
   "individual_document_facts_verified":False,"camera_deployment_verified":False,
   "policy_adoption_verified":False}
  items.append(result);counts[change]=counts.get(change,0)+1
  if change!="source_fingerprint_unchanged_not_factual_verification":
   changes.append({"source_id":row["source_id"],"state":row["state"],"status":row["status"],
    "review_reason":change,"original_source_url":row["source_url"]})
 by_state=[]
 for j in jurisdiction:
  state=j["state"];sources=[s for s in items if s["state"]==state]
  accessible=sum(s["status"].startswith("original_") for s in sources)
  held=len(sources)-accessible
  changed=sum(s["change"]=="source_bytes_changed_review_required" for s in sources)
  unknown=sum(s["change"]=="new_source_baseline_requires_review" for s in sources)
  state_gap=("no_accessible_curated_government_original" if accessible==0 else
    "some_curated_originals_held" if held else
    "curated_originals_accessible_statewide_agency_inventory_unverified")
  by_state.append({"state":state,"name":j["name"],"originals_monitored":len(sources),
   "originals_accessible":accessible,"originals_held":held,"new_or_changed_unreviewed":changed+unknown,
   "monitored_original_source_ids":[s["source_id"] for s in sources],
   "held_original_source_ids":[s["source_id"] for s in sources if s["status"].startswith("held_")],
   "documented_gap":state_gap,
   "all_state_agencies_inventoried":False,"statewide_flock_adoption_verified":False,
   "statewide_camera_locations_verified":False})
 assert len(by_state)==51 and all(s["originals_monitored"]>=1 for s in by_state)
 snapshot={"schema_version":2,"observed_on":day,"scope":"government_source_access_and_fingerprint_only_not_published_contract_or_policy_findings",
  "jurisdictions_monitored":51,"monitored_urls":len(items),"supplemental_urls":len(supplemental),"agency_depth_urls":len(depth),"reviewed_additions_urls":len(reviewed),"official_alternate_urls":len(alternates),"receipts":items,"review_queue":changes,"review_counts":counts,
  "states":by_state,"verified_new_contract_or_policy_claims":0,"automatic_camera_or_sharing_publications":0}
 health={"schema_version":1,"observed_on":day,"scope":snapshot["scope"],
  "jurisdictions":51,"monitored_urls":len(items),"supplemental_urls":len(supplemental),"agency_depth_urls":len(depth),"reviewed_additions_urls":len(reviewed),"official_alternate_urls":len(alternates),
  "accessible_origins":sum(s["status"].startswith("original_") for s in items),
  "held_origins":sum(s["status"].startswith("held_") for s in items),
  "source_hash_changes_pending_individual_review":counts.get("source_bytes_changed_review_required",0),
  "first_baselines_pending_individual_review":counts.get("new_source_baseline_requires_review",0),
  "states":by_state,"source_receipts":[{"source_id":s["source_id"],"state":s["state"],
    "url":s["source_url"],"status":s["status"],"change":s["change"],
    "last_accessible_on":s["last_usable_on"]} for s in items],
  "source_verified_contract_changes":0,"new_camera_locations_published":0,
  "limitations":"Source monitoring and SHA changes do not prove Flock adoption, current use, policy changes or statewide source completeness. Every difference requires individual original-document review."}
 return snapshot,health

def main():
 p=argparse.ArgumentParser();p.add_argument("--run",type=Path,default=RUN)
 p.add_argument("--previous",type=Path,default=SNAPSHOT)
 p.add_argument("--snapshot",type=Path,default=SNAPSHOT)
 p.add_argument("--health",type=Path,default=HEALTH)
 args=p.parse_args()
 registry=json.loads(monitor.REGISTRY.read_text())
 existing=json.loads(monitor.EXISTING.read_text())
 prior=json.loads(args.previous.read_text()) if args.previous.is_file() else json.loads(BUILTIN.read_text())
 run=json.loads(args.run.read_text())
 snapshot,health=continuity(run,registry,existing,prior,day=dt.datetime.now(dt.timezone.utc).date().isoformat())
 for path,obj in ((args.snapshot,snapshot),(args.health,health)):
  path=path.resolve()
  if not path.is_relative_to(ROOT):raise ValueError("Unsafe output location")
  path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf8")
 print("NATIONWIDE_51_ORIGINAL_SOURCE_MONITOR",json.dumps({k:health[k] for k in
  ("jurisdictions","monitored_urls","supplemental_urls","accessible_origins","held_origins",
   "source_hash_changes_pending_individual_review","first_baselines_pending_individual_review")},sort_keys=True))
if __name__=="__main__":main()
