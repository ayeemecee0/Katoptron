#!/usr/bin/env python3
"""Classify exact AGO-linked third-party originals without publishing policy claims.

All requests are for public policy links already enumerated in the AGO state
registry. Does not crawl, follow redirects, inspect private data or automatically
infer Flock hardware, live access or camera points. Outputs metadata only.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,html.parser,io,json,re,urllib.parse,urllib.request
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"wa-original-agency-alpr-registrations.json"
OUTPUT=ROOT/".katoptron-ci"/"wa-ag-external-original-policy-source-receipts.json"
AGO="https://www.atg.wa.gov/ALPR"
ARCHIVE_HOST="agportal-s3bucket.s3.us-west-2.amazonaws.com"
HOSTS={
 "blackdiamondwa.gov","www.cwu.edu","www.cpwa.us","www.douglascountysheriff.org",
 "www.eastwenatcheewa.gov","inside.ewu.edu","www.ellensburgwa.gov",
 "www.cityofenumclaw.net","www.everettwa.gov","www.grandview.wa.us",
 "public.powerdms.com","www.co.kittitas.wa.us","www.libertylakewa.gov",
 "www.cityofmontesano.com","www.pasco-wa.gov","selahwa.gov",
 "www.soundtransit.org","uniongapwa.gov","www.washington.edu",
 "transportation.wsu.edu","transportation.wwu.edu"
}
STATES={"original_pdf_text_detected","original_pdf_image_only","original_html_text_detected",
 "held_redirect","held_http_error","held_unreachable","held_oversized",
 "held_empty_or_unusable","held_invalid_pdf","held_unsupported_content"}
MAX_BYTES=8_000_000
MAX_PAGES=160
MAX_HTML=1_500_000
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("redirect_disallowed")
class Words(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.words=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in {"script","style","svg"}:self.skip+=1
 def handle_endtag(self,tag):
  if tag in {"script","style","svg"}:self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip:self.words.append(s)
def exact(url):
 if not isinstance(url,str) or len(url)>1200:return False
 try:
  p=urllib.parse.urlsplit(url)
  return (p.scheme=="https" and p.hostname in HOSTS and p.netloc==p.hostname and
   not p.username and not p.password and not p.fragment and bool(p.path) and
   not re.search(r"%2e|\\|\.\.",p.path,re.I) and len(p.query)<140)
 except (ValueError,TypeError):return False
def candidates(registry):
 if (not isinstance(registry,dict) or registry.get("source_url")!=AGO or
     not isinstance(registry.get("registrations"),list)):raise ValueError("AGO registry invalid")
 seen=set();results=[]
 for entry in registry["registrations"]:
  name=entry["agency_name"]
  if name in seen:raise ValueError("Duplicate AGO agency identity")
  seen.add(name)
  for url in entry["policy_links_from_official_ago_page"]:
   if url.startswith("https://"+ARCHIVE_HOST+"/"):continue
   if not exact(url):raise ValueError("Unexpected external policy URL in state registry")
   results.append({"agency_name":name,"policy_source_url":url,"submitted_on":entry.get("submitted_on")})
 return sorted(results,key=lambda r:(r["agency_name"],r["policy_source_url"]))
def fetch(url):
 if not exact(url):raise ValueError("unapproved_url")
 req=urllib.request.Request(url,headers={"User-Agent":"Katoptron-AGO-public-policy-external-source-triage/1.0","Accept":"application/pdf,text/html;q=0.9"})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=18) as res:
   if res.status!=200 or res.geturl()!=url:raise ValueError("unexpected_response")
   mime=res.headers.get("Content-Type","").split(";")[0].strip().lower()
   data=res.read(MAX_BYTES+1)
   return mime,data
 except urllib.error.HTTPError as exc:
  if 300<=exc.code<400:raise ValueError("redirect_disallowed") from None
  raise ValueError("http_error") from None
def image_resource(page):
 resources=page.get("/Resources")
 if not resources:return False
 resources=resources.get_object()
 if not hasattr(resources,"get"):return False
 objs=resources.get("/XObject")
 if not objs:return False
 objs=objs.get_object()
 if not hasattr(objs,"values"):return False
 return any(hasattr(o.get_object(),"get") and str(o.get_object().get("/Subtype"))=="/Image" for o in objs.values())
def evaluate(original,loader=fetch):
 row={**original,"inspection_status":None,"content_type":None,"content_sha256":None,
      "bytes":None,"page_count":None,"text_pages":0,"image_pages":0,
      "page_mentions_flock":[],
      "manufacturer_identity_assertion":False,"installed_equipment_assertion":False,
      "agency_compliance_assertion":False,"camera_coordinates_assertion":False}
 try:
  mime,raw=loader(original["policy_source_url"])
 except Exception as exc:
  msg=str(exc)
  row["inspection_status"]="held_redirect" if msg=="redirect_disallowed" else "held_http_error" if msg=="http_error" else "held_unreachable"
  return row
 if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:
  row["inspection_status"]="held_oversized";return row
 if len(raw)<100:
  row["inspection_status"]="held_empty_or_unusable";return row
 row["content_type"]=mime[:100] if isinstance(mime,str) else None
 if raw.startswith(b"%PDF-"):
  try:
   pdf=PdfReader(io.BytesIO(raw),strict=True)
   if pdf.is_encrypted or not 1<=len(pdf.pages)<=MAX_PAGES:raise ValueError("bad_pdf")
   text_pages=0;image_pages=0;term=[]
   for i,page in enumerate(pdf.pages,1):
    text=" ".join((page.extract_text() or "").casefold().split())
    if len(text)>=35:text_pages+=1
    if image_resource(page):image_pages+=1
    if re.search(r"\bflock\s+safety\b",text):term.append(i)
   if not text_pages and not image_pages:raise ValueError("blank")
   row.update(inspection_status="original_pdf_text_detected" if text_pages else "original_pdf_image_only",
    page_count=len(pdf.pages),text_pages=text_pages,image_pages=image_pages,page_mentions_flock=term)
  except Exception:
   row["inspection_status"]="held_invalid_pdf";return row
 elif b"<html" in raw[:1200].lower() or b"<!doctype html" in raw[:1200].lower():
  if len(raw)>MAX_HTML:row["inspection_status"]="held_oversized";return row
  parser=Words()
  try:parser.feed(raw.decode("utf-8",errors="replace"))
  except Exception:row["inspection_status"]="held_empty_or_unusable";return row
  clean=" ".join(" ".join(parser.words).casefold().split())
  if len(clean)<100:row["inspection_status"]="held_empty_or_unusable";return row
  row["inspection_status"]="original_html_text_detected"
  row["page_mentions_flock"]=[0] if "flock safety" in clean else []
 else:
  row["inspection_status"]="held_unsupported_content";return row
 row["content_sha256"]=hashlib.sha256(raw).hexdigest()
 row["bytes"]=len(raw)
 return row
def validate(data,registry):
 expected=candidates(registry)
 if (not isinstance(data,dict) or data.get("schema_version")!=1 or
  data.get("source_registry_url")!=AGO or
  data.get("scope")!="external_source_metadata_only_no_policy_facts" or
  not isinstance(data.get("receipts"),list) or len(data["receipts"])!=len(expected)):
  raise ValueError("External-source catalog or provenance invalid")
 for row,src in zip(data["receipts"],expected):
  if (any(row.get(k)!=src[k] for k in src) or row.get("inspection_status") not in STATES or
   not all(row.get(k) is False for k in ("manufacturer_identity_assertion","installed_equipment_assertion",
          "agency_compliance_assertion","camera_coordinates_assertion"))):
   raise ValueError("AGO-linked source identity or evidence classification changed")
  good=row["inspection_status"].startswith("original_")
  if good:
   if (not re.fullmatch("[0-9a-f]{64}",row.get("content_sha256") or "") or
     not isinstance(row.get("bytes"),int) or not 100<=row["bytes"]<=MAX_BYTES or
     not isinstance(row.get("page_mentions_flock"),list)):
    raise ValueError("Retrieved original provenance invalid")
   if row["inspection_status"].startswith("original_pdf"):
    if not isinstance(row.get("page_count"),int) or not 1<=row["page_count"]<=MAX_PAGES:
     raise ValueError("Invalid original PDF page count")
    if any(not isinstance(n,int) or not 1<=n<=row["page_count"] for n in row["page_mentions_flock"]):
     raise ValueError("Unreviewed original PDF page number")
   else:
    if row.get("page_count") is not None or not set(row["page_mentions_flock"])<=set([0]):
     raise ValueError("HTML source must not invent PDF pages")
  else:
   if row.get("content_sha256") is not None or row.get("page_count") is not None or row.get("bytes") is not None or row.get("page_mentions_flock")!=[]:
    raise ValueError("Held original cannot be verified")
 return data
def build(registry,loader=fetch,workers=5,date=None):
 originals=candidates(registry)
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  results=list(pool.map(lambda entry:evaluate(entry,loader),originals))
 return validate({"schema_version":1,"source_registry_url":AGO,
  "inspected_on":date or dt.datetime.now(dt.timezone.utc).date().isoformat(),
  "scope":"external_source_metadata_only_no_policy_facts",
  "notes":"Registry link identity and byte/page inspection are not adoption, Flock deployment, current access, installed camera locations, or compliance evidence.",
  "receipts":results},registry)
def compare_to_published(fresh,baseline):
 """Separate original-PDF content drift from frequently changing HTML wrappers.

 This never promotes any source into verified policy findings. A changed PDF
 requires a new page review. HTML hash change is a recheck lead, not an
 authoritative update to adopted policy or vendor status.
 """
 by_agency={r["agency_name"]:r for r in baseline["receipts"]}
 results={"pdf_original_bytes_or_pages_changed_requires_review":[],
  "html_wrapper_bytes_changed_recheck_leads":[],
  "previously_retrieved_now_held":[],
  "previously_held_now_retrieved_requires_review":[]}
 for x in fresh["receipts"]:
  old=by_agency[x["agency_name"]]
  was=old["inspection_status"].startswith("original_")
  is_now=x["inspection_status"].startswith("original_")
  if was and is_now:
   if x["content_sha256"]!=old["content_sha256"] or x["page_count"]!=old["page_count"]:
    key=("html_wrapper_bytes_changed_recheck_leads" if
      old["inspection_status"]=="original_html_text_detected" and
      x["inspection_status"]=="original_html_text_detected"
      else "pdf_original_bytes_or_pages_changed_requires_review")
    results[key].append(x["agency_name"])
  elif was and not is_now:results["previously_retrieved_now_held"].append(x["agency_name"])
  elif not was and is_now:results["previously_held_now_retrieved_requires_review"].append(x["agency_name"])
 return results
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,default=OUTPUT)
 p.add_argument("--workers",type=int,default=5)
 args=p.parse_args()
 if not 1<=args.workers<=8:raise ValueError("Excessive network fanout")
 registry=json.loads(REGISTRY.read_text(encoding="utf8"))
 data=build(registry,workers=args.workers)
 baseline_path=ROOT/"data"/"wa-ag-external-policy-source-inspection.json"
 baseline=validate(json.loads(baseline_path.read_text(encoding="utf8")),registry)
 changes=compare_to_published(data,baseline)
 print("WA_AG_EXTERNAL_POLICY_RECHECK",json.dumps(changes,sort_keys=True))
 if changes["pdf_original_bytes_or_pages_changed_requires_review"]:
  raise ValueError("Original PDF byte or page drift requires source and policy review")
 output=args.out.resolve()
 if not output.is_relative_to(ROOT):raise ValueError("Output outside trusted directory")
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
 totals={}
 for row in data["receipts"]:totals[row["inspection_status"]]=totals.get(row["inspection_status"],0)+1
 print("WA_AG_EXTERNAL_POLICY_TRIAGE",json.dumps({"links":len(data["receipts"]),"unique_urls":len(set(r["policy_source_url"] for r in data["receipts"])),"statuses":totals},sort_keys=True))
 for row in data["receipts"]:
  print("WA_AG_EXTERNAL_POLICY_RECEIPT",json.dumps({k:row[k] for k in
   ("agency_name","policy_source_url","inspection_status","content_sha256","bytes","page_count","text_pages","image_pages","page_mentions_flock")},sort_keys=True))
if __name__=="__main__":main()
