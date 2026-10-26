#!/usr/bin/env python3
"""Synchronize dated public government/vendor evidence into opt-in Watch events.

Never ingest raw ALPR searches, names, plates, addresses, user routes,
private community reports, or speculative signed contracts.
Source dates are NOT ingestion dates or observed camera activity.
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta


def source_key(label):
    if not isinstance(label,str):return None
    x=label.strip()
    m=re.fullmatch(r"(.+?),\s*([A-Z]{2})",x)
    if not m:
        m=re.fullmatch(r"(.+?)\s+([A-Z]{2})\s+(?:PD|SO)",x)
    if not m:return None
    name=re.sub("[^a-z0-9 ]","",m.group(1).lower()).strip()
    return name+"|"+m.group(2) if name else None


def fingerprint(text):
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def as_event(key,kind,title,summary,source_url,source_date,tier,locality):
    if not isinstance(source_url,str) or not source_url.startswith("https://"):
        return None
    if locality is None:return None
    return {
      "event_key":key[:128],
      "kind":kind,
      "title":title[:280],
      "summary":summary[:800],
      "source_url":source_url,
      "source_date":source_date,
      "evidence_tier":tier,
      "locality_key":locality
    }


def build_events(government,portals,contracts,today=None):
    today=today or date.today()
    result=[]
    qualifying={"recorded_legislative_decision","editorially_reviewed_action","executed_contract"}
    for row in government:
        if row.get("event_type") not in qualifying:continue
        place=source_key(row.get("jurisdiction_label"))
        event_id=row.get("event_key")
        if not isinstance(event_id,str) or not event_id:continue
        key="gov_"+fingerprint("|".join([event_id,str(row.get("event_date")),
                        str(row.get("source_url")),str(row.get("evidence_level"))]))
        # Executed contracts are documents, not decisions on their own.
        # A new signed agreement can interest contract subscribers without
        # being mislabelled as a renewal.
        kind=("contract_document" if row.get("event_type")=="executed_contract"
              else "government_decision")
        obj=as_event(key,kind,
          str(row.get("title") or "Original government source event"),
          (str(row.get("summary") or "Original government source event")+
           " This record does not prove current camera installation, contract execution unless explicitly signed, or any actual plate search."),
          row.get("source_url"),row.get("event_date"),"original_government",place)
        if obj:result.append(obj)
    byagency={}
    for p in portals:
        if p.get("disclosure_status")!="verified_source_snapshot":continue
        agency=p.get("agency_key")
        source_date=p.get("source_date")
        if not agency or not source_date:continue
        byagency.setdefault(agency,[]).append(p)
        key="portal_"+fingerprint(agency+"|"+str(source_date))
        obj=as_event(key,"vendor_portal_snapshot",
          "New dated Flock vendor disclosure: "+str(p.get("agency_label")),
          "Flock-hosted agency portal snapshot dated "+str(source_date)+
          ". Mixed camera totals, searches and retention are vendor claims; not live operating status or individually verified GIS points.",
          p.get("portal_url"),source_date,"vendor_first_party",
          source_key(p.get("agency_label")))
        if obj:result.append(obj)
    for agency,items in byagency.items():
        dated=sorted(items,key=lambda a:str(a.get("source_date")))
        for old,new in zip(dated,dated[1:]):
            a,b=old.get("retention_days"),new.get("retention_days")
            if a is None or b is None or a==b:continue
            key="retention_"+fingerprint(agency+"|"+str(new["source_date"])+"|"+str(a)+"|"+str(b))
            obj=as_event(key,"retention_changed",
             "Flock vendor-reported retention changed at "+str(new.get("agency_label")),
             "Two dated first-party vendor snapshots show retention "+str(a)+" to "+str(b)+
             " days. These are source-dated disclosures, not proof of the present setting.",
             new.get("portal_url"),new.get("source_date"),
             "vendor_first_party",source_key(new.get("agency_label")))
            if obj:result.append(obj)
    for c in contracts:
        until=c.get("ends_on")
        try:ends=date.fromisoformat(str(until))
        except (TypeError,ValueError):continue
        if not today<=ends<=today+timedelta(days=90):continue
        key="expiry_"+fingerprint(str(c.get("contract_key"))+"|"+ends.isoformat())
        obj=as_event(key,"contract_renewal",
          "Source-documented Flock contract end date approaching",
          "A reviewed executed Flock agreement lists an end date of "+ends.isoformat()+
          ". This is a contract expiration watch, NOT proof that a renewal is planned or approved.",
          c.get("source_url"),ends.isoformat(),"original_government",
          source_key(c.get("jurisdiction_label")))
        if obj:result.append(obj)
    seen=set();clean=[]
    for item in result:
        if item["event_key"] not in seen:clean.append(item);seen.add(item["event_key"])
    return clean


def api(url,key,path,method="GET",body=None):
    req=urllib.request.Request(url.rstrip("/")+"/rest/v1/"+path,
     method=method,
     data=(json.dumps(body,separators=(",",":")).encode() if body is not None else None),
     headers={"apikey":key,"Authorization":"Bearer "+key,
       "Accept":"application/json","Content-Type":"application/json",
       "Prefer":"resolution=ignore-duplicates,return=minimal"})
    with urllib.request.urlopen(req,timeout=40) as response:
        return json.load(response) if method=="GET" else None


def pages(url,key,table,select,filters=""):
    out=[]
    for offset in range(0,10000,500):
        q=urllib.parse.urlencode({"select":select,"limit":"500","offset":str(offset)})
        if filters:q+="&"+filters
        batch=api(url,key,table+"?"+q)
        if not isinstance(batch,list):raise ValueError("Incomplete evidence source")
        out.extend(batch)
        if len(batch)<500:return out
    raise ValueError("Evidence source pagination limit reached")


def synchronize(url,key,events):
    for offset in range(0,len(events),125):
        api(url,key,"flock_agency_watch_events?on_conflict=event_key",
           "POST",events[offset:offset+125])
    return len(events)


def main():
    url=os.getenv("SUPABASE_URL");token=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not token:raise RuntimeError("Private Watch event sync credentials missing")
    govt=pages(url,token,"flock_accountability_events",
       "event_key,event_type,evidence_level,title,summary,jurisdiction_label,event_date,source_url")
    vendor=pages(url,token,"flock_vendor_portal_snapshots",
       "agency_key,agency_label,portal_url,source_date,retention_days,disclosure_status")
    contracts=pages(url,token,"flock_public_signed_contract_end_dates",
       "contract_key,jurisdiction_label,ends_on,source_url")
    events=build_events(govt,vendor,contracts)
    synchronize(url,token,events)
    print("Public evidence source Watch event identities reconciled:",len(events),
          "; no personal data or plate logs; no fabricated government decisions")


if __name__=="__main__":
    try:main()
    except Exception as error:
        raise SystemExit("Watch evidence sync held: "+type(error).__name__+
                         ": "+str(error)[:160]) from None
