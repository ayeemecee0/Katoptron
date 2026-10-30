#!/usr/bin/env python3
"""All-51-jurisdiction original-government publication watch, fail closed.

Sources are exact government publication URLs selected through independent
research. This watcher only generates source receipts and state-level work queues.
A fetched page or PDF is NEVER a verified camera, policy, adoption, contract,
sharing relationship or current agency operation. No plate records are acquired.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,io,ipaddress,json,re,socket,urllib.parse,urllib.request,urllib.error
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
ALTERNATE_RECOVERY=ROOT/"data"/"nationwide-original-government-recovery-alternates-2026-10-29.json"
UNDERREPRESENTED=ROOT/"data"/"underrepresented-state-original-government-research-2026-10-29.json"
VALUE_ORIGINALS=ROOT/"data"/"three-high-value-original-publisher-targets-2026-10-29.json"
ADDITIONAL_EDITORIAL=ROOT/"data"/"editorial-originals-intelligence-batch-2026-10-29.json"
OUTPUT=ROOT/".katoptron-ci"/"nationwide-51-jurisdiction-original-source-watch.json"
HISTORICAL_AUDIT=ROOT/"data"/"19-held-original-issuer-recovery-audit-2026-10-29.json"
HISTORICAL_RESULT=ROOT/".katoptron-ci"/"historical-19-originals-retrieval-recovery.json"
MAX_BYTES_HTML=1_800_000
MAX_BYTES_PDF=10_000_000
MAX_EXCEPTIONAL_PDF=33_000_000
LARGE_PDF_ORIGINALS={'ut-government-contract-proposal','wv-other-vendor-alpr-procurement-not-flock'}
MAX_PAGES=120
LEGACY_GOV_HOSTS={"www.moline.il.us","www.naperville.il.us","www.darien.il.us","www.co.routt.co.us","www.leg.state.nv.us","www.lvmpd.com","www.senate.state.oh.us","www.house.state.oh.us"}
MAX_MONITORED_SOURCES=150
MAX_PAGES=200  # bounded 159-page Nevada legislative report; only first 8 text pages sampled
STATES=("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
STATUS={"original_government_html_accessible","original_government_pdf_accessible",
 "held_redirect","held_http_error","held_oversized","held_wrong_format",
 "held_unreadable_original","held_timeout_or_network"}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
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
    "source_url":r["source_url"],"kind":"pdf" if r["id"]=="ia-judicial-original-opinion" else r["kind"],
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
 editorial=json.loads(ADDITIONAL_EDITORIAL.read_text(encoding="utf8"))
 if (data.get("schema_version")!=1 or not isinstance(data.get("sources"),list) or len(data["sources"])!=46 or
     dossier.get("schema_version")!=1 or national.get("schema_version")!=1):
  raise ValueError("Reviewed original additions not source-qualified")
 indexed={("qualified_original_government_docket",x["id"]):x for x in dossier["sources"]}
 indexed.update({("source_attributed_national_original_government_leads",x["id"]):x for x in national["leads"]})
 indexed.update({("manually_verified_original_document",x["id"]):x for x in page_review["discovery_candidates"] if x.get("status")=="original_pdf_page_visually_verified"})
 if editorial.get("schema_version")!=1 or len(editorial.get("sources",[]))!=14:raise ValueError("Incomplete independent original-government editorial register")
 indexed.update({("independently_reviewed_official_source",x["id"]):x for x in editorial["sources"] if x.get("independently_verified_original_publisher") is True})
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
      (row.get("record_origin") not in ("manually_verified_original_document","independently_reviewed_official_source") and
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
  elif row["record_origin"]=="independently_reviewed_official_source":
   if (src.get("evidence_tier") not in ("official_html_reviewed","official_pdf_page_inspected","official_pdf_text_inspected") or
       not src.get("unresolved_question") or not src.get("next_verification_action") or
       src.get("source_version_change_verified") is not False or src.get("new_watch_event") is not False or
       (row["kind"]=="pdf") != src["evidence_tier"].startswith("official_pdf")):
    raise ValueError("Unverified government original or false change publication")
  elif not src.get("source_issuer_review_status","").startswith("source_attributed_"):
   raise ValueError("National original not source-attributed")
  ids.add(row["id"]);urls.add(row["source_url"])
  out.append({"id":row["id"],"state":row["state"],"publisher":row["publisher"],
   "source_url":row["source_url"],"kind":row["kind"],"origin_role":row["origin_role"]})
 return out

def independent_issuer_alternatives(official):
 """Publisher indexes that contextualize held originals. Never assert exact PDF recovery."""
 data=json.loads(ALTERNATE_RECOVERY.read_text(encoding="utf8"))
 if data.get("schema_version")!=1 or len(data.get("originals",[]))!=6:
  raise ValueError("Incomplete issuer-recovery provenance evidence")
 indexed={x["id"]:x for x in official}
 found=[];ids=set();urls=set()
 for row in data["originals"]:
  prior=indexed.get(row.get("source_id"))
  if (not prior or row.get("id") in ids or not re.fullmatch(r"gov-alternate-[0-9]{2}",str(row.get("id",""))) or
      row.get("source_url") in urls or row.get("source_url")==row.get("original_url") or
      row.get("original_url")!=prior["source_url"] or row.get("state")!=prior["state"] or
      row.get("kind") not in ("html","pdf") or not exact(row.get("source_url")) or
      row.get("publisher_review")!="official_original_issuer_document_index_or_related_government_publication" or
      len(str(row.get("why_relevant","")))<35 or
      row.get("original_source_deleted") is not False or
      row.get("original_source_automatically_recovered") is not False or
      row.get("same_document_version_equivalence_proven") is not False or
      row.get("camera_operation_inferred") is not False or
      row.get("policy_adoption_inferred") is not False):
   raise ValueError("Unverified original-government fallback or changed publisher identity")
  ids.add(row["id"]);urls.add(row["source_url"])
  found.append({"id":row["id"],"state":row["state"],"publisher":row["publisher"],
    "source_url":row["source_url"],"kind":row["kind"],
    "origin_role":"same_official_issuer_alternate_original_not_equivalent_to_held_source",
    "parent_held_source_id":row["source_id"]})
 return found

def underrepresented_government_originals():
 """Original legislative/lobbying documents only: never installation or adopted policy."""
 data=json.loads(UNDERREPRESENTED.read_text(encoding="utf8"))
 if (data.get("schema_version")!=1 or len(data.get("government_originals",[]))!=3 or
     data.get("confirmed_government_operational_installations")!=0):
  raise ValueError("Invalid underserved original government source research")
 out=[];seen=set()
 for row in data["government_originals"]:
  if (row.get("id") in seen or not re.fullmatch(r"underrepresented-(?:ct|ri)-[0-9]{2}",str(row.get("id",""))) or
      row.get("state") not in ("CT","RI") or row.get("kind") not in ("html","pdf") or
      not exact(row.get("source_url")) or
      (row["kind"]=="pdf")!=urllib.parse.urlsplit(row["source_url"]).path.lower().endswith(".pdf") or
      not row.get("publisher") or len(row.get("grounded_finding",""))<80 or
      len(row.get("unknown",""))<45 or len(row.get("next_step",""))<45 or
      row.get("no_adoption_inferred") is not True or row.get("monitor_eligible") not in (True,False)):
   raise ValueError("Unreviewed original government legislative source")
  seen.add(row["id"])
  if not row["monitor_eligible"]:continue
  out.append({"id":row["id"],"state":row["state"],"source_url":row["source_url"],
   "kind":row["kind"],"publisher":row["publisher"],
   "origin_role":"government_legislative_original_not_operational_deployment"})
 return out

def original_value_sources():
 """Source-attributed government documents that generate specific verification tasks, not cameras."""
 data=json.loads(VALUE_ORIGINALS.read_text(encoding="utf8"))
 if data.get("schema_version")!=1 or len(data.get("sources",[]))!=3 or data.get("research_lead_targets")!=3:
  raise ValueError("Incomplete evidence-value government original registry")
 out=[];seen=set()
 for row in data["sources"]:
  if (row.get("id") in seen or not re.fullmatch(r"value-(?:ct|ne|sc)-[a-z0-9-]{6,75}",str(row.get("id",""))) or
      row.get("state") not in ("CT","NE","SC") or row.get("kind")!="html" or
      not exact(row.get("source_url")) or not row.get("publisher") or
      len(str(row.get("supported_finding","")))<70 or len(str(row.get("next_verification","")))<65 or
      len(str(row.get("limitations","")))<65):
   raise ValueError("Unqualified research-value government publication")
  seen.add(row["id"]);out.append({"id":row["id"],"state":row["state"],"kind":"html",
   "publisher":row["publisher"],"source_url":row["source_url"],
   "origin_role":"original_issuer_research_index_with_actionable_followup_not_camera_claim"})
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
def trusted_redirect(src,current,target):
 """Only equivalent government document paths, or Elgin's authenticated original news archive."""
 if not exact(target):return False
 a=urllib.parse.urlsplit(current);b=urllib.parse.urlsplit(target)
 host=lambda x:x.lower().removeprefix("www.")
 if host(a.hostname)!=host(b.hostname):return False
 if a.path==b.path and a.query==b.query:return True
 return (src["id"]=="reviewed-23-tx" and
  a.path.lower()=="/m/newsflash/home/detail/1824" and
  b.path.lower()=="/m/newsflash/archive/item/1824" and b.query=="arcId=2451")

