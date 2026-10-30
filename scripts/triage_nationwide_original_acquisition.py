#!/usr/bin/env python3
"""Prioritize nationwide original-government acquisition WITHOUT publishing search leads.

Input is the 51-state search-discovery artifact. Output is an editorial work queue,
never a verified policy, signed contract, camera, Watch event or source-version delta.
"""
import argparse,datetime as dt,json,re,urllib.parse
from pathlib import Path
from discover_51_state_original_government_links import allowed_link

ROOT=Path(__file__).resolve().parents[1]
DISCOVERY=ROOT/".katoptron-ci/nationwide-51-state-publication-discovery-leads.json"
REGISTRY=ROOT/"data/nationwide-government-jurisdiction-registry.json"
LEGACY=ROOT/"data/national-government-audit-source-portals.json"
RECOVERY=ROOT/"data/nationwide-recovery-government-originals-2026-10-29.json"
DEPTH=ROOT/"data/nationwide-targeted-agency-original-depth-2026-10-29.json"
REVIEWED=ROOT/"data/nationwide-reviewed-original-monitor-additions-2026-10-29.json"
OUT=ROOT/".katoptron-ci/nationwide-original-acquisition-editorial-queue.json"
SENSITIVE=re.compile(r"(?:search|query|plate|vehicle).{0,16}(?:log|reads?|hits?|person|location)|"
                     r"(?:raw|individual)[-_/]?(?:alpr|lpr|plate|vehicle)",re.I)
RELEVANCE=re.compile(r"\b(?:flock|alpr|license[ -]?plate|plate[ -]?readers?|"
                     r"retention|sharing|access|contract|procurement|audit)\b",re.I)

def existing_urls(registry,legacy,recovery,depth,reviewed):
    groups=(registry["official_seed_sources"],legacy["sources"],
            recovery["original_source_recovery_candidates"],depth["sources"],reviewed["sources"])
    result={}
    for group in groups:
        for row in group:
            url=row.get("source_url") or row.get("url")
            if not url:raise ValueError("Curated URL missing")
            url=allowed_link(url) or url
            if url in result and result[url]!=row.get("state"):
                raise ValueError("Same curated URL assigned to conflicting states")
            result[url]=row.get("state")
    return result

def prioritize(discovery,registry,legacy,recovery,depth,reviewed):
    states=discovery.get("states")
    all_states={x["state"] for x in registry["jurisdictions"]}
    if (discovery.get("schema_version")!=1 or discovery.get("states_enrolled")!=51 or
        not isinstance(states,list) or len(states)!=51 or
        {x.get("state") for x in states}!=all_states or len(all_states)!=51):
        raise ValueError("Complete 50-state/DC search receipt required")
    known=existing_urls(registry,legacy,recovery,depth,reviewed)
    per_state={code:sum(code==s for s in known.values()) for code in all_states}
    seen=set();queue=[];diagnostics=[]
    for state in states:
        code=state["state"];leads=state.get("search_leads")
        if (state.get("discovery_status") not in
            ("public_search_completed_leads_unverified","search_provider_unavailable_retry_needed")
            or not isinstance(leads,list) or len(leads)>6):
            raise ValueError("Invalid search provider or oversized state candidate response")
        accepted=0;held=0
        for hit in leads:
            url=hit.get("candidate_original_url")
            safe=allowed_link(url)
            title=hit.get("title","")
            if (not safe or safe!=url or SENSITIVE.search(urllib.parse.urlsplit(url).path) or
                not isinstance(title,str) or not RELEVANCE.search(title) or
                hit.get("original_document_content_reviewed") is not False or
                hit.get("flock_equipment_confirmed") is not False or
                hit.get("state_relevance_confirmed") is not False):
                held+=1;continue
            if url in seen or url in known:held+=1;continue
            seen.add(url);accepted+=1
            # Priority measures acquisition need only, NOT newsworthiness or claim accuracy.
            score=(70 if per_state[code]==0 else 45 if per_state[code]==1 else 20)+(
                10 if re.search(r"contract|agreement|policy|audit|ordinance|procurement",title,re.I) else 0)
            queue.append({"state_query":code,"candidate_url":url,"search_title":title[:200],
                "priority":score,"reason":"few_curated_state_origins" if per_state[code]<2 else "additional_original_document",
                "known_monitored_state_urls":per_state[code],
                "review_status":"hold_until_original_government_issuer_and_document_independently_verified",
                "publisher_identity_verified":False,"individual_document_reviewed":False,
                "source_date_verified":False,"flock_technology_verified":False,
                "source_version_difference_verified":False,"eligible_for_publication":False,
                "next_checks":["Confirm original issuer controls the exact URL and agency/state relevance",
                  "Retrieve bounded original bytes without cross-origin redirect or private records",
                  "Record source date, author, precise claim, status and limitations",
                  "Independent human review before adding to curated source monitor"]})
        diagnostics.append({"state":code,"search_status":state["discovery_status"],
            "curated_urls":per_state[code],"new_unreviewed_candidates":accepted,
            "duplicates_or_invalid_held":held,"inventory_complete":False})
    queue.sort(key=lambda x:(-x["priority"],x["state_query"],x["candidate_url"]))
    return {"schema_version":1,"generated_on":dt.datetime.now(dt.timezone.utc).date().isoformat(),
        "scope":"editorial_original_government_acquisition_queue_not_verified_documents",
        "states":51,"curated_urls":len(known),"new_unreviewed_candidates":len(queue),
        "priority_review_target":25,"ready_for_review":queue[:25],
        "remaining_review_queue":queue[25:],"state_gaps":diagnostics,
        "automatic_verified_records_published":0,"automatic_watch_events_sent":0,
        "source_verification_required":True,
        "limitation":"Search providers can be unavailable or return irrelevant .gov links. A queue item is never evidence of Flock use, policy adoption or a document change."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--discovery",type=Path,default=DISCOVERY)
    p.add_argument("--out",type=Path,default=OUT)
    a=p.parse_args()
    d=json.loads(a.discovery.read_text(encoding="utf8"))
    inputs=[json.loads(f.read_text(encoding="utf8")) for f in (REGISTRY,LEGACY,RECOVERY,DEPTH,REVIEWED)]
    result=prioritize(d,*inputs)
    target=a.out.resolve()
    if not target.is_relative_to(ROOT):raise ValueError("Unsafe output path")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("ORIGINAL_GOV_ACQUISITION_QUEUE",json.dumps({
        "states":result["states"],"curated_urls":result["curated_urls"],
        "new_unreviewed":result["new_unreviewed_candidates"],
        "priority_first_25":len(result["ready_for_review"]),
        "automatically_verified":0},sort_keys=True))
if __name__=="__main__":main()
