#!/usr/bin/env python3
"""Unverified PUBLIC search-lead discovery for every US state and Washington DC.

Search result metadata is a lead, not proof of government origin, Flock equipment,
adopted policy, installed ALPR cameras, sharing or current status. Original
documents are verified separately, via exact bounded government URLs. No private
plate records, coordinates or sensitive query data are ingested.
"""
import argparse,concurrent.futures,datetime as dt,html,json,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"nationwide-government-jurisdiction-registry.json"
OUTPUT=ROOT/".katoptron-ci"/"nationwide-51-state-publication-discovery-leads.json"
MAX_RESPONSE=700_000
MAX_PER_STATE=6
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("search_provider_redirect")
def allowed_link(url):
 if not isinstance(url,str) or len(url)>1000 or re.search(r"%2e|\\|/\.\.?/",url.split("?")[0],re.I):return None
 try:
  p=urllib.parse.urlsplit(url)
  if (p.scheme!="https" or not p.hostname or not p.hostname.endswith(".gov") or
      p.netloc!=p.hostname or p.fragment or p.username or p.password or
      not p.path.startswith("/")):return None
  if any(x in p.path.lower() for x in ("/search-logs","/raw-plate","/vehicle-reads")):return None
  return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,p.query,""))
 except (ValueError,TypeError):return None
def state_search_url(name):
 q='"Flock Safety" "license plate" "'+name+'" site:.gov'
 return "https://www.bing.com/search?format=rss&q="+urllib.parse.quote(q,safe="")
def fetch(name):
 url=state_search_url(name)
 req=urllib.request.Request(url,headers={"User-Agent":"Katoptron-public-government-records-discovery/1.0",
  "Accept":"application/rss+xml,application/xml,text/xml"})
 with urllib.request.build_opener(DenyRedirect()).open(req,timeout=18) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Search provider response changed")
  data=res.read(MAX_RESPONSE+1)
 if not 50<=len(data)<=MAX_RESPONSE:raise ValueError("Bounded search feed unavailable")
 return data
def parse_rss(name,raw):
 if not isinstance(raw,bytes) or len(raw)>MAX_RESPONSE or not raw.lstrip().startswith(b"<?xml") and not raw.lstrip().startswith(b"<rss"):
  raise ValueError("Search provider did not return public RSS")
 root=ET.fromstring(raw)
 if root.tag!="rss":raise ValueError("Search provider result changed format")
 out=[];seen=set()
 for item in root.findall("./channel/item"):
  title=" ".join((item.findtext("title") or "").split())[:200]
  url=allowed_link(item.findtext("link") or "")
  if not url or url in seen:continue
  # A search result mentioning a state in a query still does not authenticate
  # the geographic or factual relevance of its original government publisher.
  if not re.search(r"\b(?:flock|alpr|license\s+plate|plate\s+reader)\b",
      title+" "+(item.findtext("description") or ""),re.I):continue
  seen.add(url)
  out.append({"state_query":name,"title":html.unescape(title),"candidate_original_url":url,
   "evidence_tier":"public_government_domain_search_link_unverified_publisher_agency_and_content",
   "state_relevance_confirmed":False,"flock_equipment_confirmed":False,
   "original_document_content_reviewed":False,"camera_coordinates_claimed":False})
  if len(out)>=MAX_PER_STATE:break
 return out
def inspect_state(j,provider=fetch):
 row={"state":j["state"],"name":j["name"],"discovery_status":"not_checked",
  "searched_original_government_domain":False,"search_leads":[]}
 try:
  raw=provider(j["name"])
  row["search_leads"]=parse_rss(j["name"],raw)
  row["discovery_status"]="public_search_completed_leads_unverified"
  row["searched_original_government_domain"]=True
 except Exception as exc:
  row["discovery_status"]="search_provider_unavailable_retry_needed"
  row["error_type"]=type(exc).__name__
 return row
def scan(obj,provider=fetch,workers=5):
 j=obj.get("jurisdictions")
 if not isinstance(j,list) or len(j)!=51 or len({x.get("state") for x in j})!=51:
  raise ValueError("Fifty states and DC discovery queue not complete")
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  rows=list(pool.map(lambda state:inspect_state(state,provider),j))
 if len(rows)!=51 or any(r["state"]!=j[i]["state"] for i,r in enumerate(rows)):
  raise ValueError("Nationwide state discovery became incomplete")
 return {"schema_version":1,"date":dt.datetime.now(dt.timezone.utc).date().isoformat(),
  "scope":"unverified_public_government_search_leads_all_50_states_plus_dc",
  "warning":"A successful query or government-hosted search result does not establish a relevant Flock document, original authenticity, agency deployment, sharing permissions, camera coordinates or negative coverage in states with zero matches.",
  "states_enrolled":51,"states_checked":sum(x["searched_original_government_domain"] for x in rows),
  "states_provider_unavailable":sum(not x["searched_original_government_domain"] for x in rows),
  "unreviewed_government_link_leads":sum(len(x["search_leads"]) for x in rows),
  "states":rows}
def main():
 p=argparse.ArgumentParser();p.add_argument("--workers",type=int,default=5)
 p.add_argument("--out",type=Path,default=OUTPUT)
 opts=p.parse_args()
 if not 1<=opts.workers<=8:raise ValueError("Unbounded government discovery")
 obj=json.loads(REGISTRY.read_text(encoding="utf8"))
 report=scan(obj,workers=opts.workers)
 path=opts.out.resolve()
 if not path.is_relative_to(ROOT):raise ValueError("Unsafe report output")
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
 print("NATIONWIDE_51_STATE_PUBLICATION_DISCOVERY",json.dumps({"states":51,"checked":report["states_checked"],
  "provider_unavailable":report["states_provider_unavailable"],"leads_not_facts":report["unreviewed_government_link_leads"]},sort_keys=True))
 for x in report["states"]:
  print("STATE_PUBLICATION_DISCOVERY",json.dumps({"state":x["state"],
   "status":x["discovery_status"],"unreviewed_links":len(x["search_leads"])},sort_keys=True))
if __name__=="__main__":main()