def pdf_limit(src):
 return MAX_EXCEPTIONAL_PDF if src["id"] in LARGE_PDF_ORIGINALS else MAX_BYTES_PDF

class SourceTransportError(ValueError):
 """Safe metadata for original-source triage, never an editorial claim."""
 def __init__(self,kind,http_status=None,redirect_location=None):
  super().__init__(kind)
  self.http_status=http_status
  self.redirect_location=redirect_location

def fetch(src):
 """Bounded exact original fetch; one targeted retry for transient government transport errors.
 Cross-authority redirects are prohibited. Never conceal a blocked URL behind a related issuer index.
 """
 import time
 url=src["source_url"];initial=url
 if not exact(url):raise SourceTransportError("unsafe_source")
 cap=pdf_limit(src) if src["kind"]=="pdf" else MAX_BYTES_HTML
 opener=urllib.request.build_opener(NoRedirect())
 for hop in range(3):
  if not exact(url) or not public_dns(urllib.parse.urlsplit(url).hostname):
   raise SourceTransportError("unsafe_dns")
  req=urllib.request.Request(url,headers={
   "Accept":"text/html,application/pdf;q=0.9,*/*;q=0.5",
   "Accept-Language":"en-US,en;q=0.8","Accept-Encoding":"identity",
   "User-Agent":"Mozilla/5.0 (compatible; KatoptronSourceReader/1.0; +https://ayeemecee0.github.io/Katoptron/)"})
  for attempt in range(2):
   try:
    with opener.open(req,timeout=20) as res:
     if res.status!=200 or res.geturl()!=url:raise SourceTransportError("unexpected_response")
     length=res.headers.get("Content-Length")
     if length and length.isdecimal() and int(length)>cap:raise SourceTransportError("oversized_original")
     data=res.read(cap+1)
     if len(data)>cap:raise SourceTransportError("oversized_original")
     if url!=initial and src["id"]=="reviewed-23-tx" and b"Pausing City of Elgin" not in data:
      raise SourceTransportError("archive_document_identity_unconfirmed")
     return data,url
   except urllib.error.HTTPError as exc:
    if exc.code in (301,302,303,307,308):
     loc=exc.headers.get("Location","")
     target=urllib.parse.urljoin(url,loc) if loc else ""
     if target==url or not trusted_redirect(src,url,target):
      candidate=target if exact(target) else None
      raise SourceTransportError("original_redirect",http_status=exc.code,redirect_location=candidate) from None
     url=target
     break
    if exc.code in (429,500,502,503,504) and attempt==0:
     time.sleep(0.4);continue
    raise SourceTransportError("http_error",http_status=exc.code) from None
   except (TimeoutError,ConnectionError,urllib.error.URLError,OSError):
    if attempt==0:
     time.sleep(0.4);continue
    raise SourceTransportError("network_error") from None
  else:
   raise SourceTransportError("network_error")
  # A validated redirect advances to the next bounded government-origin hop.
  continue
 raise SourceTransportError("original_redirect")


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

