#!/usr/bin/env python3
"""Source-identity-pinned national ALPR agenda acquisition.

Bootstraps additional government Legistar tenants from a manually reviewed
government-record issuer/tenant link. Reuses bounded, paginated discovery
and an idempotent private review queue. NEVER promotes an agenda lead to
a passed vote, signed contract, map point or subscriber alert.
"""
import argparse
import concurrent.futures
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import discover_government_records as scanner

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data/qualified-original-government-docket-2026-10-29.json"
OUTPUT=ROOT/".katoptron-ci/government-new-agenda-leads.json"
TENANTS={
 "cityofcleveland":("Cleveland Division of Police","OH"),
 "elpasotexas":("El Paso City Council","TX"),
 "stpaul":("Saint Paul City Council","MN"),
 "allentownpa":("Allentown City Council","PA"),
 "carrolltontx":("Carrollton City Council","TX"),
 "rockfordil":("Rockford City Council","IL"),
 "monterey":("Monterey County Sheriff's Office","CA"),
 "manteca-ca":("Manteca Police Department","CA"),
 "ci-ssf-ca":("South San Francisco Police Department","CA"),
}
# A source page is a seed for discovery ONLY if it was examined and remains
# exactly tied to the above tenant and issuer. Do not accept arbitrary YAML.
EXACT_SEEDS={
 "cityofcleveland":"cleveland-oh-ordinance-683-2026",
 "elpasotexas":"el-paso-tx-item-26-1092",
 "stpaul":"saint-paul-mn-res-26-1421",
 "allentownpa":"allentown-pa-ipvm-15-8653",
 "carrolltontx":"carrollton-tx-item-7749",
 "rockfordil":"rockford-il-res-26-00160",
 "monterey":"monterey-ca-agenda-a-26-368",
 "manteca-ca":"manteca-ca-agenda-26-399",
 "ci-ssf-ca":"south-san-francisco-ca-26-2370",
}
def verified_seed_registry(path=CATALOG):
    obj=json.loads(Path(path).read_text(encoding="utf8"))
    if obj.get("schema_version")!=1 or obj.get("scope")!="historical_original_government_records_not_new_source_changes":
        raise ValueError("Unreviewed source seed registry")
    docs={row["id"]:row for row in obj["sources"]}
    seeds={}
    for tenant,(label,state) in TENANTS.items():
        row=docs.get(EXACT_SEEDS[tenant])
        if not row or row.get("agency")!=label or row.get("state")!=state or row.get("watch_category")!="historical_research_only":
            raise ValueError("Reviewed government issuer mismatch: "+tenant)
        url=urlsplit(row.get("source_url",""))
        if (url.scheme!="https" or url.hostname!=tenant+".legistar.com" or
            url.port is not None or url.username or url.password or url.fragment or
            url.path!="/LegislationDetail.aspx" or not re.search(r"(?:^|&)ID=\d{6,9}(?:&|$)",url.query)):
            raise ValueError("Government Legistar source identity invalid: "+tenant)
        seeds[tenant]=label
    return seeds

def acquire(seeds,collector=scanner.scan,enqueue=scanner.queue,workers=4):
    # Existing scanner has bounded pages, sanitized query terms, and only
    # public matters. Limit bootstrap scan breadth independently so it
    # cannot burn through hundreds of tenant API requests per scheduled job.
    previous=(scanner.PAGE_SIZE,scanner.MAX_PAGES_PER_TENANT,scanner.MAX_MATCHES_PER_TENANT)
    scanner.PAGE_SIZE=80
    scanner.MAX_PAGES_PER_TENANT=3
    scanner.MAX_MATCHES_PER_TENANT=12
    outcomes=[]
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(collector,k,v):k for k,v in seeds.items()}
            for future in concurrent.futures.as_completed(futures):
                tenant=futures[future]
                try:
                    leads=future.result()
                    if not isinstance(leads,list):raise ValueError("Invalid agenda scan result")
                    outcomes.append((tenant,leads,None))
                except Exception as exc:
                    outcomes.append((tenant,[],type(exc).__name__))
    finally:
        scanner.PAGE_SIZE,scanner.MAX_PAGES_PER_TENANT,scanner.MAX_MATCHES_PER_TENANT=previous
    found=0;created=0;failed=0;all_rows=[]
    for tenant,leads,error in sorted(outcomes):
        row={"tenant":tenant,"publisher":seeds[tenant],"discovery_status":"source_unavailable" if error else "public_agenda_scan_complete",
             "error_type":error,"matched_agenda_leads":len(leads),"new_to_review_queue":0,"queue_failures":0}
        for lead in leads:
            # Never insert externally supplied website/tenant links. The
            # scanner's MatterId API endpoint is stable, but not the browser ID.
            url=urlsplit(lead.get("url",""))
            if (url.scheme!="https" or url.hostname!="webapi.legistar.com"
                or not re.fullmatch("/v1/"+re.escape(tenant)+r"/matters/\d+",url.path)
                or url.query or url.fragment or lead.get("status")!="unreviewed"
                or lead.get("publisher")!=seeds[tenant]):
                raise ValueError("Unverified discovery lead held")
            found+=1
            try:
                if enqueue(lead):
                    created+=1;row["new_to_review_queue"]+=1
            except Exception:
                failed+=1;row["queue_failures"]+=1
        all_rows.append(row)
    return {"schema_version":1,"new_agencies_discovered":0,
            "source_tenants_checked":len(outcomes),"candidate_matches":found,
            "new_review_queue_leads":created,"queue_write_failures":failed,
            "alert_events_created":0,"agencies_with_verified_new_contracts":0,
            "coverage_note":"Candidates are unreviewed Legistar agenda matters. Not new source-qualified Watch alerts, signed contracts or camera positions.",
            "tenant_outcomes":all_rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--validate-only",action="store_true")
    p.add_argument("--output",default=str(OUTPUT))
    args=p.parse_args()
    sources=verified_seed_registry()
    if args.validate_only:
        print("Verified government agenda discovery seed links:",len(sources),
              "states:",len(set(state for _,state in TENANTS.values())))
        return
    result=acquire(sources)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("P0 government acquisition:",json.dumps({
      k:result[k] for k in ("source_tenants_checked","candidate_matches",
       "new_review_queue_leads","queue_write_failures","alert_events_created")}))
    if result["queue_write_failures"]:
        raise RuntimeError("Some reviewed source candidates could not be queued; artifact retained")

if __name__=="__main__":main()
