#!/usr/bin/env python3
"""Fetch original .gov publisher pages and compare *verified* text versions.

First observation is baseline, NEVER an alert. Every subsequent new fingerprint
is private pending original-page editorial review, NEVER auto-mailed as an agency
decision, changed contract, adopted policy, spending, or live camera event.
"""
import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from convert_official_flock_disclosures import PlainText, normalize
from verify_new_original_agency_html import ANCHORS, fetch, valid

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data"/"qualified-original-government-docket-2026-10-29.json"

def hash_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def fingerprint(row,raw):
    if row["id"] not in ANCHORS or not valid(row["source_url"]):
        raise ValueError("Unqualified government issuer")
    if not isinstance(raw,bytes) or len(raw)>2_500_000:
        raise ValueError("Original government HTML bytes invalid")
    if b"<html" not in raw[:3000].lower():
        raise ValueError("Original publisher did not supply HTML")
    parser=PlainText()
    parser.feed(raw.decode("utf-8","replace"))
    body=normalize(" ".join(parser.blocks))
    anchor=normalize(ANCHORS[row["id"]])
    idx=body.find(anchor)
    if idx<0:
        raise ValueError("Exact source-specific claim anchor disappeared")
    # Changes to boilerplate still go to review, but are distinguishable
    # from changes near the original agency claim.
    context=body[max(0,idx-220):min(len(body),idx+len(anchor)+220)]
    return {"source_id":row["id"],"source_url":row["source_url"],
        "locality_key":row["locality_key"],"source_date":row["source_date"],
        "text_sha256":hash_text(body),"anchor_context_sha256":hash_text(context)}

def rest(base,secret,resource,method="GET",body=None):
    headers={"apikey":secret,"Authorization":"Bearer "+secret,
             "Accept":"application/json","Content-Type":"application/json"}
    if method=="POST":headers["Prefer"]="resolution=ignore-duplicates,return=minimal"
    req=urllib.request.Request(base.rstrip("/")+"/rest/v1/"+resource,
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=35) as response:
        if method=="GET":
            result=json.load(response)
            if not isinstance(result,list):raise RuntimeError("Government version lookup returned unexpected response")
            return result
        return None

def record(fact,api):
    source=urllib.parse.quote(fact["source_id"],safe="")
    previous=api("flock_original_page_versions?"+urllib.parse.urlencode({
        "select":"text_sha256,anchor_context_sha256",
        "source_id":"eq."+fact["source_id"],"order":"first_seen_at.desc","limit":"1"}))
    if len(previous)>1:raise RuntimeError("Ambiguous government version history")
    prior=previous[0] if previous else None
    # Write baseline BEFORE any change review. Unique receipt is idempotent.
    api("flock_original_page_versions?on_conflict=source_id,text_sha256","POST",[fact])
    if not prior:return "baselined_unreviewed_not_an_event"
    if prior["text_sha256"]==fact["text_sha256"]:
        return "unchanged"
    scope=("anchor_context_changed" if prior["anchor_context_sha256"]!=fact["anchor_context_sha256"]
           else "publisher_page_text_changed")
    review={"source_id":fact["source_id"],"source_url":fact["source_url"],
        "locality_key":fact["locality_key"],"previous_sha256":prior["text_sha256"],
        "current_sha256":fact["text_sha256"],"change_scope":scope}
    api("flock_original_page_review_queue?on_conflict=source_id,current_sha256","POST",[review])
    return "held_"+scope+"_requires_original_editorial_review"

def scan(rows,fetcher,api):
    if len({x["id"] for x in rows})!=len(rows):raise ValueError("Duplicate source identity")
    outcomes={}
    for row in rows:
        if row["id"] not in ANCHORS:continue
        try:
            if row["watch_category"]!="historical_research_only":raise ValueError("New-event replay prohibited")
            fact=fingerprint(row,fetcher(row["source_url"]))
            outcomes[row["id"]]=record(fact,api)
        except Exception as e:
            # Never silently label a source as reviewed after a timeout,
            # redirect, removed anchor, invalid publisher, or API failure.
            outcomes[row["id"]]="held_"+type(e).__name__
    return outcomes

def main():
    base=os.environ.get("SUPABASE_URL")
    secret=os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not base or not secret:raise RuntimeError("Protected service credentials absent")
    data=json.loads(CATALOG.read_text(encoding="utf8"))
    outcomes=scan(data["sources"],fetch,lambda path,method="GET",body=None:
        rest(base,secret,path,method,body))
    totals={}
    for status in outcomes.values():totals[status]=totals.get(status,0)+1
    print("ORIGINAL_GOVERNMENT_VERSION_REVIEW",json.dumps({
       "checked":len(outcomes),"outcomes":totals,
       "automatically_published_watch_events":0,
       "automatically_certified_contract_changes":0}))
    if not outcomes or sum(v=="unchanged" or v=="baselined_unreviewed_not_an_event"
                       or v.startswith("held_anchor_context_changed") or
                       v.startswith("held_publisher_page_text_changed")
                       for v in outcomes.values())<6:
        raise RuntimeError("Too few original government versions could be safely checked")
if __name__=="__main__":main()
