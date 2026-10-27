#!/usr/bin/env python3
"""Metadata-only six-state original public government ALPR source-watch.

Reads ONLY explicitly approved government publisher URLs and links from their
public document indexes. Never acquires plate reads, people, search logs,
private data or applies unsupported interpretations of government documents.
No auto-published findings, sharing-network edges or camera coordinates.
"""
import argparse
import datetime as dt
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PORTALS=ROOT/"data"/"national-government-audit-source-portals.json"
OUTPUT=ROOT/".katoptron-ci"/"national-government-source-candidates.json"
OFFICIAL_HOSTS={
 "www.sanbruno.ca.gov","sanmateo.courts.ca.gov","www.paloalto.gov",
 "www.greenbaywi.gov","rva.gov","www.rva.gov",
 "www.austintexas.gov","services.austintexas.gov",
 "attorneygeneral.delaware.gov","www.woodburn-or.gov",
 "www.moline.il.us","www.naperville.il.us","www.darien.il.us","www.atg.wa.gov"
}
KEYWORDS=re.compile(r"\b(?:flock|alpr|automated license plate|license plate reader|plate recognition)\b",re.I)
DOCWORDS=re.compile(r"\b(?:audit|report|review|assessment|oversight|jury|commission|policy|contract|agreement|flock|alpr|license plate|reader|privacy)\b",re.I)
SKIP=re.compile(r"\b(?:raw\s+(?:alpr\s+)?search\s+logs?|alpr\s+search\s+logs?|vehicle\s+reads?|individual\s+plate\s+reads?|plate\s+search\s+logs?|live\s+search\s+audit|raw\s+plate\s+data|user\s+audit\s+logs?)\b",re.I)
MAX_HTML=1_600_000
MAX_PDF=8_000_000
MAX_LINKS=400
MAX_RESULTS=120
MAX_PAGES=110

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*_a,**_kw):
  raise ValueError("Official government URL redirected; review exact new host")
def canonical(url,hosts):
 if not isinstance(url,str) or len(url)>900:return None
 try:
  p=urllib.parse.urlsplit(url)
  if p.scheme!="https" or p.hostname not in hosts or p.hostname not in OFFICIAL_HOSTS or p.netloc!=p.hostname or p.fragment or p.username or p.password:return None
  if p.query:
   if p.hostname!="services.austintexas.gov" or p.path!="/edims/document.cfm" or not re.fullmatch(r"id=\d{4,9}",p.query):return None
  if "/.." in p.path or "\\" in p.path or not p.path.startswith("/"):return None
  return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,p.query,""))
 except (TypeError,ValueError,AttributeError):return None

def catalog(obj):
 if not isinstance(obj,dict) or obj.get("schema_version")!=1 or not isinstance(obj.get("sources"),list):
  raise ValueError("Missing official source registry")
 rows=obj["sources"]
 if not 1<=len(rows)<=25:raise ValueError("Unbounded official publisher list")
 ids=set()
 for row in rows:
  if not isinstance(row,dict) or row.get("id") in ids or not re.fullmatch(r"[a-z0-9-]{10,90}",row.get("id","")):
   raise ValueError("Duplicate original publisher source")
  ids.add(row["id"])
  if row.get("state") not in {"CA","WI","VA","TX","DE","OR","IL","WA"} or row.get("kind") not in {"html_index","pdf_original"}:
   raise ValueError("Unexpected source state or document type")
  hosts=row.get("allowed_document_hosts")
  if not isinstance(hosts,list) or not 1<=len(hosts)<=3 or len(hosts)!=len(set(hosts)) or not set(hosts)<=OFFICIAL_HOSTS:
   raise ValueError("Unverified original government publisher domain")
  if not canonical(row.get("url"),set(hosts)):
   raise ValueError("Source index URL was not explicitly official")
  if row.get("publisher_role") not in {"police_department","government_independent_oversight","government_legal_authority"}:
   raise ValueError("Original government publisher attribution missing")
  if not isinstance(row.get("agency"),str) or not 8<=len(row["agency"])<120:
   raise ValueError("Missing publisher identity")
 return rows

