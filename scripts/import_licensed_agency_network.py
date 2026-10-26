#!/usr/bin/env python3
"""Import complete licensed secondary agency directory. Never creates GIS pins.

Source: EyesOnFlock via deflock-data (CC BY-SA 4.0).
Network edges are consumed directionally by agency-network.js; the DB stores
only clearly SECONDARY organization summaries, not 700k rows pretending to be
first-party agreements, and not OSM or municipal camera coordinates.

Fails shut on incomplete files before writing any records.
"""
import argparse
import json
import hashlib
import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict

BASE = "https://deflockdata.dontgetflocked.com/"
MAX_BYTES = 40_000_000
KEYS = ("sharing-network-meta.json","sharing-network-nodes.geojson","sharing-network-adjacency.json")


def download(name, opener=urllib.request.urlopen):
    url = BASE + name
    request = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Katoptron-Evidence-Research/1.0 (public source attribution)",
    })
    with opener(request, timeout=45) as resp:
        if getattr(resp, "status", 200) != 200:
            raise ValueError("Source HTTP failure")
        payload = resp.read(MAX_BYTES+1)
        if len(payload)>MAX_BYTES:
            raise ValueError("Source file exceeds fixed safe size")
    return json.loads(payload)


def validate(meta,geojson,adjacency):
    if not isinstance(meta,dict) or not isinstance(geojson,dict) or not isinstance(adjacency,dict):
        raise ValueError("Incomplete secondary network source")
    features=geojson.get("features")
    if geojson.get("type")!="FeatureCollection" or not isinstance(features,list) or not 5000<=len(features)<=30000:
        raise ValueError("Incomplete or invalid agency catalogue")
    if meta.get("featureCount")!=len(features) or not 700<=meta.get("portalCount",0)<=30000:
        raise ValueError("Agency/portal count mismatch")
    if not re.fullmatch(r"20\d\d-\d\d-\d\dT[^ ]+",str(meta.get("generatedAt",""))):
        raise ValueError("Missing dated source snapshot")
    ids=set()
    portals=0
    byid={}
    for record in features:
        prop=record.get("properties") if isinstance(record,dict) else None
        if not isinstance(prop,dict):
            raise ValueError("Agency source properties missing")
        aid=prop.get("id")
        if not isinstance(aid,str) or not 2<=len(aid)<=160 or aid in ids:
            raise ValueError("Duplicate or invalid canonical agency ID")
        name=prop.get("name")
        if not isinstance(name,str) or not 2<=len(name)<=300:
            raise ValueError("Invalid source agency name")
        ids.add(aid)
        byid[aid]=prop
        portals+=prop.get("isPortal") is True
    if portals!=meta["portalCount"]:
        raise ValueError("Portal identity reconciliation mismatch")
    edges=0
    for parent,children in adjacency.items():
        if parent not in ids or not isinstance(children,list):
            raise ValueError("Unknown sharing source")
        seen=set()
        for child in children:
            if child not in ids or child==parent or child in seen:
                raise ValueError("Invalid, duplicate or self-referential source edge")
            seen.add(child)
        edges+=len(children)
    if not 100000<=edges<=2500000 or edges!=meta.get("directedEdges"):
        raise ValueError("Directed network edge inventory truncated")
    return byid


def as_optional_int(value):
    if not isinstance(value,int) or isinstance(value,bool) or value<0:
        return None
    return value


def rows(byid,meta,adjacency=None):
    for agency_id,prop in byid.items():
        state=prop.get("state")
        edges=(adjacency or {}).get(agency_id)
        # A portal with NO listed recipients is still a known empty list,
        # not a missing snapshot. Its SHA must detect first addition and
        # removal of the final directed source relationship.
        fingerprint=(hashlib.sha256(("\\n".join(edges or [])).encode("utf8")).hexdigest()
                      if prop.get("isPortal") is True else None)
        yield dict(
            source_agency_id=agency_id,
            sharing_list_sha256=fingerprint,
            agency_name=prop["name"],
            state_code=state if isinstance(state,str) and re.fullmatch("[A-Z]{2}",state) else None,
            agency_type=prop.get("type") if prop.get("type") in
                {"police","sheriff","state","federal","school","private","other"} else "other",
            is_reporting_portal=prop.get("isPortal") is True,
            portal_slug=prop.get("portalSlug") if prop.get("isPortal") else None,
            # Zero in the source export may encode blank field. Avoid
            # presenting missing vendor counter as a measured zero.
            source_reported_mixed_cameras=(as_optional_int(prop.get("cameras")) or None)
                if prop.get("isPortal") else None,
            source_reported_searches=(as_optional_int(prop.get("searches")) or None)
                if prop.get("isPortal") else None,
            source_reported_hotlist_hits=(as_optional_int(prop.get("hotlistHits")) or None)
                if prop.get("isPortal") else None,
            source_reported_network_links=as_optional_int(prop.get("connectionCount")),
            source_snapshot_at=meta["generatedAt"],
            source_url=BASE+"sharing-network-nodes.geojson",
            source_tier="secondary_aggregated_portal_snapshot",
            source_license="CC BY-SA 4.0",
        )