def inspect(src,fetcher=fetch,capture_dir=None):
 record={"source_id":src["id"],"state":src["state"],"publisher":src["publisher"],
  "source_url":src["source_url"],"kind":src["kind"],"status":None,
  "original_sha256":None,"original_bytes":None,"pdf_pages":None,
  "publisher_flock_keyword_seen":False,"published_facts_verified":False,
  "device_status_verified":False,"camera_coordinates_published":False,
  "unreviewed_same_host_policy_candidates":[],"retrieved_url":None,
  "verified_same_publisher_redirect":False,
  "transport_http_status":None,"transport_redirect_candidate":None,
  "transport_failure_reason":None}
 try:
  item=fetcher(src)
  raw,final_url=item if isinstance(item,tuple) and len(item)==2 else (item,src["source_url"])
  if not exact(final_url):raise ValueError("unsafe_retrieval_url")
  record["retrieved_url"]=final_url
  record["verified_same_publisher_redirect"]=final_url!=src["source_url"]
 except Exception as err:
  reason=str(err)
  record["transport_failure_reason"]=reason if reason in ("http_error","network_error","original_redirect","oversized_original","unsafe_dns","archive_document_identity_unconfirmed","unsafe_source","unexpected_response") else "unclassified_transport_error"
  record["transport_http_status"]=getattr(err,"http_status",None)
  record["transport_redirect_candidate"]=getattr(err,"redirect_location",None)
  record["status"]="held_redirect" if reason in ("original_redirect","archive_document_identity_unconfirmed") else (
   "held_oversized" if reason=="oversized_original" else ("held_http_error" if reason=="http_error" else "held_timeout_or_network"))
  return record
 if not isinstance(raw,bytes) or len(raw)<100 or len(raw)>(pdf_limit(src) if src["kind"]=="pdf" else MAX_BYTES_HTML):
  record["status"]="held_oversized" if isinstance(raw,bytes) and len(raw)>(pdf_limit(src) if src["kind"]=="pdf" else MAX_BYTES_HTML) else "held_unreadable_original"
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
   pdf=PdfReader(io.BytesIO(raw),strict=src["id"]!="mi-state-procurement-meeting-minutes")
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
 if capture_dir is not None:
  dst=Path(capture_dir).resolve()
  if not dst.is_relative_to(ROOT) or not re.fullmatch(r"[a-z0-9_-]{7,120}",src["id"]):
   raise ValueError("Unsafe public original capture path")
  dst.mkdir(parents=True,exist_ok=True)
  (dst/(src["id"]+"."+src["kind"])).write_bytes(raw)
 return record
