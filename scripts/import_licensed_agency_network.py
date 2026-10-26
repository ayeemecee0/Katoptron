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


def rows(byid,meta):
    for agency_id,prop in byid.items():
        state=prop.get("state")
        yield dict(
            source_agency_id=agency_id,
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


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    meta,source,links=(download(name) for name in KEYS)
    indexed=validate(meta,source,links)
    batch=list(rows(indexed,meta))
    print("External source reconciled:",len(batch),"agency IDs,",
          meta["portalCount"],"dated portal identities,",
          meta["directedEdges"],"directional links")
    if args.dry_run:
        print("DRY RUN: zero database records published")
        return
    n=publish(batch,os.getenv("SUPABASE_URL",""),
              os.getenv("SUPABASE_SERVICE_ROLE_KEY",""))
    print("Secondary agency directory imported:",n,
          "(government camera locations inserted: ZERO)")


if __name__=="__main__":
    try:main()
    except Exception as e:
        raise SystemExit("Licensed agency import held: "+type(e).__name__+
                         " "+str(e)[:140]) from None
