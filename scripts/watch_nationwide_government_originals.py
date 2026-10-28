#!/usr/bin/env python3
"""All-51-jurisdiction original-government publication watch, fail closed.

Sources are exact government publication URLs selected through independent
research. This watcher only generates source receipts and state-level work queues.
A fetched page or PDF is NEVER a verified camera, policy, adoption, contract,
sharing relationship or current agency operation. No plate records are acquired.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,io,json,re,urllib.parse,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"nationwide-government-jurisdiction-registry.json"
EXISTING=ROOT/"data"/"national-government-audit-source-portals.json"
OUTPUT=ROOT/".katoptron-ci"/"nationwide-51-jurisdiction-original-source-watch.json"
MAX_BYTES_HTML=1_800_000
MAX_BYTES_PDF=10_000_000
MAX_PAGES=120
STATES=("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
STATUS={"original_government_html_accessible","original_government_pdf_accessible",
 "held_redirect","held_http_error","held_oversized","held_wrong_format",
 "held_unreadable_original","held_timeout_or_network"}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("original_redirect")
def exact(url):
 if not isinstance(url,str) or len(url)>950 or re.search(r"%2e|\\|/\.\.?/",url.split("?")[0],re.I):return False
 try:
  p=urllib.parse.urlsplit(url)
  return (p.scheme=="https" and p.hostname is not None and
   (p.hostname.endswith(".gov") or p.hostname=="www.state.wv.us") and
   p.netloc==p.hostname and not p.fragment and not p.username and not p.password and
   len(p.path)>1 and len(p.query)<=190)
 except (ValueError,TypeError):return False
def catalog(obj,existing):
 if (not isinstance(obj,dict) or obj.get("schema_version")!=1 or
     obj.get("universe")!="50_us_states_plus_district_of_columbia" or
     not isinstance(obj.get("jurisdictions"),list) or len(obj["jurisdictions"])!=51 or
     not isinstance(obj.get("official_seed_sources"),list) or
     not isinstance(existing,dict) or existing.get("schema_version")!=1):
  raise ValueError("Nationwide source registry not complete")
 state_names={}
 for x in obj["jurisdictions"]:
  if (x.get("state") in state_names or x.get("state") not in STATES or
     not isinstance(x.get("name"),str) or not 3<=len(x["name"])<=24 or
     x.get("discovery_status")!="enrolled_state_research_queue" or
     not isinstance(x.get("search_terms"),list) or len(x["search_terms"])!=2):
   raise ValueError("Invalid or duplicated US state research jurisdiction")
  state_names[x["state"]]=x["name"]
 if set(state_names)!=set(STATES):raise ValueError("All 50 states and DC must be represented")
 seen=set()
 for src in obj["official_seed_sources"]:
  if (src.get("state") not in state_names or src.get("id") in seen or
      not re.fullmatch("[a-z]{2}-[a-z0-9-]{9,95}",src.get("id","")) or
      src.get("kind") not in {"html","pdf"} or
      src.get("origin_role")!="government_authored_publication_not_independently_page_reviewed" or
      not exact(src.get("source_url")) or
      not isinstance(src.get("publisher"),str) or len(src["publisher"])<10 or
      "no unverified" not in src.get("evidence_limit","")):
   raise ValueError("Ungrounded original government publication source")
  seen.add(src["id"])
 if len(obj["official_seed_sources"])<20:raise ValueError("Too few new state sources")
 present={x["state"] for x in existing.get("sources",[])}
 if not present<=set(STATES):raise ValueError("Existing official state evidence invalid")
 return obj["jurisdictions"],obj["official_seed_sources"],present
def fetch(src):
 url=src["source_url"]
 if not exact(url):raise ValueError("Original government source not approved")
 req=urllib.request.Request(url,headers={"Accept":"text/html,application/pdf",
   "User-Agent":"Katoptron-US-national-original-government-source-observation/1.0"})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=22) as res:
   if res.status!=200 or res.geturl()!=url:raise ValueError("unexpected_response")
   data=res.read((MAX_BYTES_PDF if src["kind"]=="pdf" else MAX_BYTES_HTML)+1)
 except urllib.error.HTTPError as exc:
  raise ValueError("http_error") from None
 return data

class PolicyLinks(HTMLParser):
 """Bounded original government href discovery, never source fact promotion."""
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.href=None
  self.buf=[]
  self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=="a":
   self.href=dict(attrs).get("href","")
   self.buf=[]
 def handle_data(self,data):
  if self.href is not None and len(self.buf)<8:
   self.buf.append(data)
 def handle_endtag(self,tag):
  if tag=="a" and self.href is not None:
   self.links.append((self.href," ".join(" ".join(self.buf).split())[:170]))
   self.href=None
   self.buf=[]
POLICY_ANCHOR=re.compile(
 r"\b(?:flock|alpr|license[ -]?plate|plate[ -]?reader|"
 r"(?:surveillance|camera).{0,25}(?:policy|ordinance)|"
 r"(?:policy|ordinance).{0,25}(?:surveillance|camera))\b",re.I)
POLICY_ROLE=re.compile(r"\b(?:policy|general\s+order|ordinance|"
 r"(?:alpr|flock|lpr).{0,25}(?:document|report|audit|transparency))\b",re.I)
SENSITIVE_PATH=re.compile(r"(?:plate[-_/]?(?:read|search)|"
 r"vehicle[-_/]?(?:query|log|event)|"
 r"(?:case|person)[-_/]?(?:record|detail)|"
 r"raw[-_/]?(?:data|hit)|access[-_/]?log)",re.I)
def policy_candidates(original,raw):
 """Only same-host official government document-link candidates.

 Explicitly NOT original content verification, adoption, Flock deployment,
 legal effective date or an exhaustive agency directory. Search leads
 remain a separate review layer; unsafe/cross-host redirects are excluded.
 """
 try:
  base=urllib.parse.urlsplit(original)
  if not exact(original) or not isinstance(raw,bytes) or len(raw)>MAX_BYTES_HTML:
   return []
  p=PolicyLinks();p.feed(raw.decode("utf8",errors="replace"))
  found=[];seen=set()
  for href,title in p.links:
   if not title or not href or not POLICY_ANCHOR.search(title) or not POLICY_ROLE.search(title):
    continue
   url=urllib.parse.urljoin(original,href)
   u=urllib.parse.urlsplit(url)
   if u.hostname!=base.hostname or not exact(url) or SENSITIVE_PATH.search(u.path):
    continue
   if url==original or url in seen:continue
   seen.add(url)
   found.append({"candidate_url":url,"anchor_text":title,
    "evidence_tier":"government_same_host_link_unverified_individual_document",
    "individually_reviewed":False,"policy_adopted_verified":False,
    "flock_vendor_verified":False,"camera_locations_verified":False,
    "effective_date_verified":False})
   if len(found)>=12:break
  return found
 except (ValueError,TypeError):
  return []

def inspect(src,fetcher=fetch):
 record={"source_id":src["id"],"state":src["state"],"publisher":src["publisher"],
  "source_url":src["source_url"],"kind":src["kind"],"status":None,
  "original_sha256":None,"original_bytes":None,"pdf_pages":None,
  "publisher_flock_keyword_seen":False,"published_facts_verified":False,
  "device_status_verified":False,"camera_coordinates_published":False,
  "unreviewed_same_host_policy_candidates":[]}
 try:raw=fetcher(src)
 except Exception as err:
  reason=str(err)
  record["status"]="held_redirect" if reason=="original_redirect" else (
   "held_http_error" if reason=="http_error" else "held_timeout_or_network")
  return record
 if not isinstance(raw,bytes) or len(raw)<100 or len(raw)>(MAX_BYTES_PDF if src["kind"]=="pdf" else MAX_BYTES_HTML):
  record["status"]="held_oversized" if isinstance(raw,bytes) and len(raw)>100 else "held_unreadable_original"
  return record
 if src["kind"]=="html":
  if b"<html" not in raw[:1600].lower() and b"<!doctype html" not in raw[:1600].lower():
   record["status"]="held_wrong_format";return record
  text=raw.decode("utf8",errors="replace").casefold()
  record["publisher_flock_keyword_seen"]="flock" in text
  record["unreviewed_same_host_policy_candidates"]=policy_candidates(src["source_url"],raw)
  record["status"]="original_government_html_accessible"
 else:
  if not raw.startswith(b"%PDF-"):record["status"]="held_wrong_format";return record
  try:
   pdf=PdfReader(io.BytesIO(raw),strict=True)
   if pdf.is_encrypted or not 1<=len(pdf.pages)<=MAX_PAGES:raise ValueError("invalid_pdf")
   record["pdf_pages"]=len(pdf.pages)
   # A source could mention Flock in one of many government agenda pages.
   # Do not treat a keyword match as evidence of an approved agreement.
   for page in pdf.pages[:min(8,len(pdf.pages))]:
    if "flock" in (page.extract_text() or "").casefold():
     record["publisher_flock_keyword_seen"]=True;break
  except Exception:
   record["status"]="held_unreadable_original";record["pdf_pages"]=None;return record
  record["status"]="original_government_pdf_accessible"
 record["original_sha256"]=hashlib.sha256(raw).hexdigest()
 record["original_bytes"]=len(raw)
 return record
def watch(obj,existing,fetcher=fetch,workers=5):
 jurisdictions,seeds,existing_states=catalog(obj,existing)
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  receipts=list(pool.map(lambda s:inspect(s,fetcher),seeds))
 original_seed_states={r["state"] for r in receipts if r["status"].startswith("original_")}
 planned={r["state"] for r in seeds}|existing_states
 by_state=[]
 for j in jurisdictions:
  code=j["state"]
  r=[x for x in receipts if x["state"]==code]
  by_state.append({"state":code,"name":j["name"],
   "research_queue_enrolled":True,
   "existing_curated_publisher_count":sum(x["state"]==code for x in existing["sources"]),
   "new_original_sources_seeded":len(r),
   "new_original_sources_retrieved":sum(x["status"].startswith("original_") for x in r),
   "new_original_sources_held":sum(x["status"].startswith("held_") for x in r),
   "source_gap":"needs_authenticated_government_original" if code not in planned else
     "publisher_monitoring_started_not_statewide_evidence_complete",
   "camera_coverage_claimed":False,"agency_inventory_complete":False,
   "new_same_host_policy_link_candidates_unverified":sum(
      len(x["unreviewed_same_host_policy_candidates"]) for x in r)})
 return {"schema_version":1,"created_on":dt.datetime.now(dt.timezone.utc).date().isoformat(),
  "scope":"all_51_state_discovery_queue_and_government_source_receipts_not_coverage_claims",
  "jurisdictions_total":51,
  "states_with_existing_or_new_official_seed_sources":len(planned),
  "states_without_official_sources_seeded":sorted(set(STATES)-planned),
  "seed_receipts":receipts,"jurisdictions":by_state,
  "unreviewed_same_host_policy_link_candidates":sum(
   len(x["unreviewed_same_host_policy_candidates"]) for x in receipts),
  "verified_policy_adoptions_published":0}
def main():
 p=argparse.ArgumentParser();p.add_argument("--workers",type=int,default=5)
 p.add_argument("--out",type=Path,default=OUTPUT)
 args=p.parse_args()
 if not 1<=args.workers<=8:raise ValueError("Rate limit exceeded")
 result=watch(json.loads(REGISTRY.read_text(encoding="utf8")),json.loads(EXISTING.read_text(encoding="utf8")),workers=args.workers)
 path=args.out.resolve()
 if not path.is_relative_to(ROOT):raise ValueError("Unsafe output")
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
 n=sum(x["status"].startswith("original_") for x in result["seed_receipts"])
 print("NATIONWIDE_ORIGINAL_GOVERNMENT_SOURCE_WATCH",json.dumps({"jurisdictions":51,"states_with_seed_or_existing":result["states_with_existing_or_new_official_seed_sources"],
  "seed_urls":len(result["seed_receipts"]),"new_urls_accessible":n,"new_urls_held":len(result["seed_receipts"])-n,
  "states_needing_original_government_seed":result["states_without_official_sources_seeded"],
  "new_same_host_policy_links_to_review":result["unreviewed_same_host_policy_link_candidates"],
  "policy_adoptions_automatically_published":0},sort_keys=True))
 for row in result["seed_receipts"]:
  print("ORIGINAL_GOVERNMENT_STATE_SOURCE",json.dumps({k:row[k] for k in ["state","source_id","status","original_sha256","pdf_pages"]},sort_keys=True))
if __name__=="__main__":main()
