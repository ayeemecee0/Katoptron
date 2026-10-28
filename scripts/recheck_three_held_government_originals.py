#!/usr/bin/env python3
"""Recheck two formerly held original government ALPR publications.

Third held Lafayette CO program source is reconciled to a newer original
government termination statement rather than falsely reverting its status.
Produces only source-qualified review receipts. No camera locations, present
vendor access, policy-effective dates or signed contracts inferred.
"""
import hashlib,html,json,re,unicodedata,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"nationwide-government-jurisdiction-registry.json"
ORIGINALS=ROOT/"data"/"nationwide-original-government-source-receipts.json"
NEWER=ROOT/"data"/"verified-agency-html-source-disclosures-2026-10-27.json"
CHECKED={
 "fl-police-operational-status-statement":{
  "state":"FL",
  "url":"https://www.pcbfl.gov/m/NewsFlash/Home/Detail/38",
  "category":"city_chief_announced_flock_use_suspension_and_removal_planning",
  "anchors":[
   "suspending its use of the Flock Automated License Plate Reader system effective immediately",
   "PCBPD will work with Flock to coordinate the removal of cameras",
   "PCBPD's access to and use of the Flock system ends today"
  ]},
 "nc-police-technology-disclosure":{
  "state":"NC",
  "url":"https://raleighnc.gov/services/how-does-raleigh-use-flock-cameras",
  "category":"city_police_describes_flock_use_monthly_audits_retention_and_annual_cost",
  "anchors":[
   "The City of Raleigh partners with Flock Safety",
   "Flock data is automatically deleted after 30 days",
   "The department pays about $75,000 annually for Flock cameras"
  ]}
}
CO_SOURCE="co-police-technology-disclosure"
CO_NEW="lafayette-co"
class HTMLText(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.off=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in {"script","style","svg","noscript","template"}:self.off+=1
 def handle_endtag(self,t):
  if t in {"script","style","svg","noscript","template"}:self.off=max(0,self.off-1)
 def handle_data(self,t):
  if not self.off and t.strip():self.parts.append(t.strip())
def norm(s):
 s=unicodedata.normalize("NFKC",html.unescape(s)).replace("’","'").replace("‘","'")
 return " ".join(s.casefold().split())
MAX_BYTES=1_900_000
class NoCrossHost(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,url):
  base=urllib.parse.urlsplit(req.full_url)
  dst=urllib.parse.urlsplit(url)
  if dst.scheme!="https" or dst.hostname!=base.hostname:
   raise ValueError("Government original redirect changed publisher")
  return super().redirect_request(req,fp,code,msg,headers,url)
def fetch(url):
 if url not in {x["url"] for x in CHECKED.values()}:
  raise ValueError("Original publisher URL not in source registry")
 req=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-government-ALPR-original-source-review/1.0",
  "Accept":"text/html"})
 with urllib.request.build_opener(NoCrossHost()).open(req,timeout=25) as r:
  if r.status!=200:raise ValueError("Original publisher not accessible")
  data=r.read(MAX_BYTES+1);final=r.geturl()
 if not 100<len(data)<=MAX_BYTES or b"<html" not in data[:5000].lower():
  raise ValueError("Original government webpage was not bounded HTML")
 if urllib.parse.urlsplit(final).hostname!=urllib.parse.urlsplit(url).hostname:
  raise ValueError("Government publisher provenance not preserved")
 return data,final
def inspect(registry,prior,newer,fetcher=fetch):
 rows={x["id"]:x for x in registry["official_seed_sources"]}
 old={x["source_id"]:x for x in prior["receipts"]}
 news={x["id"]:x for x in newer["source_disclosures"]}
 results=[]
 for ident,x in CHECKED.items():
  o=old.get(ident);seed=rows.get(ident)
  if not o or not seed or o["status"]!="held_http_error" or o["source_url"]!=x["url"] or seed["source_url"]!=x["url"] or o["state"]!=x["state"]:
   raise ValueError("Unresolved original government source has changed history")
  base={"id":ident,"state":x["state"],"original_url":x["url"],
   "old_retrieval_status":o["status"],"source_class":x["category"],
   "camera_points_added":0,"live_sharing_edges_added":0,
   "completed_camera_removal_independently_verified":False,
   "current_live_camera_operation_independently_verified":False,
   "policy_effective_date_verified":False}
  try:payload,url=fetcher(x["url"])
  except Exception as e:
   base["disposition"]="still_held_original_unreachable"
   base["reason"]=type(e).__name__
   results.append(base);continue
  parsed=HTMLText()
  parsed.feed(payload.decode("utf-8",errors="replace"))
  text=norm(" ".join(parsed.parts))
  missing=[a for a in x["anchors"] if norm(a) not in text]
  if missing:
   base["disposition"]="held_claim_anchor_drift"
   base["missing_anchor_count"]=len(missing)
   results.append(base);continue
  base.update(disposition="verified_source_recheck_original_HTML",
    reviewed_publisher_url=url,original_html_sha256=hashlib.sha256(payload).hexdigest(),
    corroborated_statement_anchors=len(x["anchors"]),publisher_statements_verified=True)
  results.append(base)
 co=old.get(CO_SOURCE);seed=rows.get(CO_SOURCE);latest=news.get(CO_NEW)
 if (not co or co["status"]!="held_redirect" or not seed or co["source_url"]!=seed["source_url"] or
   not latest or latest["state"]!="CO" or
   latest["publisher_statement_category"]!="announced_termination_process" or
   not latest["source_claim_anchors_verified"] or
   not re.fullmatch("[a-f0-9]{64}",latest["original_html_sha256"])):
  raise ValueError("Colorado source supersession not independently grounded")
 results.append({"id":CO_SOURCE,"state":"CO","original_url":co["source_url"],
  "old_retrieval_status":co["status"],"disposition":"superseded_original_government_source_lead",
  "newer_verified_publisher_url":latest["source_url"],
  "newer_original_html_sha256":latest["original_html_sha256"],
  "source_class":"city_2026_termination_process_supersedes_older_flock_program_website_claim",
  "old_url_independently_retrieved":False,
  "current_live_camera_operation_independently_verified":False,
  "completed_camera_removal_independently_verified":False,
  "camera_points_added":0,"live_sharing_edges_added":0})
 return {"schema_version":1,"base_source_holds":12,"results":results,
  "resolved_original_source_items":sum(r["disposition"] in
   {"verified_source_recheck_original_HTML","superseded_original_government_source_lead"} for r in results),
  "remaining_original_source_holds":12-sum(r["disposition"] in
   {"verified_source_recheck_original_HTML","superseded_original_government_source_lead"} for r in results),
  "actual_flock_camera_locations_added":0,"current_operating_status_independently_verified":False}
if __name__=="__main__":
 a=json.loads(REGISTRY.read_text(encoding="utf8"))
 b=json.loads(ORIGINALS.read_text(encoding="utf8"))
 c=json.loads(NEWER.read_text(encoding="utf8"))
 out=inspect(a,b,c)
 print("M11_RESOLVED_GOVERNMENT_ORIGINALS",json.dumps(out,sort_keys=True))
