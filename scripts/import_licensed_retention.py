#!/usr/bin/env python3
"""Dated, source-attributed secondary Flock portal retention observations.
Raw EyesOnFlock is CC BY-SA 4.0 and is an aggregator, not a firsthand audit.
No physical camera positions, plate read logs, identities or user routes.
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from import_licensed_agency_network import BASE
from sync_agency_watch_events import source_key

SRC="https://eyesonflock.com/api/v1/data"
LIMIT=25_000_000

def get_json(url,opener=None):
    opener=opener or urllib.request.urlopen
    req=urllib.request.Request(url,headers={"User-Agent":"Katoptron-Source-Provenance/1.0",
                                            "Accept":"application/json"})
    with opener(req,timeout=50) as resp:
        data=resp.read(LIMIT+1)
    if len(data)>LIMIT:raise ValueError("External source exceeds size limit")
    return json.loads(data)

def retention_days(value):
    if isinstance(value,bool) or value is None:return None
    if isinstance(value,int):
        return value if 0<=value<=3650 else None
    if isinstance(value,str):
        m=re.fullmatch(r"\s*(\d{1,4})(?:\s*(?:days?|d))?\s*",value,flags=re.I)
        if m:
            x=int(m.group(1))
            return x if 0<=x<=3650 else None
    return None

def normalize(raw,registry,observed_on):
    if not isinstance(raw,dict) or not isinstance(raw.get("portals"),list) or        not 700<=len(raw["portals"])<=30000 or "summary" not in raw:
        raise ValueError("Source returned truncated or unexpected portal list")
    out=[]
    seen=set()
    for p in raw["portals"]:
        if not isinstance(p,dict):continue
        slug=p.get("slug")
        if not isinstance(slug,str) or not re.fullmatch(r"[a-z0-9-]{2,160}",slug):
            continue
        if slug in seen:raise ValueError("Duplicate portal slug from licensed source")
        seen.add(slug)
        aid=registry.get(slug)
        if not aid:continue
        out.append(dict(source_agency_id=aid,observed_on=observed_on,
                        retention_days=retention_days(p.get("data_retention")),
                        portal_slug=slug,
                        source_url="https://eyesonflock.com/portal/"+slug,
                        evidence_tier="secondary_aggregated_portal_snapshot"))
    if len(out)<700:raise ValueError("Insufficient agency identity overlap with licensed network")
    return out

def server(url,key,path,method="GET",body=None):
    req=urllib.request.Request(url.rstrip("/")+"/rest/v1/"+path,
      method=method,
      headers={"apikey":key,"Authorization":"Bearer "+key,
        "Content-Type":"application/json",
        "Prefer":"resolution=ignore-duplicates,return=minimal"},
      data=json.dumps(body).encode("utf8") if body is not None else None)
    with urllib.request.urlopen(req,timeout=45) as response:
        return json.load(response) if method=="GET" else None

def paginate(url,key,table,fields):
    rows=[]
    for offset in range(0,20000,500):
        q=urllib.parse.urlencode({"select":fields,"limit":"500","offset":str(offset)})
        result=server(url,key,table+"?"+q)
        if not isinstance(result,list):raise ValueError("Source history incomplete")
        rows.extend(result)
        if len(result)<500:return rows
    raise ValueError("Source history too large for bounded import")

def history_events(current,older,agency_names=None):
    agency_names=agency_names or {}
    prior={}
    for old in sorted(older,key=lambda r:str(r.get("observed_on"))):
        if old.get("retention_days") is not None:
            prior[old["source_agency_id"]]=old
    events=[]
    for new in current:
        previous=prior.get(new["source_agency_id"])
        if not previous or previous["retention_days"] is None or new["retention_days"] is None or            previous["retention_days"]==new["retention_days"]:continue
        digest=hashlib.sha256(
            (new["source_agency_id"]+"|"+new["observed_on"]+"|"+str(new["retention_days"])).encode()
        ).hexdigest()
        events.append({
         "event_key":"secondary_retention_"+digest,
         "source_agency_id":new["source_agency_id"],
         "kind":"retention_changed",
         "title":"Secondary source retention report changed: "+new["portal_slug"],
         "summary":("An EyesOnFlock secondary reading changed from "+
           str(previous["retention_days"])+" to "+str(new["retention_days"])+
           " days between aggregator observations. First-party status and effective policy must be rechecked."),
         "source_url":new["source_url"],
         "source_date":new["observed_on"],
         "evidence_tier":"secondary_aggregated_portal_snapshot",
         "locality_key":source_key(agency_names.get(new["source_agency_id"]))
        })
    return events

def main():
    url=os.getenv("SUPABASE_URL")
    key=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:raise RuntimeError("No protected source sync credentials")
    agencies=paginate(url,key,"flock_secondary_portal_agencies",
                      "source_agency_id,agency_name,portal_slug,is_reporting_portal")
    reg={x["portal_slug"]:x["source_agency_id"]
         for x in agencies if x.get("is_reporting_portal") and x.get("portal_slug")}
    agency_names={x["source_agency_id"]:x["agency_name"] for x in agencies}
    raw=get_json(SRC)
    now=datetime.now(timezone.utc).date().isoformat()
    rows=normalize(raw,reg,now)
    prior=paginate(url,key,"flock_secondary_portal_retention_history",
                   "source_agency_id,retention_days,observed_on")
    events=history_events(rows,prior,agency_names)
    for start in range(0,len(rows),150):
        server(url,key,
         "flock_secondary_portal_retention_history?on_conflict=source_agency_id,observed_on",
         method="POST",body=rows[start:start+150])
    if events:
        for offset in range(0,len(events),150):
            server(url,key,"flock_agency_watch_events?on_conflict=event_key",
                method="POST",body=events[offset:offset+150])
    print("Dated secondary retention source observations:",len(rows),
          "new comparative structural changes:",len(events),
          "; exact camera locations imported: ZERO")

if __name__=="__main__":
    try:main()
    except Exception as exc:
        raise SystemExit("Licensed retention sync held: "+type(exc).__name__+
                          ": "+str(exc)[:160]) from None
