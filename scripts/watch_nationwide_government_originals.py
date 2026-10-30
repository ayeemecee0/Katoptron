#!/usr/bin/env python3
"""All-51-jurisdiction original-government publication watch, fail closed.

Sources are exact government publication URLs selected through independent
research. This watcher only generates source receipts and state-level work queues.
A fetched page or PDF is NEVER a verified camera, policy, adoption, contract,
sharing relationship or current agency operation. No plate records are acquired.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,io,ipaddress,json,re,socket,urllib.parse,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"nationwide-government-jurisdiction-registry.json"
EXISTING=ROOT/"data"/"national-government-audit-source-portals.json"
RECOVERY=ROOT/"data"/"nationwide-recovery-government-originals-2026-10-29.json"
AGENCY_DEPTH=ROOT/"data"/"nationwide-targeted-agency-original-depth-2026-10-29.json"
REVIEWED_ADDITIONS=ROOT/"data"/"nationwide-reviewed-original-monitor-additions-2026-10-29.json"
QUALIFIED_DOCKET=ROOT/"data"/"qualified-original-government-docket-2026-10-29.json"
NATIONAL_REVIEWED=ROOT/"data"/"nationwide-original-research-leads-expanded-2026-10-29.json"
PAGE_REVIEW=ROOT/"data"/"manual-original-evidence-review-2026-10-29.json"
OUTPUT=ROOT/".katoptron-ci"/"nationwide-51-jurisdiction-original-source-watch.json"
MAX_BYTES_HTML=1_800_000
MAX_BYTES_PDF=10_000_000
MAX_PAGES=120
LEGACY_GOV_HOSTS={"www.moline.il.us","www.naperville.il.us","www.darien.il.us","www.co.routt.co.us","www.leg.state.nv.us","www.lvmpd.com","www.senate.state.oh.us","www.house.state.oh.us"}
MAX_MONITORED_SOURCES=125
MAX_PAGES=200  # bounded 159-page Nevada legislative report; only first 8 text pages sampled
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
   (p.hostname.endswith(".gov") or p.hostname=="www.state.wv.us" or p.hostname in LEGACY_GOV_HOSTS) and
   p.netloc==p.hostname and not p.fragment and not p.username and not p.password and
   len(p.path)>1 and len(p.query)<=190)
 except (ValueError,TypeError):return False
def public_dns(host):
 try:
  addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
  return bool(addresses) and all(ipaddress.ip_address(item[4][0]).is_global for item in addresses)
 except (OSError,ValueError):return False

def legacy_sources(existing):
 """Exactly the pre-curated original publishers; no unverifiable domains."""
 items=[]
 for src in existing["sources"]:
  if src.get("kind") not in ("html_index","pdf_original") or not exact(src.get("url")):
   raise ValueError("Unsafe existing original government source")
  if not re.fullmatch(r"[a-z0-9-]{8,100}",src.get("id","")) or not src.get("agency"):
   raise ValueError("Missing historical publisher identity")
  items.append({"id":"legacy-"+src["id"],"state":src["state"],
    "publisher":src["agency"],"source_url":src["url"],
    "kind":"pdf" if src["kind"]=="pdf_original" else "html",
    "origin_role":"precurated_government_publication_not_individually_reviewed"})
 if len(items)!=len({x["id"] for x in items}) or len(items)>25:
  raise ValueError("Duplicate or oversized historical publisher registry")
 return items

def recovery_sources(original=None):
 """Discovery does not grant publication authority; exact vetted 11 publisher URLs only."""
 if original is None:original=json.loads(RECOVERY.read_text(encoding="utf8"))
 if not isinstance(original,dict) or original.get("schema_version")!=1 or not isinstance(original.get("original_source_recovery_candidates"),list):
  raise ValueError("Supplementary government recovery registry invalid")
 rows=original["original_source_recovery_candidates"]
 held=set("CO FL HI IA MI MS NC NV NY UT WV".split())
 if len(rows)!=11 or {r.get("state") for r in rows}!=held:
  raise ValueError("Source recovery needs one independently located government publisher per affected state")
 seen=set();sources=[]
 for r in rows:
  if (r.get("id") in seen or r.get("state") not in STATES or r.get("kind") not in {"html","pdf"} or
      r.get("origin_role")!="supplemental_government_publisher_individual_claims_unverified" or
      r.get("operational_camera_verified") is not False or r.get("executed_contract_verified") is not False or
      not isinstance(r.get("publisher"),str) or len(r["publisher"])<12 or
      not re.fullmatch(r"[a-z]{2}-[a-z0-9-]{12,95}",r.get("id","")) or
      not exact(r.get("source_url")) or "no unverified" not in r.get("evidence_limit","")):
   raise ValueError("Supplemental original-government publication held as unsafe")
  seen.add(r["id"])
  sources.append({"id":r["id"],"state":r["state"],"publisher":r["publisher"],
    "source_url":r["source_url"],"kind":r["kind"],
    "origin_role":"supplemental_government_publisher_individual_claims_unverified"})
 return sources

def agency_depth_sources():
 """Issuer-attributed supplemental originals, never new verified Flock facts."""
 data=json.loads(AGENCY_DEPTH.read_text(encoding="utf8"))
 if data.get("schema_version")!=1 or not isinstance(data.get("sources"),list) or len(data["sources"])!=12:
  raise ValueError("Multi-document issuer registry incomplete")
 ids=set();out=[]
 for x in data["sources"]:
  if (x.get("id") in ids or not re.fullmatch(r"[a-z]{2}-[a-z0-9-]{10,100}",x.get("id","")) or
   x.get("state") not in STATES or x.get("kind") not in ("html","pdf") or
   x.get("origin_role")!="original_government_publisher_metadata_secondary_source" or
   x.get("individual_contract_status_verified") is not False or
   not x.get("government_source_confirmed_by_public_publisher_page") is True or
   not exact(x.get("source_url")) or not x.get("publisher") or not x.get("locality_key")):
   raise ValueError("Non-original source or unreviewed agency claim in depth registry")
  ids.add(x["id"]);out.append({"id":x["id"],"state":x["state"],"publisher":x["publisher"],
    "source_url":x["source_url"],"kind":x["kind"],"origin_role":x["origin_role"]})
 return out

def reviewed_addition_sources():
 """22 exact government originals, four independently page-reviewed, for safe monitoring.

 Added to *monitoring*, not newly discovered or independently confirmed new facts.
 A source's prior editorial ID, issuer, state, URL and source date must match.
 """
 data=json.loads(REVIEWED_ADDITIONS.read_text(encoding="utf8"))
 dossier=json.loads(QUALIFIED_DOCKET.read_text(encoding="utf8"))
 national=json.loads(NATIONAL_REVIEWED.read_text(encoding="utf8"))
 page_review=json.loads(PAGE_REVIEW.read_text(encoding="utf8"))
 if (data.get("schema_version")!=1 or not isinstance(data.get("sources"),list) or len(data["sources"])!=22 or
     dossier.get("schema_version")!=1 or national.get("schema_version")!=1):
  raise ValueError("Reviewed original additions not source-qualified")
 indexed={("qualified_original_government_docket",x["id"]):x for x in dossier["sources"]}
 indexed.update({("source_attributed_national_original_government_leads",x["id"]):x for x in national["leads"]})
 indexed.update({("manually_verified_original_document",x["id"]):x for x in page_review["discovery_candidates"] if x.get("status")=="original_pdf_page_visually_verified"})
 out=[];ids=set();urls=set()
 for row in data["sources"]:
  src=indexed.get((row.get("record_origin"),row.get("record_id")))
  if (not src or row.get("id") in ids or not re.fullmatch(r"reviewed-[0-9]{2}-[a-z]{2}",str(row.get("id",""))) or
      row.get("state") not in STATES or row.get("source_url") in urls or
      row.get("state")!=src.get("state") or row.get("source_url")!=src.get("source_url",src.get("url")) or
      row.get("publisher")!=src.get("agency",src.get("original_publisher")) or
      row.get("source_date")!=src.get("source_date",src.get("source_date_note")) or
      row.get("origin_role")!="original_government_historical_publication_monitor_only" or
      row.get("kind") not in ("html","pdf") or
      (row.get("record_origin")!="manually_verified_original_document" and
        (row["kind"]=="pdf") != urllib.parse.urlsplit(row["source_url"]).path.lower().endswith(".pdf")) or
      not exact(row.get("source_url")) or
      row.get("individual_document_facts_verified_by_monitor") is not False or
      row.get("operational_camera_verified_by_monitor") is not False or
      row.get("policy_change_verified_by_monitor") is not False):
   raise ValueError("New monitored original lacks independent prior source citation: "+str(row.get("id","?")))
  if row["record_origin"]=="qualified_original_government_docket":
   if src.get("watch_category")!="historical_research_only" or not src.get("source_type","").startswith("government_"):
    raise ValueError("Docket source lacks original-government provenance")
  elif row["record_origin"]=="manually_verified_original_document":
   if (row["kind"]!="pdf" or not isinstance(src.get("page"),int) or src.get("page")<1 or
       src.get("status")!="original_pdf_page_visually_verified"):
    raise ValueError("Independently page-inspected original PDF required")
  elif not src.get("source_issuer_review_status","").startswith("source_attributed_"):
   raise ValueError("National original not source-attributed")
  ids.add(row["id"]);urls.add(row["source_url"])
  out.append({"id":row["id"],"state":row["state"],"publisher":row["publisher"],
   "source_url":row["source_url"],"kind":row["kind"],"origin_role":row["origin_role"]})
 return out

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
 legacy=legacy_sources(existing)
 present={x["state"] for x in legacy}
 if not present<=set(STATES) or len(seen)+len(legacy)>MAX_MONITORED_SOURCES:raise ValueError("Existing official state evidence invalid")
 return obj["jurisdictions"],obj["official_seed_sources"],present
def fetch(src):
 url=src["source_url"]
 if not exact(url) or not public_dns(urllib.parse.urlsplit(url).hostname):raise ValueError("Original government source not approved or resolves privately")
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
 r"vehicle(?:[-_/][a-z0-9]{1,20}){0,2}[-_/]?(?:read|search|query|log|event)|"
 r"(?:case|person)[-_/]?(?:record|detail)|"
 r"(?:search|access)[-_/]?(?:log|query|read)|"
 r"raw[-_/]?(?:data|hit))",re.I)
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
 legacy=legacy_sources(existing)
 recovery=recovery_sources()
 depth=agency_depth_sources()
 reviewed=reviewed_addition_sources()
 existing_urls=[s["source_url"] for s in seeds+legacy+recovery+depth+reviewed]
 existing_ids=[s["id"] for s in seeds+legacy+recovery+depth+reviewed]
 if (len(existing_urls)!=len(set(existing_urls)) or len(existing_ids)!=len(set(existing_ids)) or
     not 100<=len(existing_urls)<=MAX_MONITORED_SOURCES):
  raise ValueError("Missing, duplicate or excessive original-government monitoring inventory")
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  receipts=list(pool.map(lambda s:inspect(s,fetcher),seeds))
  legacy_receipts=list(pool.map(lambda s:inspect(s,fetcher),legacy))
  recovery_receipts=list(pool.map(lambda s:inspect(s,fetcher),recovery))
  depth_receipts=list(pool.map(lambda s:inspect(s,fetcher),depth))
  reviewed_receipts=list(pool.map(lambda s:inspect(s,fetcher),reviewed))
 all_receipts=receipts+legacy_receipts+recovery_receipts+depth_receipts+reviewed_receipts
 original_seed_states={r["state"] for r in all_receipts if r["status"].startswith("original_")}
 planned={r["state"] for r in seeds}|existing_states
 by_state=[]
 for j in jurisdictions:
  code=j["state"]
  r=[x for x in receipts if x["state"]==code]
  old=[x for x in legacy_receipts if x["state"]==code]
  extra=[x for x in recovery_receipts if x["state"]==code]
  deep=[x for x in depth_receipts if x["state"]==code]
  newly_monitored=[x for x in reviewed_receipts if x["state"]==code]
  combined=r+old+extra+deep+newly_monitored
  accessible=sum(x["status"].startswith("original_") for x in combined)
  held=sum(x["status"].startswith("held_") for x in combined)
  source_gap=("no_monitored_government_original_accessible" if accessible==0 else
    "publisher_urls_accessible_but_agency_inventory_not_complete")
  by_state.append({"state":code,"name":j["name"],
   "research_queue_enrolled":True,
   "existing_curated_publisher_count":sum(x["state"]==code for x in existing["sources"]),
   "new_original_sources_seeded":len(r),
   "new_original_sources_retrieved":sum(x["status"].startswith("original_") for x in r),
   "new_original_sources_held":sum(x["status"].startswith("held_") for x in r),
   "source_gap":source_gap,
   "monitored_original_urls":len(combined),
   "monitored_original_accessible":accessible,
   "monitored_original_held":held,
   "held_source_ids":[x["source_id"] for x in combined if x["status"].startswith("held_")],
   "state_agency_original_inventory_verified":False,
   "statewide_flock_contract_policy_coverage_verified":False,
   "camera_coverage_claimed":False,"agency_inventory_complete":False,
   "new_same_host_policy_link_candidates_unverified":sum(
      len(x["unreviewed_same_host_policy_candidates"]) for x in combined)})
 return {"schema_version":1,"created_on":dt.datetime.now(dt.timezone.utc).date().isoformat(),
  "scope":"all_51_state_discovery_queue_and_government_source_receipts_not_coverage_claims",
  "jurisdictions_total":51,
  "states_with_existing_or_new_official_seed_sources":len(planned),
  "states_without_official_sources_seeded":sorted(set(STATES)-planned),
  "seed_receipts":receipts,"legacy_receipts":legacy_receipts,"recovery_receipts":recovery_receipts,"depth_receipts":depth_receipts,"reviewed_addition_receipts":reviewed_receipts,
  "monitored_sources_total":len(all_receipts),
  "monitored_original_accessible":sum(x["status"].startswith("original_") for x in all_receipts),
  "monitored_original_held":sum(x["status"].startswith("held_") for x in all_receipts),
  "all_source_receipts":all_receipts,
  "jurisdictions":by_state,
  "unreviewed_same_host_policy_link_candidates":sum(
   len(x["unreviewed_same_host_policy_candidates"]) for x in all_receipts),
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
  "all_government_urls_monitored":result["monitored_sources_total"],
  "supplemental_sources_monitored":len(result["recovery_receipts"]),
  "agency_depth_sources_monitored":len(result["depth_receipts"]),
  "reviewed_original_urls_newly_monitored":len(result["reviewed_addition_receipts"]),
  "reviewed_original_urls_accessible":sum(x["status"].startswith("original_") for x in result["reviewed_addition_receipts"]),
  "agency_depth_sources_accessible":sum(x["status"].startswith("original_") for x in result["depth_receipts"]),
  "supplemental_accessible":sum(x["status"].startswith("original_") for x in result["recovery_receipts"]),
  "all_originals_accessible":result["monitored_original_accessible"],
  "all_originals_held":result["monitored_original_held"],
  "states_with_no_accessible_original":sorted(row["state"] for row in result["jurisdictions"] if row["monitored_original_accessible"]==0),
  "states_needing_original_government_seed":result["states_without_official_sources_seeded"],
  "new_same_host_policy_links_to_review":result["unreviewed_same_host_policy_link_candidates"],
  "policy_adoptions_automatically_published":0},sort_keys=True))
 for row in result["all_source_receipts"]:
  print("ORIGINAL_GOVERNMENT_STATE_SOURCE",json.dumps({k:row[k] for k in ["state","source_id","status","original_sha256","pdf_pages"]},sort_keys=True))
if __name__=="__main__":main()
