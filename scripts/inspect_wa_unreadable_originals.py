#!/usr/bin/env python3
"""Read-only original-source failure classification for seven held AGO policy PDFs.

Output metadata only. Never print document contents or follow unapproved URL
redirects. Do not automatically promote a reparsed PDF into verified findings.
"""
import io,json,urllib.request
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
AGO=json.loads((ROOT/"data"/"wa-original-agency-alpr-registrations.json").read_text(encoding="utf8"))
SRC=json.loads((ROOT/"data"/"wa-ago-original-policy-source-inspection.json").read_text(encoding="utf8"))
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
   if not 100<len(raw)<=(16_000_000 if name=="Kirkland Police Department" else 8_000_000) or not raw.startswith(b"%PDF-"):
    info["diagnosis"]="NOT_PDF_OR_OUT_OF_BOUNDS"
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
    info["diagnosis"]="REQUIRES_SEPARATE_MANUAL_REVIEW"
   print("HELD_WA_ORIGINAL_DIAGNOSIS",json.dumps(info,sort_keys=True))
  except Exception as exc:
   print("HELD_WA_ORIGINAL_DIAGNOSIS",json.dumps({"agency":name,"source_status":r["inspection_status"],
    "diagnosis":"UNAVAILABLE","error_type":type(exc).__name__},sort_keys=True))
if __name__=="__main__":main()
