#!/usr/bin/env python3
"""Original government HTML -> source-attributed, bounded, publishable facts.

Only independently selected official publisher URLs and literal, claim-specific
visible source anchors qualify. No guessing policy effective dates, camera
coordinates, sharing edges, live equipment status or vendor installation.
No private plate or search data collected. No database credentials needed.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,html,json,re,unicodedata
from html.parser import HTMLParser
from pathlib import Path
import urllib.parse,urllib.request
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data"/"agency-official-html-source-candidates-2026-10-27.json"
OUT=ROOT/".katoptron-ci"/"new-original-agency-publication-verification.json"
MAX_BYTES=2_000_000
STATES="AR ID KY NM TN IN MN MO MA ME CO".split()
STATUS={"agency_reports_flock_use","announced_not_renewing","agency_reports_removed","announced_termination_process"}
class PlainText(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.blocks=[];self.off=0
 def handle_starttag(self,tag,attrs):
  if tag in {"script","style","noscript","svg","template"}:self.off+=1
 def handle_endtag(self,tag):
  if tag in {"script","style","noscript","svg","template"}:self.off=max(0,self.off-1)
 def handle_data(self,data):
  if not self.off and data.strip():self.blocks.append(data.strip())
def normalize(value):
 value=unicodedata.normalize("NFKC",html.unescape(value))
 value=value.replace("’","'").replace("‘","'").replace("\xa0"," ")
 return " ".join(value.casefold().split())
def publisher_url(url):
 try:
  u=urllib.parse.urlsplit(url)
  return (u.scheme=="https" and not u.username and not u.password and
   u.port is None and u.hostname and
   u.hostname.endswith(".gov") and u.netloc==u.hostname and
   not u.fragment and not re.search(r"%2e|\\|/\.\.?/",u.path,re.I) and
   len(u.path)>3 and not re.search(r"(?:plate[-_]?reads|search[-_]?logs|vehicle[-_]?queries)",u.path,re.I))
 except (ValueError,TypeError):return False
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  src=urllib.parse.urlsplit(req.full_url)
  dest=urllib.parse.urlsplit(newurl)
  if dest.scheme!="https" or dest.hostname not in {src.hostname,src.hostname.removeprefix("www."),"www."+src.hostname} or not publisher_url(newurl):
   raise ValueError("Government publisher redirect held for review")
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(url):
 if not publisher_url(url):raise ValueError("Government source URL invalid")
 req=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-original-government-ALPR-evidence-review/1.0",
  "Accept":"text/html"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=23) as resp:
  if resp.status!=200:raise ValueError("Government original returned error")
  final=resp.geturl()
  if not publisher_url(final):raise ValueError("Government source changed publisher")
  raw=resp.read(MAX_BYTES+1)
 if not 100<len(raw)<=MAX_BYTES or b"<html" not in raw[:2000].lower():
  raise ValueError("Original not bounded government HTML")
 return raw,final
def validate_catalog(doc):
 if doc.get("schema_version")!=1 or len(doc.get("records",[]))!=11:
  raise ValueError("Original government candidate registry incomplete")
 seen=set();states=set()
 for row in doc["records"]:
  if (row.get("id") in seen or row.get("state") not in STATES or
      row.get("state") in states or row.get("status") not in STATUS or
      not publisher_url(row.get("source_url")) or
      not 8<=len(row.get("agency",""))<=120 or
      not 25<=len(row.get("anchor",""))<=220 or
      not isinstance(row.get("additional_source_anchors"),list) or
      not 1<=len(row["additional_source_anchors"])<=4 or
      any(not 15<=len(a)<=160 for a in row["additional_source_anchors"]) or
      row.get("policy_adoption_verified") is not False or
      row.get("actual_vendor_config_verified") is not False or
      row.get("exact_camera_coordinates_added")!=0 or
      row.get("active_sharing_edges_added")!=0):
   raise ValueError("Unapproved agency authority or unsupported claims")
  seen.add(row["id"]);states.add(row["state"])
 if len(states)!=11 or set(STATES)!=states:raise ValueError("Ten new states plus Colorado missing")
 return doc["records"]
def inspect(row,fetcher=fetch):
 base={"id":row["id"],"state":row["state"],"agency":row["agency"],
       "source_url":row["source_url"],"source_date":row["source_date"],
       "publisher_status":row["status"],"summary":row["summary"],
       "verified_original_html":False,"status":"held_source_unavailable",
       "original_html_sha256":None,"claim_specific_anchors_verified":False,
       "current_equipment_or_technical_configuration_independently_verified":False,
       "verified_camera_coordinates_added":0,"verified_live_sharing_edges_added":0,
       "legal_policy_adoption_verified":False}
 try:raw,final=fetcher(row["source_url"])
 except Exception as exc:
  base["hold_type"]=type(exc).__name__;return base
 if not isinstance(raw,bytes) or len(raw)>MAX_BYTES or not publisher_url(final):
  base["status"]="held_invalid_original";return base
 parser=PlainText()
 try:parser.feed(raw.decode("utf-8",errors="replace"))
 except Exception:
  base["status"]="held_html_parse";return base
 text=normalize(" ".join(parser.blocks))
 # Underlying page must contain the exact agency statement and independent
 # corroborating numeric/contract/status anchors. No LLM extraction, no nearby
 # text heuristic, no invented signatures or official policy effective dates.
 required=[row["anchor"],*row["additional_source_anchors"]]
 missing=[s for s in required if normalize(s) not in text]
 if missing:
  base["status"]="held_original_source_claim_drift"
  base["missing_claim_anchors"]=len(missing);return base
 base.update(status="verified_agency_published_html_statements",
  source_url=final,verified_original_html=True,
  original_html_sha256=hashlib.sha256(raw).hexdigest(),
  claim_specific_anchors_verified=True,
  corroborated_anchor_count=len(required),
  evidence_tier="source_attributed_original_government_html_not_original_pdf_page_review",
  source_freshness_type="publisher_statement_as_observed_not_live_camera_telemetry",
  device_count_individually_verified=0)
 return base
def run(catalog,fetcher=fetch,workers=5):
 rows=validate_catalog(catalog)
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  results=list(pool.map(lambda item:inspect(item,fetcher),rows))
 verified=[r for r in results if r["verified_original_html"]]
 return {"schema_version":1,
  "source_as_of":dt.datetime.now(dt.timezone.utc).isoformat(),
  "scope":"government_HTML_source_claims_not_live_operational_camera_installation",
  "verified_agency_publisher_statements":len(verified),
  "states_new_source_disclosures":sorted({r["state"] for r in verified}),
  "verified_agency_policy_pdf_dossiers_added":0,
  "verified_exact_camera_points_added":0,
  "verified_live_sharing_edges_added":0,
  "verified_legal_policy_effective_dates_added":0,
  "records":results}
def main():
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT)
 args=p.parse_args();path=args.out.resolve()
 if not path.is_relative_to(ROOT):raise ValueError("Output outside repository")
 result=run(json.loads(CATALOG.read_text(encoding="utf8")))
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print("GOVERNMENT_ORIGINAL_HTML_CONVERSION",json.dumps({
  "verified_publisher_statements":result["verified_agency_publisher_statements"],
  "new_states":result["states_new_source_disclosures"],
  "held":len(result["records"])-result["verified_agency_publisher_statements"],
  "verified_camera_points":0,"policy_pdf_dossiers_added":0},sort_keys=True))
 for r in result["records"]:
  print("SOURCE_QUALIFIED_AGENCY_RESULT",json.dumps({k:r.get(k) for k in
   ("id","state","agency","status","original_html_sha256","source_url","publisher_status",
    "corroborated_anchor_count","hold_type","missing_claim_anchors")},sort_keys=True))
if __name__=="__main__":main()
