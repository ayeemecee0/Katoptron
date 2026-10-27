#!/usr/bin/env python3
"""Bounded original-government Flock document acquisition.

Auto-publishes NO contract facts, sharing grants, council votes, retention
policy changes, or camera coordinates. Discovers original government document
links and possible recipient names to a PRIVATE review queue. Publishes only
aggregate acquisition metrics.
"""
import csv
import datetime as dt
import hashlib
import io
import ipaddress
import json
import os
import re
import socket
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from government_domain_registry import valid_https_url

SEEDS=(
 ("https://portagein.gov/547/Flock-Information-Center","Portage, IN"),
 ("https://www.shakopeemn.gov/public_safety/police_department/reports___transparency.php","Shakopee, MN"),
 ("https://www.paloalto.gov/Departments/Police/Public-Information-Portal/Automated-License-Plate-Recognition-ALPR","Palo Alto, CA"),
 ("https://www.alexandriava.gov/police-department/license-plate-reader-dashboard-and-response-to-city-council-questions-on-flock","Alexandria, VA"),
 ("https://www.cityofwoodland.gov/1704/Automated-License-Plate-Readers-ALPR","Woodland, CA"),
)
MAX_PAGE=900_000
MAX_CSV=250_000
MAX_LINKS_PER_PAGE=55
USER_AGENT="Katoptron-GovernmentDocumentIndex/1.0 (public source research)"
PATTERNS=(
 ("sharing_export",re.compile(r"shar(?:e|ed|ing)|network.*access|data.access|authorization|\bmou\b",re.I)),
 ("contract",re.compile(r"contract|agreements?|purchase order|invoice|procure|pricing|costs?",re.I)),
 ("policy",re.compile(r"policy|policies|retention|procedures?",re.I)),
 ("audit",re.compile(r"audits?|compliance|independent.review",re.I)),
 ("meeting_record",re.compile(r"meeting|council|agenda|minutes|staff.report|resolution",re.I)),
)
LIKELY_RESOURCE=re.compile(r"\.(?:pdf|csv|xlsx?|docx?)(?:$|\?)",re.I)
# Top-level city-site navigation often contains "Privacy Policy", "City Auditor",
# "Auditorium", or "Contract Administration" links. Those aren't Flock
# documents merely because the parent page describes ALPR.
DIRECT_FLOCK_LABEL=re.compile(r"\bflock\b|\balpr\b|(?:automated|automatic)\s+licen[cs]e\s+plate\s+read|\blpr\b",re.I)
def relevant_document_link(label,url,kind):
 if kind in ("contract","policy","audit","sharing_export"):
  title_and_path=label+" "+urllib.parse.urlsplit(url).path.replace("-"," ")
  if not DIRECT_FLOCK_LABEL.search(title_and_path):
   return False
 return True


