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
from urllib.parse import urlsplit, parse_qs

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

GUID_RE=re.compile(r"^[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}$")

def indexed_matters(path=CATALOG):
    """Canonical browser GUIDs explicitly reviewed in the government docket.

    Legistar's public MatterId and its browser detail ID are distinct;
    the shared MatterGuid, not the URL, provides safe reconciliation.
    """
    obj=json.loads(Path(path).read_text(encoding="utf8"))
    if obj.get("scope")!="historical_original_government_records_not_new_source_changes":
        raise ValueError("Government source catalog unavailable")
    known={}
    known_file_ids={}
    for row in obj.get("sources",[]):
        u=urlsplit(row.get("source_url",""))
        host=(u.hostname or "").lower()
        if u.scheme!="https" or not host.endswith(".legistar.com"):
            continue
        tenant=host[:-len(".legistar.com")]
        if tenant not in TENANTS or row.get("agency")!=TENANTS[tenant][0]:
            raise ValueError("Government docket publisher binding drift")
        guid=parse_qs(u.query).get("GUID",[None])[0]
        if not GUID_RE.fullmatch(guid or ""):
            raise ValueError("Government docket GUID absent/invalid")
        known.setdefault(tenant,set()).add(guid.upper())
        file_number=row.get("file_number")
        if not isinstance(file_number,str) or not 1<=len(file_number)<=35:
            raise ValueError("Missing official Legistar file number")
        normalize=lambda x:" ".join(x.upper().split())
        file_id=normalize(file_number)
        known_file_ids.setdefault(tenant,set()).add(file_id)
    if set(known)!=set(TENANTS):
        raise ValueError("Incomplete exact Legistar GUID catalog")
    return known,known_file_ids

def official_matter_guid(tenant,lead,fetcher=scanner.get_json):
    """Verify the stable WebAPI matter UUID before treating a lead as novel."""
    url=urlsplit(lead["url"])
    if (url.scheme!="https" or url.hostname!="webapi.legistar.com" or
        not re.fullmatch("/v1/"+re.escape(tenant)+r"/matters/\d+",url.path) or
        url.query or url.fragment or url.username or url.password):
        raise ValueError("Unapproved detail URL")
    item=fetcher(lead["url"])
    match=re.fullmatch("/v1/"+re.escape(tenant)+r"/matters/(\d+)",url.path)
    if (not isinstance(item,dict) or str(item.get("MatterId"))!=match.group(1)
        or item.get("MatterRestrictViewViaWeb") is True or
        not GUID_RE.fullmatch(str(item.get("MatterGuid") or ""))):
        raise ValueError("Official matter GUID unavailable or inconsistent")
    file_id=item.get("MatterFile")
    if not isinstance(file_id,str) or not 1<=len(file_id)<=35:
        raise ValueError("Public matter File # missing; novelty held")
    file_id=" ".join(file_id.upper().split())
    if not re.fullmatch(r"[A-Z0-9 ./_-]{1,35}",file_id):
        raise ValueError("Unrecognized public matter file number")
    return item["MatterGuid"].upper(),file_id

def acquire(seeds,collector=scanner.scan,enqueue=scanner.queue,workers=4,
            detail_fetch=scanner.get_json,known_guids=None,known_file_ids=None):
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
    if known_guids is None or known_file_ids is None:
        actual_guids,actual_files=indexed_matters()
        catalog=actual_guids if known_guids is None else known_guids
        file_catalog=actual_files if known_file_ids is None else known_file_ids
    else:
        catalog=known_guids
        file_catalog=known_file_ids
    if not isinstance(catalog,dict) or not isinstance(file_catalog,dict) or not set(seeds)<=set(catalog) or not set(seeds)<=set(file_catalog):
        raise ValueError("Publisher-specific reviewed matter GUID registry missing")
    found=0;created=0;failed=0;already_indexed=0;held=0;uncatalogued=0;all_rows=[]
    for tenant,leads,error in sorted(outcomes):
        row={"tenant":tenant,"publisher":seeds[tenant],"discovery_status":"source_unavailable" if error else "public_agenda_scan_complete",
             "error_type":error,"matched_agenda_leads":len(leads),"new_to_review_queue":0,"queue_failures":0,"already_in_source_catalog":0,"unreconciled_guid_hold":0,"new_uncatalogued_matches":0,"public_matter_files_seen":[]}
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
                guid,file_code=official_matter_guid(tenant,lead,detail_fetch)
            except Exception:
                held+=1;row["unreconciled_guid_hold"]+=1
                continue
            row["public_matter_files_seen"].append(file_code)
            if guid in catalog[tenant] or file_code in file_catalog[tenant]:
                already_indexed+=1;row["already_in_source_catalog"]+=1
                continue
            uncatalogued+=1;row["new_uncatalogued_matches"]+=1
            try:
                if enqueue(lead):
                    created+=1;row["new_to_review_queue"]+=1
            except Exception:
                failed+=1;row["queue_failures"]+=1
        all_rows.append(row)
    return {"schema_version":1,"new_agencies_discovered":0,
            "source_tenants_checked":len(outcomes),"candidate_matches":found,
            "new_review_queue_leads":created,"already_in_source_catalog":already_indexed,
            "new_uncatalogued_matches":uncatalogued,"unreconciled_guid_hold":held,
            "queue_write_failures":failed,
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
    for row in result["tenant_outcomes"]:
        if row["public_matter_files_seen"]:
            print("Official agenda file-number crosscheck:",row["tenant"],
                  ",".join(row["public_matter_files_seen"]),
                  "already indexed:",row["already_in_source_catalog"])
    print("P0 government acquisition:",json.dumps({
      k:result[k] for k in ("source_tenants_checked","candidate_matches",
       "new_uncatalogued_matches","already_in_source_catalog","unreconciled_guid_hold",
       "new_review_queue_leads","queue_write_failures","alert_events_created")}))
    if result["queue_write_failures"]:
        raise RuntimeError("Some reviewed source candidates could not be queued; artifact retained")

if __name__=="__main__":main()