def watch(obj,existing,fetcher=fetch,workers=5,capture_dir=None):
 jurisdictions,seeds,existing_states=catalog(obj,existing)
 # The Iowa judicial original returns application/pdf despite an old HTML registry label.
 seeds=[{**x,"kind":"pdf"} if x["id"]=="ia-judicial-original-opinion" else x for x in seeds]
 legacy=legacy_sources(existing)
 recovery=recovery_sources()
 depth=agency_depth_sources()
 reviewed=reviewed_addition_sources()
 official=seeds+legacy+recovery+depth+reviewed
 alternates=independent_issuer_alternatives(official)
 underrepresented=underrepresented_government_originals()
 high_value=original_value_sources()
 existing_urls=[s["source_url"] for s in seeds+legacy+recovery+depth+reviewed+alternates+underrepresented+high_value]
 existing_ids=[s["id"] for s in seeds+legacy+recovery+depth+reviewed+alternates]
 if (len(existing_urls)!=len(set(existing_urls)) or len(existing_ids)!=len(set(existing_ids)) or
     not 100<=len(existing_urls)<=MAX_MONITORED_SOURCES):
  raise ValueError("Missing, duplicate or excessive original-government monitoring inventory")
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),seeds))
  legacy_receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),legacy))
  recovery_receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),recovery))
  depth_receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),depth))
  reviewed_receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),reviewed))
  alternate_receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),alternates))
  underrepresented_receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),underrepresented))
  high_value_receipts=list(pool.map(lambda s:inspect(s,fetcher,capture_dir),high_value))
 all_receipts=receipts+legacy_receipts+recovery_receipts+depth_receipts+reviewed_receipts+alternate_receipts+underrepresented_receipts+high_value_receipts
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
  alternate=[x for x in alternate_receipts if x["state"]==code]
  additional=[x for x in underrepresented_receipts if x["state"]==code]
  additional.extend(x for x in high_value_receipts if x["state"]==code)
  combined=r+old+extra+deep+newly_monitored+alternate+additional
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
  "seed_receipts":receipts,"legacy_receipts":legacy_receipts,"recovery_receipts":recovery_receipts,"depth_receipts":depth_receipts,"reviewed_addition_receipts":reviewed_receipts,"official_alternate_receipts":alternate_receipts,"underrepresented_government_receipts":underrepresented_receipts,"high_value_original_receipts":high_value_receipts,
  "monitored_sources_total":len(all_receipts),
  "monitored_original_accessible":sum(x["status"].startswith("original_") for x in all_receipts),
  "monitored_original_held":sum(x["status"].startswith("held_") for x in all_receipts),
  "all_source_receipts":all_receipts,
  "jurisdictions":by_state,
  "unreviewed_same_host_policy_link_candidates":sum(
   len(x["unreviewed_same_host_policy_candidates"]) for x in all_receipts),
  "verified_policy_adoptions_published":0}