class Links(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.links=[]
  self.active=None
  self.title=""
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":
   self.active=[a.get("href") or "",a.get("title") or "",[]]
 def handle_data(self,data):
  if self.active is not None:self.active[2].append(data)
 def handle_endtag(self,tag):
  if tag=="a" and self.active is not None:
   href,title,text=self.active
   self.links.append((href," ".join((title+" "+" ".join(text)).split())[:400]))
   self.active=None

def public_dns(host):
 try:
  records=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
  return bool(records) and all(ipaddress.ip_address(r[4][0]).is_global for r in records)
 except (OSError,ValueError):return False

def normalize_url(url,base,source_host=None):
 url=urllib.parse.urljoin(base,str(url))
 p=valid_https_url(url)
 if not p or p.fragment or not p.hostname.endswith(".gov"):
  # fragments removed below for valid pages, but untrusted custom domains
  # and unapproved redirects are never made original government sources.
  if not p or not p.hostname.endswith(".gov"):return None
 p_host=p.hostname.lower()
 if source_host and p_host.removeprefix("www.")!=source_host.removeprefix("www."):
  return None
 out=urllib.parse.urlunsplit(("https",p_host,p.path or "/",p.query,""))
 return out if len(out)<=1500 else None

class SameGovRedirect(urllib.request.HTTPRedirectHandler):
 def __init__(self,root_host):
  super().__init__()
  self.root=root_host.removeprefix("www.")
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  p=valid_https_url(newurl)
  if not p or not p.hostname.endswith(".gov") or p.hostname.removeprefix("www.")!=self.root:
   raise ValueError("Redirect leaves original verified government authority")
  if not public_dns(p.hostname):
   raise ValueError("Government redirect does not resolve to a public IP")
  return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch(url,limit=MAX_PAGE):
 p=valid_https_url(url)
 if not p or not p.hostname.endswith(".gov") or not public_dns(p.hostname):
  raise ValueError("Non-government or private-network source rejected")
 req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html,text/csv,application/octet-stream,*/*"})
 opener=urllib.request.build_opener(SameGovRedirect(p.hostname))
 with opener.open(req,timeout=17) as res:
  if res.status!=200:raise ValueError("Original source HTTP "+str(res.status))
  data=res.read(limit+1)
  if len(data)>limit:raise ValueError("Original source over bounded limit")
  return data,res.headers.get("Content-Type","")

def classify(label,url):
 s=label+" "+urllib.parse.urlsplit(url).path.replace("-","_")
 for kind,pattern in PATTERNS:
  if pattern.search(s):return kind
 return None

def extract_links(html,root,jurisdiction):
 source_host=urllib.parse.urlsplit(root).hostname
 body=html.decode("utf-8","replace")
 if not re.search(r"\bflock\b|(?:automated|automatic) license plate read|\bALPR\b",body,re.I):
  raise ValueError("Source is not an ALPR/Flock program page")
 parsed=Links();parsed.feed(body)
 digest=hashlib.sha256(html).hexdigest()
 result={}
 for raw,label in parsed.links:
  url=normalize_url(raw,root,source_host)
  if not url or url==root:continue
  kind=classify(label,url)
  if not kind:continue
  if not relevant_document_link(label,url,kind):continue
  if not LIKELY_RESOURCE.search(url) and not re.search(r"download|flock|alpr|sharing|policy|contract|council|audit",label,re.I):
   continue
  if not label:label="Original government document link: "+kind
  if len(label)<3:continue
  result[url]={
   "document_url":url,
   "government_page_url":root,
   "jurisdiction_label":jurisdiction,
   "document_class":kind,
   "link_label":label[:400],
   "source_page_sha256":digest,
   "confidence":"original_government_link_only",
   "review_status":"requires_document_review"
  }
  if len(result)>=MAX_LINKS_PER_PAGE:break
 return list(result.values())

def csv_recipient_names(payload):
 if len(payload)>MAX_CSV:return []
 try:
  raw=payload.decode("utf-8-sig")
  dialect=csv.Sniffer().sniff(raw[:2048],delimiters=",;\t")
  records=csv.DictReader(io.StringIO(raw),dialect=dialect)
  headers={re.sub(r"[^a-z0-9]+"," ",h.lower()).strip():h for h in (records.fieldnames or [])}
  if any(re.search(r"plate|vin|vehicle|driver|address|search",h) for h in headers):return []
  recipient=next((headers[x] for x in ("shared with","receiving agency","recipient agency","agency name","organization")
                  if x in headers),None)
  if not recipient:return []
  names=set()
  for i,row in enumerate(records):
   if i>=5000:break
   name=" ".join((row.get(recipient) or "").split())
   if len(name)>=4 and len(name)<=180 and re.search(r"[A-Za-z]",name):
    names.add(name)
  return sorted(names)[:2000]
 except (csv.Error,UnicodeError,ValueError,TypeError):return []

def rest(url,secret,table,method="GET",params=None,body=None,prefer=None):
 path=table
 if params:path+="?"+urllib.parse.urlencode(params,doseq=True)
 headers={"apikey":secret,"Authorization":"Bearer "+secret,
          "Content-Type":"application/json","Accept":"application/json"}
 if prefer:headers["Prefer"]=prefer
 req=urllib.request.Request(url.rstrip("/")+"/rest/v1/"+path,method=method,
    headers=headers,data=(json.dumps(body).encode() if body is not None else None))
 with urllib.request.urlopen(req,timeout=30) as res:
  return json.loads(res.read()) if method=="GET" else None

def page_all(url,secret,table,columns):
 rows=[]
 for off in range(0,20000,500):
  batch=rest(url,secret,table,params={"select":columns,"limit":"500","offset":str(off)})
  if not isinstance(batch,list):raise ValueError("Incomplete acquisition DB scan")
  rows.extend(batch)
  if len(batch)<500:return rows
 raise ValueError("Acquisition snapshot exceeds bounded scan")

def reviewed_seeds(url,secret,when=None,limit=22):
 # Review status originates in the existing original-government program
 # inventory. Only .gov links are used; redirects and alternate domains
 # still fail the separate URL and public-IP checks.
 when=when or dt.datetime.now(dt.timezone.utc).date()
 rows=page_all(url,secret,"flock_documented_programs",
               "jurisdiction_label,official_evidence_url,record_status")
 out={}
 for row in rows:
  if row.get("record_status")!="verified":continue
  source=normalize_url(row.get("official_evidence_url") or "",
                      row.get("official_evidence_url") or "")
  label=str(row.get("jurisdiction_label") or "")
  if not source or not label or len(label)>150:continue
  out[source]=label
 # Keep hand-curated high-yield original government entries every run,
 # rotate additional vetted original sources for national expansion.
 for url,label in SEEDS:out[url]=label
 priorities=list(SEEDS)
 other=sorted((url,label) for url,label in out.items() if url not in dict(SEEDS))
 spare=max(0,limit-len(priorities))
 if len(other)>spare and spare:
  start=when.toordinal()%len(other)
  other=(other[start:]+other[:start])[:spare]
 return tuple(priorities+other[:spare])

def scan(fetcher=fetch,seeds=SEEDS,observed_pages=None):
 out={};recipients={};successful=0;errors=[]
 for seed,label in seeds:
  try:
   html,kind=fetcher(seed,MAX_PAGE)
   if not kind.lower().startswith("text/html"):
    raise ValueError("Original page did not return HTML")
   items=extract_links(html,seed,label)
   successful+=1
   # Record appearance history only for fully parsed, successfully retrieved
   # original government pages. Errors MUST NOT count as missing documents.
   if observed_pages is not None:
    observed_pages[seed]={"sha256":hashlib.sha256(html).hexdigest(),
                          "urls":[x["document_url"] for x in items]}
   for x in items:
    out.setdefault(x["document_url"],x)
  except Exception as exc:
   errors.append((seed,type(exc).__name__,str(exc)[:130]))
 for url,item in list(out.items()):
  if item["document_class"]!="sharing_export" or not (url.lower().split("?")[0].endswith(".csv") or re.search(r"\.csv\b",item["link_label"],re.I)):
   continue
  try:
   body,_=fetcher(url,MAX_CSV)
   names=csv_recipient_names(body)
   if names:recipients[url]=names
  except Exception as exc:
   errors.append((url,type(exc).__name__,str(exc)[:100]))
 return out,recipients,successful,errors

def save(out,recipients,successful,errors,url,secret,seeded_count=len(SEEDS),observed_pages=None):
 prior_rows=page_all(url,secret,"flock_original_document_leads","document_url,government_page_url")
 existing={r["document_url"] for r in prior_rows}
 new=[v for k,v in out.items() if k not in existing]
 if new:
  for i in range(0,len(new),125):
   rest(url,secret,"flock_original_document_leads",method="POST",
    params={"on_conflict":"document_url"},body=new[i:i+125],
    prefer="resolution=ignore-duplicates,return=minimal")
 # The original source-link observation ledger is updated atomically once
 # the new links have been committed. It never updates document review_status
 # or interprets absent links as revoked contracts/permissions.
 if observed_pages is not None:
  root_by_url={r["document_url"]:r["government_page_url"] for r in prior_rows}
  root_by_url.update({u:item["government_page_url"] for u,item in out.items()
                      if u not in root_by_url})
  for root,observation in sorted(observed_pages.items()):
   included=sorted({u for u in observation["urls"] if root_by_url.get(u)==root})
   rest(url,secret,"rpc/record_original_document_link_scan",method="POST",
    body={"p_government_page_url":root,
          "p_document_urls":included,
          "p_page_sha256":observation["sha256"]},
    prefer="return=minimal")
 candidate_rows=[{"document_url":u,"recipient_label":name,
  "extraction_basis":"csv_named_recipient_column_unreviewed","review_status":"review_required"}
  for u,names in recipients.items() for name in names]
 for i in range(0,len(candidate_rows),100):
  rest(url,secret,"flock_original_sharing_extraction_candidates",method="POST",
   params={"on_conflict":"document_url,recipient_label"},body=candidate_rows[i:i+100],
   prefer="resolution=ignore-duplicates,return=minimal")
 all_leads=page_all(url,secret,"flock_original_document_leads","document_url,review_status")
 named=page_all(url,secret,"flock_original_sharing_extraction_candidates","document_url,recipient_label")
 if observed_pages is None:
  missing_links=0
 else:
  missing_links=sum(r["link_status"]=="not_linked_after_two_successful_scans"
    for r in page_all(url,secret,"flock_original_document_link_observations","link_status"))
 triaged=sum(r["triage_status"] in ("readable_document_indicators_only","no_extractable_text")
   for r in page_all(url,secret,"flock_original_pdf_content_triage","triage_status"))
 primary=page_all(url,secret,"flock_original_sharing_edges","source_key,recipient_label")
 sources=page_all(url,secret,"flock_original_sharing_sources","source_key")
 stamp=dt.datetime.now(dt.timezone.utc).date().isoformat()
 metrics={"metric_date":stamp,"seeded_pages":seeded_count,"successfully_read_pages":successful,
   "total_discovered_links":len(all_leads),
   "total_reviewed_documents":sum(r["review_status"]=="document_content_verified" for r in all_leads),
   "raw_named_recipient_candidates":len(named),
   "verified_original_sharing_edges":len(primary),
   "verified_original_publishers":len(sources),
   "source_errors":len(errors),
   "pdf_content_triaged_documents":triaged,
   "original_links_missing_two_successful_scans":missing_links}
 rest(url,secret,"flock_original_acquisition_public_metrics",method="POST",
   params={"on_conflict":"metric_date"},body=[metrics],
   prefer="resolution=merge-duplicates,return=minimal")
 rest(url,secret,"flock_original_document_scan_runs",method="POST",
   body=[{"seeded_pages":seeded_count,"successfully_read_pages":successful,
     "new_document_links":len(new),"seen_document_links":len(out),
     "named_recipient_candidates":len(candidate_rows),
     "source_errors":len(errors),
     "summary":"Original gov hyperlink extraction only; no verified agreement or camera coordinates."}],
   prefer="return=minimal")
 return metrics,len(new)

def main():
 url=os.environ.get("SUPABASE_URL","")
 secret=os.environ.get("SUPABASE_SERVICE_ROLE_KEY","")
 if not url or not secret:raise RuntimeError("Original-gov private acquisition credentials missing")
 seeds=reviewed_seeds(url,secret)
 observed_pages={}
 data,names,ok,errors=scan(seeds=seeds,observed_pages=observed_pages)
 print("Original .gov sources successful:",ok,"/",len(seeds),
  "linked document leads:",len(data),"CSV recipient candidates:",sum(map(len,names.values())),
  "held source errors:",len(errors))
 for root,kind,why in errors:print("Held",urllib.parse.urlsplit(root).hostname,kind,why[:80])
 metrics,created=save(data,names,ok,errors,url,secret,seeded_count=len(seeds),observed_pages=observed_pages)
 print("New original government document leads:",created,
       "Existing/new total:",metrics["total_discovered_links"],
       "content-verified:",metrics["total_reviewed_documents"],
       "public metrics published; ZERO new permissions/camera coordinates")

if __name__=="__main__":
 try:main()
 except Exception as e:
  raise SystemExit("Original government acquisition held: "+type(e).__name__+": "+str(e)[:130]) from None
