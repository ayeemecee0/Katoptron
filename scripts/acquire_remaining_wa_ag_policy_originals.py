#!/usr/bin/env python3
"""Retrieve state Attorney General linked WA ALPR policies, preserving evidence tiers.

Original PDF hashes/page counts are acquisition receipts ONLY. ALPR registration
or even a PDF containing "Flock" is not verified Flock deployment, signed
contract, effective policy, sharing permission, installed equipment or compliance.
No raw license plate reads or full PDF text stored.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,io,json,re,urllib.parse,urllib.request
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data"/"wa-original-agency-alpr-registrations.json"
REV1=ROOT/"data"/"verified-wa-flock-policy-originals.json"
REV2=ROOT/"data"/"verified-wa-agency-policies.json"
OUT=ROOT/".katoptron-ci"/"wa-remaining-agency-original-pdf-receipts.json"
MAX_PDF_BYTES=7_000_000
MAX_PAGES=120
ALLOWED={"agportal-s3bucket.s3.us-west-2.amazonaws.com","blackdiamondwa.gov","www.cwu.edu","www.cpwa.us",
"www.douglascountysheriff.org","www.eastwenatcheewa.gov","inside.ewu.edu","www.ellensburgwa.gov",
"www.cityofenumclaw.net","www.everettwa.gov","www.grandview.wa.us","public.powerdms.com",
"www.co.kittitas.wa.us","www.libertylakewa.gov","www.cityofmontesano.com","www.pasco-wa.gov",
"selahwa.gov","www.soundtransit.org","uniongapwa.gov","www.washington.edu",
"transportation.wsu.edu","transportation.wwu.edu"}
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("unreviewed_source_redirect")
def safe(url):
 try:
  p=urllib.parse.urlsplit(url)
  if not isinstance(url,str) or len(url)>950 or p.scheme!="https" or p.hostname not in ALLOWED or
      p.netloc!=p.hostname or p.fragment or p.username or p.password or
      re.search(r"%2e|\\|/\.\.?/",p.path,re.I):return False
  if p.query:
   if p.hostname=="agportal-s3bucket.s3.us-west-2.amazonaws.com":
    return bool(re.fullmatch(r"VersionId=[A-Za-z0-9_.-]{1,100}",p.query))
   return (p.hostname in {"www.eastwenatcheewa.gov","www.everettwa.gov","www.libertylakewa.gov"} and
      p.query=="bidId=" and bool(re.fullmatch(r"/DocumentCenter/View/\d+/.+",p.path)))
  return len(p.path)>2
 except (ValueError,TypeError):return False
def fetch(url):
 if not safe(url):raise ValueError("unapproved_original")
 req=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-WA-AGO-public-policy-original-review/1.0",
  "Accept":"application/pdf,application/octet-stream"})
 with urllib.request.build_opener(DenyRedirect()).open(req,timeout=22) as r:
  if r.status!=200 or r.geturl()!=url:raise ValueError("changed_original_source")
  raw=r.read(MAX_PDF_BYTES+1)
 return raw
def select(reg,docs):
 reviewed={(r["agency_name"].lower(),r["source_url"]) for r in docs}
 if reg.get("schema_version")!=1 or len(reg.get("registrations",[]))!=97 or len(reviewed)!=11:
  raise ValueError("AG agency original review baseline incomplete")
 rows=[];already=0
 for r in reg["registrations"]:
  if r.get("registry_status")!="agency_self_certification_listed_by_state_AG_not_independently_verified":
   raise ValueError("Original AG agency registration changed")
  links=r.get("policy_links_from_official_ago_page",[])
  if not isinstance(links,list) or any(not safe(u) for u in links):
   raise ValueError("Unknown state-linked agency original publisher")
  if any((r["agency_name"].lower(),u) in reviewed for u in links):
   already+=1;continue
  rows.append(r)
 if len(rows)!=86 or already!=11:raise ValueError("Previously reviewed WA originals were double-counted or lost")
 return rows
def inspect(r,fetcher=fetch):
 source=(r["policy_links_from_official_ago_page"] or [None])[0]
 result={"id":r["id"],"agency":r["agency_name"],"state":"WA",
  "official_state_registration":"https://www.atg.wa.gov/ALPR",
  "linked_original_url":source,"status":"held_original_url_absent",
  "content_sha256":None,"pdf_pages":None,"readable_first_3_pages":False,
  "source_flock_word_first_3_pages":False,
  "individual_original_policy_pages_verified":False,
  "agency_currently_operating_verified":False,"flock_vendor_or_installation_verified":False,
  "legal_policy_adoption_verified":False,"camera_points_added":0,"sharing_edges_added":0}
 if source is None:return result
 try:payload=fetcher(source)
 except Exception as e:
  name=str(e)
  result["status"]="held_original_redirect" if "redirect" in name else ("held_http_or_network")
  result["hold_type"]=type(e).__name__;return result
 if not isinstance(payload,bytes) or len(payload)>MAX_PDF_BYTES:
  result["status"]="held_oversized_or_invalid";return result
 if not payload.startswith(b"%PDF-") or len(payload)<300:
  result["status"]="held_wrong_media";return result
 try:
  pdf=PdfReader(io.BytesIO(payload),strict=True)
  if pdf.is_encrypted or not 1<=len(pdf.pages)<=MAX_PAGES:raise ValueError("encrypted_or_oversized")
  parts=[]
  for page in pdf.pages[:3]:
   text=(page.extract_text() or "")[:20000]
   if text:parts.append(text)
  source_text=" ".join(parts)
  result.update(status="retrieved_unreviewed_original_pdf",
   content_sha256=hashlib.sha256(payload).hexdigest(),
   pdf_pages=len(pdf.pages),readable_first_3_pages=bool(parts),
   source_flock_word_first_3_pages=bool(re.search(r"\bflock(?:\s+safety)?\b",source_text,re.I)))
 except Exception:
  result["status"]="held_unreadable_original"
 return result
def run(catalog,reviewed,fetcher=fetch,workers=6):
 rows=select(catalog,reviewed)
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  data=list(pool.map(lambda row:inspect(row,fetcher),rows))
 ok=sum(r["status"]=="retrieved_unreviewed_original_pdf" for r in data)
 return {"schema_version":1,"checked_at":dt.datetime.now(dt.timezone.utc).isoformat(),
 "scope":"86_state_AG_linked_original_Alpr_policy_acquisition_receipts_not_individual_source_page_review",
 "already_individually_page_reviewed":11,"remaining_agencies_checked":86,
 "original_pdf_receipts_retrieved":ok,"original_pdf_held":86-ok,
 "new_adopted_policy_claims":0,"new_verified_flock_agency_operators":0,
 "new_camera_coordinates":0,"new_live_sharing_edges":0,"receipts":data}
def main():
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT);p.add_argument("--workers",type=int,default=6)
 opts=p.parse_args()
 if not 1<=opts.workers<=8:raise ValueError("Unbounded source acquisition")
 dest=opts.out.resolve()
 if not dest.is_relative_to(ROOT):raise ValueError("Invalid destination")
 data=run(json.loads(REG.read_text(encoding="utf8")),
  [*json.loads(REV1.read_text(encoding="utf8"))["documents"],*json.loads(REV2.read_text(encoding="utf8"))["documents"]],
  workers=opts.workers)
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("WA_AG_UNREVIEWED_ORIGINAL_PDF_ACQUISITION",json.dumps({
  "state_AG_registrations":97,"prior_individual_PDF_reviews":11,
  "remaining_originals":86,"retrieved_PDF_receipts":data["original_pdf_receipts_retrieved"],
  "held_PDF_receipts":data["original_pdf_held"],
  "vendor_or_policy_effective_claims_published":0},sort_keys=True))
 for r in data["receipts"]:
  print("WA_AG_DOCUMENT_RECEIPT",json.dumps({k:r.get(k) for k in
   ("id","agency","status","pdf_pages","content_sha256","source_flock_word_first_3_pages")},sort_keys=True))
if __name__=="__main__":main()
