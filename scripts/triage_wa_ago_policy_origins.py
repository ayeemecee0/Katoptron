#!/usr/bin/env python3
"""Non-publication triage of source PDFs linked by WA Attorney General ALPR registry.

Triage is *not* content verification, equipment attribution, officer compliance,
or camera mapping. Fetch only exact immutable-version AGO S3 links already in
the local original AGO snapshot. No redirects, requests to arbitrary domains,
raw page text, plate records, or private results. Errors do not produce facts.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,io,json,re,urllib.parse,urllib.request
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"wa-original-agency-alpr-registrations.json"
OUT=ROOT/".katoptron-ci"/"wa-ag-linked-policy-original-receipts.json"
AGO="https://www.atg.wa.gov/ALPR"
HOST="agportal-s3bucket.s3.us-west-2.amazonaws.com"
MAX_BYTES=8_000_000
MAX_PAGES=160
STATUS={"exact_pdf_text_detected","exact_pdf_scan_only","held_non_pdf","held_unreadable_pdf","held_unreachable","held_redirect"}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("redirect")
def is_exact_ag_hosted(url):
 if not isinstance(url,str) or len(url)>950:return False
 try:
  p=urllib.parse.urlsplit(url)
  return p.scheme=="https" and p.hostname==HOST and p.netloc==HOST and not p.username and not p.password and not p.fragment and not re.search(r"%2e|\\|\.\.",p.path,re.I) and p.path.startswith("/ALPR/") and p.path.lower().endswith(".pdf") and bool(re.fullmatch(r"VersionId=[A-Za-z0-9._-]{12,120}",p.query))
 except (ValueError,TypeError):return False
def candidates(registry):
 if not isinstance(registry,dict) or registry.get("source_url")!=AGO or not isinstance(registry.get("registrations"),list):
  raise ValueError("Wrong original source registry")
 agency_seen=set();out=[]
 for row in registry["registrations"]:
  name=row.get("agency_name");links=row.get("policy_links_from_official_ago_page")
  if not isinstance(name,str) or not 4<=len(name)<=160 or name in agency_seen or not isinstance(links,list):
   raise ValueError("Duplicate or malformed state-submitted agency")
  agency_seen.add(name)
  for url in links:
   if is_exact_ag_hosted(url):
    out.append({"agency_name":name,"policy_source_url":url,"submitted_on":row.get("submitted_on")})
 return sorted(out,key=lambda x:(x["agency_name"],x["policy_source_url"]))
def fetch(url):
 if not is_exact_ag_hosted(url):raise ValueError("unlisted_domain")
 req=urllib.request.Request(url,headers={"Accept":"application/pdf","User-Agent":"Katoptron-WA-AGO-original-public-policy-triage/1.0"})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=18) as r:
   if r.status!=200 or r.geturl()!=url:raise ValueError("status_or_url")
   return r.read(MAX_BYTES+1)
 except ValueError:
  raise
def evaluate(candidate,fetcher=fetch):
 row={**candidate,"inspection_status":None,"page_count":None,"sha256":None,"bytes":None,
   "searchable_text_pages":0,"scanned_image_pages":0,"potential_flock_term_pages":[],
   "manufacturer_identity_assertion":False,"camera_coordinates_asserted":False}
 try:raw=fetcher(candidate["policy_source_url"])
 except Exception as e:
  row["inspection_status"]="held_redirect" if isinstance(e,ValueError) and str(e)=="redirect" else "held_unreachable"
  return row
 if not isinstance(raw,bytes) or len(raw)>MAX_BYTES or len(raw)<100 or not raw.startswith(b"%PDF-"):
  row["inspection_status"]="held_non_pdf";return row
 try:
  pdf=PdfReader(io.BytesIO(raw),strict=True)
  if pdf.is_encrypted or not 1<=len(pdf.pages)<=MAX_PAGES:raise ValueError("unusable_pdf")
  textpages=0;images=0;flock=[]
  for i,page in enumerate(pdf.pages,1):
   t=" ".join((page.extract_text() or "").casefold().split())
   if len(t)>=35:textpages+=1
   if page.images:images+=1
   if re.search(r"\bflock\s+safety\b",t):flock.append(i)
  if not textpages and not images:raise ValueError("unsearchable_with_no_images")
  row.update(inspection_status="exact_pdf_text_detected" if textpages else "exact_pdf_scan_only",
   page_count=len(pdf.pages),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
   searchable_text_pages=textpages,scanned_image_pages=images,potential_flock_term_pages=flock[:160])
 except Exception:
  row["inspection_status"]="held_unreadable_pdf"
 return row
def validate_snapshot(data,registry):
 expected=candidates(registry)
 if (not isinstance(data,dict) or data.get("schema_version")!=1 or
     data.get("source_registry_url")!=AGO or
     data.get("scope")!="source_metadata_only_no_automatic_fact_publication" or
     not isinstance(data.get("receipts"),list) or len(data["receipts"])!=len(expected)):
  raise ValueError("Non-publication source receipt shape differs from AGO original index")
 for row,orig in zip(data["receipts"],expected):
  if (row.get("agency_name")!=orig["agency_name"] or
      row.get("policy_source_url")!=orig["policy_source_url"] or
      row.get("submitted_on")!=orig["submitted_on"] or row.get("inspection_status") not in STATUS or
      row.get("manufacturer_identity_assertion") is not False or
      row.get("camera_coordinates_asserted") is not False):
   raise ValueError("Forged or wrongly attributed AGO PDF receipt")
  if row["inspection_status"].startswith("exact_pdf"):
   if (not isinstance(row.get("sha256"),str) or not re.fullmatch(r"[0-9a-f]{64}",row["sha256"]) or
       not isinstance(row.get("bytes"),int) or not 100<=row["bytes"]<=MAX_BYTES or
       not isinstance(row.get("page_count"),int) or not 1<=row["page_count"]<=MAX_PAGES or
       not isinstance(row.get("searchable_text_pages"),int) or
       not 0<=row["searchable_text_pages"]<=row["page_count"] or
       not isinstance(row.get("scanned_image_pages"),int) or
       not 0<=row["scanned_image_pages"]<=row["page_count"] or
       not isinstance(row.get("potential_flock_term_pages"),list) or
       len(set(row["potential_flock_term_pages"]))!=len(row["potential_flock_term_pages"]) or
       any(not isinstance(p,int) or not 1<=p<=row["page_count"] for p in row["potential_flock_term_pages"])):
    raise ValueError("Invalid immutable PDF receipt")
   if (row["inspection_status"]=="exact_pdf_scan_only")!=(row["searchable_text_pages"]==0):
    raise ValueError("Machine-text classification conflict")
  elif row.get("sha256") is not None or row.get("page_count") is not None or row.get("potential_flock_term_pages")!=[]:
   raise ValueError("Failed PDF cannot be source-verified")
 return data
def build(registry,workers=5,fetcher=fetch,date=None):
 originals=candidates(registry)
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  receipt=list(pool.map(lambda a:evaluate(a,fetcher),originals))
 obj={"schema_version":1,"source_registry_url":AGO,"inspected_on":date or dt.datetime.now(dt.timezone.utc).date().isoformat(),
  "scope":"source_metadata_only_no_automatic_fact_publication",
  "warning":"An AGO URL, PDF hash, page count, or term occurrence does not verify Flock manufacturer, installed devices, actual data handling, sharing, audit compliance or camera coordinates. Source discrepancies are held.",
  "receipts":receipt}
 return validate_snapshot(obj,registry)
def main():
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT);p.add_argument("--workers",type=int,default=5);opts=p.parse_args()
 if not 1<=opts.workers<=8:raise ValueError("Bounded fetch concurrency required")
 data=build(json.loads(REGISTRY.read_text(encoding="utf8")),workers=opts.workers)
 path=opts.out.resolve()
 if not path.is_relative_to(ROOT):raise ValueError("Output outside repo prohibited")
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
 counts={s:sum(r["inspection_status"]==s for r in data["receipts"]) for s in sorted(STATUS)}
 print("WA_AG_VERSIONED_POLICY_TRIAGE",json.dumps({"source_count":len(data["receipts"]),"statuses":counts,
  "potential_flock_text_citations_not_verified_vendor":sum(bool(r["potential_flock_term_pages"]) for r in data["receipts"])},sort_keys=True))
 for r in data["receipts"]:
  print("WA_ORIGINAL_POLICY_RECEIPT",json.dumps({k:r[k] for k in ["agency_name","inspection_status","page_count","sha256","bytes","searchable_text_pages","scanned_image_pages","potential_flock_term_pages"]},ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