def publish(data, url, token, sender=None, batch_size=175):
    if not token or not url.startswith("https://"):
        raise ValueError("Private import credentials unavailable")
    sender=sender or urllib.request.urlopen
    endpoint=url.rstrip("/")+"/rest/v1/flock_secondary_portal_agencies?on_conflict=source_agency_id"
    completed=0
    for at in range(0,len(data),batch_size):
        batch=data[at:at+batch_size]
        request=urllib.request.Request(endpoint,
         data=json.dumps(batch,separators=(",",":")).encode("utf8"),
         method="POST",
         headers={"apikey":token,"Authorization":"Bearer "+token,
          "Content-Type":"application/json",
          "Prefer":"resolution=merge-duplicates,return=minimal"})
        with sender(request,timeout=40) as response:
            if getattr(response,"status",204) not in (200,201,204):
                raise RuntimeError("Secondary agency directory write held")
        completed+=len(batch)
    return completed


def previous_fingerprints(url, token, fetcher=None):
    fetcher=fetcher or urllib.request.urlopen
    out={}
    base=url.rstrip("/")+"/rest/v1/flock_secondary_portal_agencies"
    for offset in range(0,5000,500):
        query="?select=source_agency_id,sharing_list_sha256&is_reporting_portal=eq.true&limit=500&offset="+str(offset)
        req=urllib.request.Request(base+query,headers={"apikey":token,"Authorization":"Bearer "+token})
        with fetcher(req,timeout=30) as resp:
            rows=json.load(resp)
        if not isinstance(rows,list):
            raise ValueError("Old source history truncated")
        for r in rows:
            out[r["source_agency_id"]]=r.get("sharing_list_sha256")
        if len(rows)<500:return out
    raise ValueError("Old source history exceeds maximum page count")


def locality(prop):
    name=prop.get("name","")
    m=re.fullmatch(r"(.+?) ([A-Z]{2}) (?:PD|SO)",name)
    if not m:return None
    place=re.sub(r"[^a-z0-9 ]","",m.group(1).lower()).strip()
    return place+"|"+m.group(2) if place else None


def structural_events(data,previous,byid,meta):
    events=[]
    for row in data:
        key=row["source_agency_id"]
        old=previous.get(key)
        new=row.get("sharing_list_sha256")
        if not old or not new or old==new:continue
        prop=byid[key]
        source=BASE+"sharing-network-adjacency.json"
        slug=prop.get("portalSlug")
        if isinstance(slug,str) and re.fullmatch("[a-z0-9-]{2,160}",slug):
            source="https://eyesonflock.com/portal/"+slug
        digest=hashlib.sha256((key+"|"+new).encode("utf8")).hexdigest()
        events.append({
            "event_key":"share_"+digest,
            "locality_key":locality(prop),
            "source_agency_id":key,
            "kind":"sharing_list_changed",
            "title":(prop["name"]+" source-reported sharing list changed")[:280],
            "summary":"The dated secondary portal network changed the named outbound recipient list. This is not proof of an actual plate search, current permission, or government-certified access. Review the original vendor portal.",
            "source_url":source,
            "source_date":meta["generatedAt"][:10],
            "evidence_tier":"secondary_aggregated_portal_snapshot"
        })
    return events


def publish_events(events,url,token,sender=None):
    if not events:return 0
    sender=sender or urllib.request.urlopen
    endpoint=url.rstrip("/")+"/rest/v1/flock_agency_watch_events?on_conflict=event_key"
    for at in range(0,len(events),150):
        req=urllib.request.Request(endpoint,
          data=json.dumps(events[at:at+150],separators=(",",":")).encode("utf8"),
          method="POST",
          headers={"apikey":token,"Authorization":"Bearer "+token,
                   "Content-Type":"application/json",
                   "Prefer":"resolution=ignore-duplicates,return=minimal"})
        with sender(req,timeout=45) as response:
            if getattr(response,"status",204) not in (200,201,204):
                raise ValueError("Secondary structural watch publication held")
    return len(events)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    meta,source,links=(download(name) for name in KEYS)
    indexed=validate(meta,source,links)
    batch=list(rows(indexed,meta,links))
    print("External source reconciled:",len(batch),"agency IDs,",
          meta["portalCount"],"dated portal identities,",
          meta["directedEdges"],"directional links")
    if args.dry_run:
        print("DRY RUN: zero database records published")
        return
    url=os.getenv("SUPABASE_URL","")
    token=os.getenv("SUPABASE_SERVICE_ROLE_KEY","")
    if not url or not token:raise ValueError("Protected import secrets missing")
    previous=previous_fingerprints(url,token)
    structural=structural_events(batch,previous,indexed,meta)
    publish_events(structural,url,token)
    n=publish(batch,url,token)
    print("New genuine structural sharing changes:",len(structural))
    print("Secondary agency directory imported:",n,
          "(government camera locations inserted: ZERO)")


if __name__=="__main__":
    try:main()
    except Exception as e:
        raise SystemExit("Licensed agency import held: "+type(e).__name__+
                         " "+str(e)[:140]) from None
