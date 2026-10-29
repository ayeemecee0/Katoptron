#!/usr/bin/env python3
"""Conservative original Sacramento County publisher watch.

Visits only the explicitly reviewed County Clerk and Sheriff Commission
government publication pages. Extracts *links whose visible labels explicitly
mention Flock/ALPR*. New links go to a protected unreviewed queue, never to
public Watch events, contract/decision facts, or camera coordinates.

This supplements the separate original-source Legistar scan. HTML links that
don't directly name surveillance remain out of scope: no invented matches.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/".katoptron-ci/sacramento-county-official-source-watch.json"
PAGES=(
  "https://sccob.saccounty.gov/us/en/sheriff-community-review-commission.html",
  "https://sccob.saccounty.gov/us/en/board-of-supervisors-public-meetings.html",
  "https://agendanet.saccounty.gov/",
)
HOSTS=frozenset(("sccob.saccounty.gov","agendanet.saccounty.gov",
                 "www.saccounty.gov","www.sacsheriff.com","sacsheriff.com"))
MAX_BYTES=1_200_000
MAX_ANCHORS=1500
MAX_LEADS=70
MATCH=re.compile(r"\b(?:flock\s*(?:safety|group)?|alpr|automated?\s+licen[sc]e\s+plate\s+(?:recognition|reader))\b",re.I)

def approved(url):
    if not isinstance(url,str) or len(url)>1600 or any(ord(c)<32 for c in url):
        return False
    try:
        p=urllib.parse.urlsplit(url)
        return (p.scheme=="https" and p.hostname in HOSTS and
          p.port is None and p.username is None and p.password is None and
          not p.fragment and p.path.startswith("/") and
          not any(s in (".","..") for s in urllib.parse.unquote(p.path).split("/")))
    except (TypeError,ValueError):return False

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items=[];self.href=None;self.parts=[];self.count=0
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            self.count+=1
            self.href=next((v for k,v in attrs if k.lower()=="href"),None)
            self.parts=[]
    def handle_data(self,data):
        if self.href is not None:
            self.parts.append(data[:400])
    def handle_endtag(self,tag):
        if tag.lower()=="a" and self.href is not None:
            self.items.append((self.href," ".join(" ".join(self.parts).split())[:300]))
            self.href=None;self.parts=[]

def find_links(base,html):
    if not approved(base):raise ValueError("Unapproved government publisher")
    if not isinstance(html,str) or len(html)>MAX_BYTES:
        raise ValueError("Oversize or invalid government page")
    parser=Anchors();parser.feed(html)
    if parser.count>MAX_ANCHORS:raise ValueError("Too many government-page links")
    rows={}
    for href,label in parser.items:
        if not MATCH.search(label):continue
        url=urllib.parse.urljoin(base,href)
        if not approved(url) or url==base:continue
        # Query strings can contain sensitive tokens; these public publisher
        # pages use no account-bearing links for reviewed source documents.
        if re.search(r"(?:token|access_key|session|auth|password)=",url,re.I):
            continue
        rows[url]={"url":url,"headline":label[:180],
           "publisher":"Sacramento County official public publisher",
           "snippet":"Candidate original-government link labelled "+label[:230]+
           ". UNREVIEWED: Not an approved decision, contract, policy version or live camera evidence.",
           "state_hint":"CA","status":"unreviewed"}
        if len(rows)>MAX_LEADS:raise ValueError("Too many qualified links")
    return list(rows.values())

class StrictRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not approved(newurl):raise ValueError("External or unsafe redirect")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch_page(url):
    if url not in PAGES:raise ValueError("Unseeded government publisher")
    opener=urllib.request.build_opener(StrictRedirect())
    req=urllib.request.Request(url,headers={"User-Agent":"Katoptron/1.0 public government-source monitoring",
                                           "Accept":"text/html"})
    with opener.open(req,timeout=18) as response:
        if not approved(response.geturl()):
            raise ValueError("Publisher escaped allowlist")
        content=response.read(MAX_BYTES+1)
        if len(content)>MAX_BYTES:raise ValueError("Publisher page too large")
        media=response.headers.get("Content-Type","")
        if "text/html" not in media.lower():
            raise ValueError("Publisher not HTML")
    return content.decode("utf8",errors="replace")

def discover(fetch=fetch_page):
    results=[];all_leads={};errors=0
    for page in PAGES:
        try:
            html=fetch(page)
            leads=find_links(page,html)
            for row in leads:all_leads.setdefault(row["url"],row)
            results.append({"url":page,"status":"scanned","explicit_label_matches":len(leads),
               "source_sha256":hashlib.sha256(html.encode("utf8")).hexdigest()})
        except Exception as exc:
            errors+=1
            results.append({"url":page,"status":"held","error_type":type(exc).__name__})
    return {"schema_version":1,"jurisdiction":"Sacramento County, CA",
            "source_pages_checked":len(PAGES),"source_pages_held":errors,
            "unreviewed_explicit_source_links":len(all_leads),
            "public_alert_events_created":0,
            "new_contracts_verified":0,"camera_locations_published":0,
            "publication_policy":"Private original-source candidate review ONLY; no automatic facts or Watch alerts.",
            "sources":results,"leads":list(all_leads.values())}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args()
    if args.validate_only:
        assert len(PAGES)==3 and all(approved(p) for p in PAGES)
        print("Sacramento official publisher seeds:",len(PAGES))
        return
    result=discover()
    # Send only unpublished, unreviewed candidates to the existing private
    # queue; identity deduplication is enforced by URL uniqueness in Postgres.
    created=0;failed=0
    if result["leads"]:
        from discover_government_records import queue
        for lead in result["leads"]:
            try:created+=int(queue(lead))
            except Exception:failed+=1
    result["queue_added"]=created
    result["queue_failures"]=failed
    result["leads"]=[{"source_url":x["url"],"status":"unreviewed"} for x in result["leads"]]
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("SACRAMENTO_OFFICIAL_SOURCE_DISCOVERY",json.dumps({
        k:result[k] for k in ("source_pages_checked","source_pages_held",
          "unreviewed_explicit_source_links","queue_added","queue_failures",
          "public_alert_events_created")}))
    if failed:raise RuntimeError("Private queue writes failed; audit artifact saved")
    if result["source_pages_held"]==len(PAGES):
        raise RuntimeError("All original government publishers inaccessible; audit retained")

if __name__=="__main__":main()