def historical_recovery_receipts(result):
 """Cite actual retrieved issuer bytes for all 19 holds; unrelated new URLs never count."""
 dossier=json.loads(HISTORICAL_AUDIT.read_text(encoding="utf8"))
 held=dossier.get("cases",[])
 if len(held)!=19 or len({x["source_id"] for x in held})!=19:raise ValueError("Historical source cases incomplete")
 rows={x["source_id"]:x for x in result["all_source_receipts"]}
 cases=[]
 for prior in held:
  row=rows.get(prior["source_id"])
  if row is None:raise ValueError("Historical source disappeared from monitor")
  final=row.get("retrieved_url")
  source=row["source_url"]
  eligible=(row["status"].startswith("original_") and
    bool(re.fullmatch("[0-9a-f]{64}",str(row.get("original_sha256")))) and
    (final==source or (
      row.get("verified_same_publisher_redirect") is True and
      trusted_redirect({"id":row["source_id"]},source,str(final)))))
  cases.append({"source_id":row["source_id"],"state":row["state"],
    "historical_url":source,"publisher_retrieved_url":final if eligible else None,
    "current_retrieval_status":row["status"],"historical_failure":prior["historical_status"],
    "original_sha256":row["original_sha256"] if eligible else None,
    "pdf_pages":row.get("pdf_pages") if eligible else None,
    "historical_original_retrieved":bool(eligible),
    "transport_http_status":row.get("transport_http_status"),
    "transport_failure_reason":row.get("transport_failure_reason"),
    "transport_redirect_candidate":row.get("transport_redirect_candidate"),
    "same_publisher_redirect_verified":bool(eligible and final!=source),
    "new_equipment_or_policy_claim_verified":False,
    "evidence_limit":prior["evidence_limit"]})
 return {"schema_version":1,"observed_on":result["created_on"],
  "historical_total":19,"recovered":sum(x["historical_original_retrieved"] for x in cases),
  "remaining":sum(not x["historical_original_retrieved"] for x in cases),
  "historical_source_urls_deleted":0,"camera_operations_claimed":0,
  "cases":cases,
  "by_failure_reason":{k:sum(x.get("transport_failure_reason")==k for x in cases) for k in
   ("original_redirect","http_error","network_error","oversized_original","unclassified_transport_error")},
  "note":"Only original issuer bytes from the exact original or narrow proven same-document redirect count. Publisher-related indexes, other agencies, and stale search results never clear a historical original hold."}

def main():
 p=argparse.ArgumentParser();p.add_argument("--workers",type=int,default=5)
 p.add_argument("--capture-originals",action="store_true")
 p.add_argument("--out",type=Path,default=OUTPUT)
 args=p.parse_args()
 if not 1<=args.workers<=8:raise ValueError("Rate limit exceeded")
 result=watch(json.loads(REGISTRY.read_text(encoding="utf8")),json.loads(EXISTING.read_text(encoding="utf8")),workers=args.workers,
  capture_dir=(ROOT/'.katoptron-ci/nationwide-original-current') if args.capture_originals else None)
 path=args.out.resolve()
 if not path.is_relative_to(ROOT):raise ValueError("Unsafe output")
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
 historical=historical_recovery_receipts(result)
 HISTORICAL_RESULT.write_text(json.dumps(historical,indent=2)+"\n",encoding="utf8")
 print("HISTORICAL_ORIGINAL_SOURCE_RECOVERY",json.dumps({"recovered":historical["recovered"],"remaining":historical["remaining"],"total":historical["historical_total"]},sort_keys=True))
 n=sum(x["status"].startswith("original_") for x in result["seed_receipts"])
 print("NATIONWIDE_ORIGINAL_GOVERNMENT_SOURCE_WATCH",json.dumps({"jurisdictions":51,"states_with_seed_or_existing":result["states_with_existing_or_new_official_seed_sources"],
  "seed_urls":len(result["seed_receipts"]),"new_urls_accessible":n,"new_urls_held":len(result["seed_receipts"])-n,
  "all_government_urls_monitored":result["monitored_sources_total"],
  "supplemental_sources_monitored":len(result["recovery_receipts"]),
  "agency_depth_sources_monitored":len(result["depth_receipts"]),
  "reviewed_original_urls_newly_monitored":len(result["reviewed_addition_receipts"]),
  "research_value_originals_monitored":len(result["high_value_original_receipts"]),
  "research_value_originals_accessible":sum(x["status"].startswith("original_") for x in result["high_value_original_receipts"]),
  "underrepresented_new_government_originals_monitored":len(result["underrepresented_government_receipts"]),
  "underrepresented_new_government_originals_accessible":sum(x["status"].startswith("original_") for x in result["underrepresented_government_receipts"]),
  "held_original_publisher_alternates_monitored":len(result["official_alternate_receipts"]),
  "held_original_publisher_alternates_accessible":sum(x["status"].startswith("original_") for x in result["official_alternate_receipts"]),
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
