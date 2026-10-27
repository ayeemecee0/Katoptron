#!/usr/bin/env python3
"""Read-only original-source failure classification for seven held AGO policy PDFs.

Output metadata only. Never print document contents or follow unapproved URL
redirects. Do not automatically promote a reparsed PDF into verified findings.
"""
import hashlib,io,json,urllib.request
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
AGO=json.loads((ROOT/"data"/"wa-original-agency-alpr-registrations.json").read_text(encoding="utf8"))
SRC=json.loads((ROOT/"data"/"wa-ago-original-policy-source-inspection.json").read_text(encoding="utf8"))
BASE=json.loads((ROOT/"data"/"wa-held-original-policy-diagnostics.json").read_text(encoding="utf8"))
EXPECTED={r["agency_name"]:r for r in BASE["entries"]}
def check_published_qualification(info):
 original=EXPECTED.get(info.get("agency"))
 if not original:return False
 if info.get("diagnosis")!={
  "empty_page_content_streams":"EMPTY_PDF_PAGES_NO_CONTENT_STREAMS",
  "original_pdf_exceeds_16_mb_diagnostic_cap":"OVERSIZE_PDF_BYTE_CAP",
  "strict_parser_fails_image_pdf_lenient_only":"LENIENTLY_READABLE_IMAGE_ORIGINAL_STRICT_PDF_PARSE_FAILS",
  "pdf_reader_dependency_unresolved":"PDF_DEPENDENCY_UNRESOLVED",
  "manual_exceeds_160_page_triage_cap":"OVERSIZE_MANUAL_PAGE_COUNT"
 }[original["diagnosis"]]:return False
 if original["sha256_complete_original"] is not None:
  if info.get("sha256")!=original["sha256_complete_original"] or info.get("bytes")!=original["bytes_complete_original"]:
   return False
  expected_pages=original["page_count_structurally_readable"]
  if expected_pages is not None:
   observed_pages=info.get("strict_true",{}).get("page_count") or info.get("strict_false",{}).get("page_count")
   return observed_pages==expected_pages
  return True
 return info.get("sha256") is None and info.get("bytes",0)>=original["minimum_observed_bytes"]

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("SOURCE_REDIRECT_HELD")
def main():
 indexed={r["agency_name"]:r for r in AGO["registrations"]}
 held=[r for r in SRC["receipts"] if r["inspection_status"] in {"held_unreadable_pdf","held_non_pdf"}]
 assert len(held)==7
 for r in held:
  name=r["agency_name"]
  url=r["policy_source_url"]
  assert indexed[name]["policy_links_from_official_ago_page"]==[url]
  assert url.startswith("https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/") and "VersionId=" in url
  try:
   req=urllib.request.Request(url,headers={"Accept":"application/pdf","User-Agent":"Katoptron-original-AGO-policy-failure-review/1.0"})
   with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as res:
    assert res.status==200 and res.geturl()==url
    typ=res.headers.get("Content-Type","unknown").split(";")[0].strip().lower()
    raw=res.read(16_000_001 if name=="Kirkland Police Department" else 8_000_001)
   info={"agency":name,"source_status":r["inspection_status"],"content_type":typ,
         "bytes":len(raw),"pdf_header":raw.startswith(b"%PDF-")}
   if 100<=len(raw)<=(16_000_000 if name=="Kirkland Police Department" else 8_000_000):
    info["sha256"]=hashlib.sha256(raw).hexdigest()
   else:info["sha256"]=None
   if not 100<len(raw)<=(16_000_000 if name=="Kirkland Police Department" else 8_000_000) or not raw.startswith(b"%PDF-"):
    info["diagnosis"]="OVERSIZE_PDF_BYTE_CAP" if name=="Kirkland Police Department" and raw.startswith(b"%PDF-") else "NOT_PDF_OR_OUT_OF_BOUNDS"
   else:
    for strict in (True,False):
     try:
      pdf=PdfReader(io.BytesIO(raw),strict=strict)
      count=len(pdf.pages)
      info["strict_"+str(strict).lower()]={"page_count":count,"encrypted":pdf.is_encrypted,
         "text_extraction_eligible":False if pdf.is_encrypted else 1<=count<=160}
      if strict and name in {"Kelso Police Department","Puyallup Police Department","Wapato Police Department"}:
       root=pdf.trailer.get("/Root")
       root=root.get_object() if root else {}
       info["document_structure"]={
        "root_keys":sorted(str(k) for k in root.keys())[:20],
        "has_embedded_file_names":bool(root.get("/Names")),
        "has_acroform":bool(root.get("/AcroForm")),
        "has_collection":bool(root.get("/Collection"))
       }
      if (strict and name in {"Kelso Police Department","Puyallup Police Department","Wapato Police Department"}) or (not strict and name=="Kittitas Police Department"):
       from triage_wa_ago_policy_origins import has_embedded_image_resource
       for n,page in enumerate(pdf.pages):
        report={"page":n+1}
        for k,fn in (("text",lambda:len((page.extract_text() or "").strip())),
                      ("image_resource",lambda:has_embedded_image_resource(page))):
         try:report[k]=fn()
         except Exception as e:report[k+"_error"]=type(e).__name__
        for k,fn in (("pypdf_images",lambda:len(page.images)),
                      ("content_length",lambda:len(page.get_contents().get_data()) if page.get_contents() else 0)):
         try:report[k]=fn()
         except Exception as e:report[k+"_error"]=type(e).__name__
        if strict and name in {"Kelso Police Department","Puyallup Police Department","Wapato Police Department"}:
         for k,fn in (("annotations_count",lambda:len(page.get("/Annots",[]))),
           ("page_keys",lambda:sorted(str(k) for k in page.keys())[:20]),
           ("resources_keys",lambda:sorted(str(k) for k in (page.get("/Resources") or {}).keys())[:15])):
          try:report[k]=fn()
          except Exception as e:report[k+"_error"]=type(e).__name__
        info.setdefault("page_structure_probes",[]).append(report)
     except Exception as exc:
      info["strict_"+str(strict).lower()]={"error_type":type(exc).__name__}
    if name=="Kittitas Police Department":
     info["diagnosis"]="LENIENTLY_READABLE_IMAGE_ORIGINAL_STRICT_PDF_PARSE_FAILS"
    elif name in {"Kelso Police Department","Puyallup Police Department","Wapato Police Department"}:
     info["diagnosis"]="EMPTY_PDF_PAGES_NO_CONTENT_STREAMS"
    elif name=="Yakima Police Department":
     info["diagnosis"]="OVERSIZE_MANUAL_PAGE_COUNT"
    else:info["diagnosis"]="PDF_DEPENDENCY_UNRESOLVED"
     info["baseline_qualification_matches"]=check_published_qualification(info)
   print("HELD_WA_ORIGINAL_DIAGNOSIS",json.dumps(info,sort_keys=True))
   if not info["baseline_qualification_matches"]:
    raise ValueError("Previously published source qualification requires re-review")

  except Exception as exc:
   print("HELD_WA_ORIGINAL_DIAGNOSIS",json.dumps({"agency":name,"source_status":r["inspection_status"],
    "diagnosis":"UNAVAILABLE","error_type":type(exc).__name__},sort_keys=True))
   if isinstance(exc,ValueError) and str(exc)=="Previously published source qualification requires re-review":
    raise
if __name__=="__main__":main()