class Links(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.links=[];self.open_link=None;self.tail=None
 def handle_starttag(self,tag,attrs):
  if tag=="a":
   self.tail=None
   attrs=dict(attrs)
   self.open_link={"href":attrs.get("href",""),"text":"","tail":""}
 def handle_data(self,data):
  if self.open_link is not None:self.open_link["text"]=(self.open_link["text"]+data)[:250]
  elif self.tail is not None:self.tail["tail"]=(self.tail["tail"]+data)[:170]
 def handle_endtag(self,tag):
  if tag=="a" and self.open_link is not None:
   if len(self.links)<MAX_LINKS:
    self.links.append(self.open_link)
    self.tail=self.open_link
   self.open_link=None

def kind(text,path):
 t=(text+" "+path).lower()
 if SKIP.search(t):return None
 if re.search(r"audit|assessment|oversight|jury|review|report",t):return "original_audit_or_oversight_candidate"
 if re.search(r"policy|contract|agreement|procedure|resolution|opinion",t):return "government_policy_contract_or_decision_candidate"
 if KEYWORDS.search(t):return "other_official_alpr_metadata_candidate"
 return None

def candidates(source,html):
 parser=Links()
 parser.feed(html)
 hosts=set(source["allowed_document_hosts"])
 out=[]
 for item in parser.links:
  url=canonical(urllib.parse.urljoin(source["url"],item["href"]),hosts)
  if not url or url==source["url"]:continue
  label=" ".join((item["text"]+" "+item["tail"]).split())[:190]
  topic=label+" "+urllib.parse.unquote(urllib.parse.urlsplit(url).path)
  if not KEYWORDS.search(topic):continue
  category=kind(topic,urllib.parse.urlsplit(url).path)
  if not category:continue
  if len(out)>=MAX_RESULTS:break
  out.append({"source_id":source["id"],"state":source["state"],
   "source_url":url,"original_publisher_page":source["url"],
   "linked_title":label or "(document link without descriptive text)",
   "candidate_type":category,"publisher_role":source["publisher_role"],
   "status":"official_publisher_link_metadata_only_not_source_content_reviewed"})
 unique={}
 for row in out:unique.setdefault(row["source_url"],row)
 return sorted(unique.values(),key=lambda r:(r["candidate_type"],r["source_url"]))

def fetch(source,opener=None):
 url=source["url"]
 if not canonical(url,set(source["allowed_document_hosts"])):raise ValueError("Source not approved")
 opener=opener or urllib.request.build_opener(NoRedirect())
 req=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-original-government-publication-index/1.0",
  "Accept":"text/html,application/pdf"})
 with opener.open(req,timeout=25) as response:
  if response.status!=200 or response.geturl()!=url:raise ValueError("Changed official publisher URL")
  content_type=response.headers.get("Content-Type","").split(";")[0].lower()
  limit=MAX_HTML if source["kind"]=="html_index" else MAX_PDF
  body=response.read(limit+1)
 if len(body)<100 or len(body)>limit:raise ValueError("Empty or unbounded public original")
 if source["kind"]=="html_index":
  if content_type not in {"text/html","application/xhtml+xml"} or not body.lstrip()[:80].lower().startswith((b"<!doctype",b"<html",b"<?xml")):
   raise ValueError("Original public index is not HTML")
 else:
  if not body.startswith(b"%PDF-"):raise ValueError("Original publisher report is not a PDF")
 return body

def receipt(source,body,reader=PdfReader):
 if source["kind"]!="pdf_original" or not isinstance(body,bytes) or not body.startswith(b"%PDF-") or len(body)>MAX_PDF:
  raise ValueError("Invalid original PDF preflight")
 doc=reader(io.BytesIO(body),strict=True)
 if doc.is_encrypted or not 1<=len(doc.pages)<=MAX_PAGES:raise ValueError("Encrypted/unbounded PDF")
 return {"id":source["id"],"state":source["state"],"source_url":source["url"],
  "sha256":hashlib.sha256(body).hexdigest(),"pages":len(doc.pages),"bytes":len(body),
  "status":"machine_original_pdf_receipt_no_content_claims"}

def curated_original_urls():
 """Only exact URLs already in source-pinned, individually reviewed catalogs.

 The current discovery scan NEVER turns an unseen report into a verified one.
 Existing reviews remain subject to their own byte/page CI verifiers.
 """
 seen=set()
 for name in ("verified-national-government-oversight.json","verified-agency-published-alpr-audits.json"):
  obj=json.loads((ROOT/"data"/name).read_text(encoding="utf-8"))
  if obj.get("schema_version")!=1 or not isinstance(obj.get("reports"),list):
   raise ValueError("Incomplete individually reviewed original source catalog")
  for r in obj["reports"]:
   url=r.get("source_url")
   if not isinstance(url,str) or not re.fullmatch(r"[0-9a-f]{64}",r.get("content_sha256","")):
    raise ValueError("Unverified original content cannot be marked reviewed")
   if url in seen:raise ValueError("Reviewed original duplicated across independent attribution catalogs")
   seen.add(url)
 return seen

