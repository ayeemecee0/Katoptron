#!/usr/bin/env python3
"""Acquire only public title/date/publisher metadata from Minnesota's official ALPR audit mandate index.

The registry is not an agency operator crosswalk, Flock installation evidence, or
independent verification of the linked PDF's contents. No PDF bytes are fetched.
Only original www.lrl.mn.gov URLs are allowed, no redirect or arbitrary host.
"""
import datetime as dt
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

REGISTRY="https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735"
API_TABLE="flock_public_mn_alpr_audit_registry"
MAX_HTML=1_800_000
PDF_URL=re.compile(r"^https://www\.lrl\.mn\.gov/docs/(20[0-9]{2})/mandated/([0-9]{6})\.pdf$")
ID=re.compile(r"^([0-9]{2})-([0-9]{4})\.pdf$")
FLOCK=re.compile(r"\bflock\b",re.I)
OTHERS=re.compile(r"\b(?:axon|motorola|elsag|leonardo|vigilant)\b",re.I)

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*_args,**_kwargs):
  raise ValueError("Official archive index redirected; hold source until reverified")

class TableParser(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=="tr":
   self.row=[]
  elif tag=="td" and self.row is not None:
   self.cell={"text":[],"links":[]}
  elif tag=="a" and self.cell is not None:
   href=dict(attrs).get("href")
   if href:self.cell["links"].append(href)
 def handle_data(self,data):
  if self.cell is not None:self.cell["text"].append(data)
 def handle_endtag(self,tag):
  if tag=="td" and self.cell is not None and self.row is not None:
   self.row.append({"text":" ".join(" ".join(self.cell["text"]).split()),
                    "links":self.cell["links"]})
   self.cell=None
  elif tag=="tr":
   if self.row is not None:self.rows.append(self.row)
   self.row=None;self.cell=None

def normal_pdf_url(raw,display_text):
 if not isinstance(raw,str) or len(raw)>1200 or any(c in raw for c in "\r\n\\"):
  return None
 try:
  url=urllib.parse.urljoin(REGISTRY,raw)
  parsed=urllib.parse.urlsplit(url)
  if parsed.scheme!="https" or parsed.hostname!="www.lrl.mn.gov" or parsed.netloc!="www.lrl.mn.gov" or parsed.query or parsed.fragment:
   return None
  match=PDF_URL.fullmatch(url)
  if not match:return None
  idmatch=ID.fullmatch(display_text.strip())
  if not idmatch:return None
  if int(match.group(1)[-2:])!=int(idmatch.group(1)) or match.group(2)!=idmatch.group(1)+idmatch.group(2):
   return None
  return url
 except (ValueError,TypeError):return None

def iso(value,pattern):
 try:
  return dt.datetime.strptime(value.strip().rstrip("."),pattern).date().isoformat()
 except (ValueError,TypeError,AttributeError):return None

def title_scope(title):
 flock=bool(FLOCK.search(title))
 other=bool(OTHERS.search(title))
 if flock and other:return "mixed_or_ambiguous_title"
 if flock:return "flock_named_in_title"
 if other:return "other_vendor_named_in_title"
 return "unspecified_alpr_title"

def index_rows(html):
 if not isinstance(html,bytes) or len(html)>MAX_HTML:
  raise ValueError("Official archive HTML missing or too large")
 p=TableParser();p.feed(html.decode("utf-8","replace"))
 rows={}
 fingerprint=hashlib.sha256(html).hexdigest()
 for cells in p.rows:
  if len(cells)<6:continue
  # Site indexes: Title | Publisher(s) | Publication Date | Coverage |
  # Date Received | Report Link. Only the last cell may yield report evidence.
  title,publishers,publication,coverage,received,report=cells[:6]
  t=title["text"][:400].strip();pub=publishers["text"][:450].strip()
  candidates=[(raw,report["text"]) for raw in report["links"]]
  if len(candidates)!=1:continue
  url=normal_pdf_url(*candidates[0])
  if not url:continue
  if len(t)<18 or len(t)>400:continue
  # Preserve official metadata as received, without 'verification' of
  # report contents, manufacturer, people, dates, or installed devices.
  row={
   "source_url":url,"registry_url":REGISTRY,
   "report_id":report["text"].strip(),
   "report_title":t,"listed_publishers":pub,
   "publication_date":iso(publication["text"],"%B %d, %Y"),
   "coverage_period":coverage["text"][:260],
   "received_date":iso(received["text"],"%m/%d/%Y"),
   "title_scope":title_scope(t),
   "evidence_tier":"state_legislative_registry_index_metadata_only",
   "registry_sha256":fingerprint,
  }
  if row["report_id"] in (v["report_id"] for v in rows.values()):
   raise ValueError("Official state registry has duplicate report IDs; hold")
  rows[url]=row
 if not 20<=len(rows)<=500:
  raise ValueError("Unexpected registry report count; do not overwrite any published state records: "+str(len(rows)))
 return list(sorted(rows.values(),key=lambda r:r["report_id"],reverse=True))

def fetch_index(fetcher=None):
 if fetcher:return fetcher(REGISTRY)
 req=urllib.request.Request(REGISTRY,headers={
   "User-Agent":"Katoptron-public-official-ALPR-index/1.0",
   "Accept":"text/html"})
 opener=urllib.request.build_opener(NoRedirect())
 with opener.open(req,timeout=25) as response:
  if response.status!=200 or response.geturl()!=REGISTRY:
   raise ValueError("Original index unavailable")
  if not response.headers.get("Content-Type","").lower().startswith("text/html"):
   raise ValueError("Original archive returned non-HTML")
  payload=response.read(MAX_HTML+1)
 if len(payload)>MAX_HTML:raise ValueError("Original source exceeds bounded size")
 return payload

def rest(api,secret,path,method="GET",params=None,body=None,prefer=None):
 url=api.rstrip("/")+"/rest/v1/"+path
 if params:url+="?"+urllib.parse.urlencode(params)
 headers={"apikey":secret,"Authorization":"Bearer "+secret,"Accept":"application/json",
          "Content-Type":"application/json"}
 if prefer:headers["Prefer"]=prefer
 req=urllib.request.Request(url,method=method,headers=headers,
                            data=json.dumps(body).encode() if body is not None else None)
 with urllib.request.urlopen(req,timeout=30) as response:
  if method=="GET":return json.load(response)
  return None

def publish(rows,api,secret):
 # All this page contains is indexed public state metadata. Service account
 # has no permissions here to promote PDFs into independently reviewed facts.
 if not api.startswith("https://") or not secret:
  raise ValueError("Protected Supabase service credential unavailable")
 current=rest(api,secret,API_TABLE,params={"select":"source_url","limit":"500"})
 if not isinstance(current,list) or len(current)>=500:
  raise ValueError("Existing public registry scan incomplete")
 current_ids={r["source_url"] for r in current}
 now=dt.datetime.now(dt.timezone.utc).isoformat()
 for offset in range(0,len(rows),100):
  batch=[{**row,"last_observed_at":now} for row in rows[offset:offset+100]]
  rest(api,secret,API_TABLE,"POST",params={"on_conflict":"source_url"},
       body=batch,prefer="resolution=merge-duplicates,return=minimal")
 # Save private metrics only after all chunks succeed. Failures do not revoke
 # previously indexed original sources or constitute missing-policy evidence.
 rest(api,secret,"flock_private_mn_alpr_registry_scan_runs","POST",
      body={"scanned_at":now,"registry_sha256":rows[0]["registry_sha256"],
            "report_links":len(rows),
            "flock_titles":sum(x["title_scope"]=="flock_named_in_title" for x in rows),
            "new_links":len(set(x["source_url"] for x in rows)-current_ids)},
      prefer="return=minimal")
 return len(set(x["source_url"] for x in rows)-current_ids)

def main():
 html=fetch_index()
 rows=index_rows(html)
 print("Official Minnesota ALPR index valid entries:",len(rows),
       "Flock named in report title:",sum(x["title_scope"]=="flock_named_in_title" for x in rows),
       "other vendor explicit:",sum(x["title_scope"]=="other_vendor_named_in_title" for x in rows),
       "unknown/mixed title:",sum(x["title_scope"] in ("unspecified_alpr_title","mixed_or_ambiguous_title") for x in rows))
 api=os.environ.get("SUPABASE_URL","");secret=os.environ.get("SUPABASE_SERVICE_ROLE_KEY","")
 if not api or not secret:raise ValueError("Protected source acquisition service credentials missing")
 newly=publish(rows,api,secret)
 print("New state archive report links indexed:",newly)
 print("Indexed government report titles only. Individually verified PDF content: 0. Executed Flock contracts verified: 0.")
if __name__=="__main__":
 try:main()
 except Exception as exc:
  # Never expose authentication headers or full private HTTP errors.
  raise SystemExit("MN registry harvest held: "+type(exc).__name__+": "+(str(exc)[:170] if isinstance(exc,ValueError) else "network or database error")) from None