def run(sources,fetcher=fetch,reader=PdfReader,reviewed=None):
 results=[];all_candidates=[];pdfs=[]
 for source in sources:
  try:
   body=fetcher(source)
   if source["kind"]=="html_index":
    html=body.decode("utf-8",errors="replace")
    links=candidates(source,html)
    results.append({"id":source["id"],"state":source["state"],"status":"official_index_accessible",
                    "links_found":len(links),"sha256_of_fetched_index":hashlib.sha256(body).hexdigest()})
    all_candidates.extend(links)
   else:
    record=receipt(source,body,reader)
    pdfs.append(record)
    results.append({"id":source["id"],"state":source["state"],"status":"official_original_pdf_accessible",
                    "links_found":0})
  except Exception as exc:
   results.append({"id":source["id"],"state":source["state"],
    "status":"official_source_unavailable_needs_recheck","error_type":type(exc).__name__,"links_found":0})
 dedup={}
 for row in all_candidates:
  dedup.setdefault(row["source_url"],row)
 checked=reviewed if reviewed is not None else curated_original_urls()
 if not isinstance(checked,set):raise ValueError("Invalid reviewed-original registry")
 priorities={"original_audit_or_oversight_candidate":0,
             "government_policy_contract_or_decision_candidate":1,
             "other_official_alpr_metadata_candidate":2}
 ranked=sorted(dedup.values(),key=lambda x:(x["source_url"] in checked,
              priorities[x["candidate_type"]],x["state"],x["source_url"]))
 for item in ranked:
  item["review_status"]=(
    "already_individually_page_reviewed_with_pinned_original"
    if item["source_url"] in checked else "new_original_link_needs_individual_content_review")

 return {"schema_version":1,"generated_at":dt.datetime.now(dt.timezone.utc).isoformat(),
  "scope":"original_official_government_link_metadata_and_machine_receipts_only",
  "states_monitored":len({s["state"] for s in sources}),
  "government_publishers_monitored":len(sources),
  "source_checks":results,"linked_candidates":ranked[:MAX_RESULTS],
  "linked_candidates_truncated":len(ranked)>MAX_RESULTS,
  "unreviewed_original_link_candidates":sum(x["source_url"] not in checked for x in ranked),
  "already_reviewed_original_links":sum(x["source_url"] in checked for x in ranked),
  "original_pdf_receipts":pdfs,"substantive_facts_auto_published":0,
  "camera_locations_auto_published":0,"sharing_edges_auto_published":0}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--out",type=Path,default=OUTPUT)
 opts=parser.parse_args()
 src=catalog(json.loads(PORTALS.read_text(encoding="utf-8")))
 result=run(src)
 p=opts.out.resolve()
 if not p.is_relative_to(ROOT):raise ValueError("Source watch output must remain in CI workspace")
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 for s in result["source_checks"]:print("GOVERNMENT_SOURCE",s["id"],s["status"],"LINKS",s["links_found"])
 print("STATES",result["states_monitored"],"PUBLISHER_SOURCES",len(src),
  "LINK_CANDIDATES",len(result["linked_candidates"]),
  "UNREVIEWED_LINKS",result["unreviewed_original_link_candidates"],
  "ALREADY_REVIEWED_LINKS",result["already_reviewed_original_links"],
  "DIRECT_ORIGINAL_PDF_RECEIPTS",len(result["original_pdf_receipts"]))
 print("NEW FACTS",result["substantive_facts_auto_published"],"CAMERA PINS",
  result["camera_locations_auto_published"],"SHARING EDGES",result["sharing_edges_auto_published"])
 for candidate in result["linked_candidates"]:
  if candidate["review_status"]=="new_original_link_needs_individual_content_review":
   # Exact official link metadata only. Safe to include in public CI logs.
   print("REVIEW_ORIGINAL_CANDIDATE",candidate["state"],candidate["source_id"],
         candidate["candidate_type"],candidate["source_url"],
         "TITLE",candidate["linked_title"][:100])
 print("SOURCE_WATCH_ARTIFACT",p.relative_to(ROOT))
if __name__=="__main__":
 try:main()
 except Exception as exc:
  raise SystemExit("Source watch held: "+type(exc).__name__+(" "+str(exc)[:160] if isinstance(exc,ValueError) else "")) from None
