#!/usr/bin/env python3
"""Verify three page-reviewed Washington AGO-linked public agency ALPR policies.

Agency policy PDFs are not independent audits, Flock proof, camera locations,
sharing relationships, or implementation/compliance certificates.
"""
import hashlib,io,json,re,urllib.request
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"data"/"verified-wa-agency-policies.json"
AGO_PATH=ROOT/"data"/"wa-original-agency-alpr-registrations.json"
EXPECTED={
 "auburn-wa-policy-july-2026":{
  "agency":"Auburn Police Department","pages":8,"date":"2026-07-02",
  "method":"original_pdf_sha256_page_text_anchors",
  "sha":"484830933e46300a5471d3fccc4354f33ae1b683bc8401fa938b8a4d3f53863f",
  "anchors":{2:("21 days","investigating or enforcing federal immigration matters"),
             5:("default retention","traffic studies","commercial vehicle enforcement"),
             6:("external sharing","immigration enforcement agencies","research"),
             7:("annual internal audit","locations of alpr cameras")}
 },
 "normandy-park-wa-policy-june-2026":{
  "agency":"Normandy Park Police Department","pages":5,"date":"2026-06-30",
  "method":"original_pdf_sha256_page_text_anchors",
  "sha":"b4b26800bc0d3966b83df83abd8ccd9eeb7485e61b4057f724adad2352e4e935",
  "anchors":{1:("flock safety camera administrators","flock safety camera users"),
             3:("investigating or enforcing federal immigration matters","flock safety camera data","all stored alpr data shall not be retained for more than 21 days"),
             4:("audit trail data shall be retained for two years","an internal audit will occur at least annually"),
             5:("releasing alpr data","written request","administrative sergeant")}
 },
 "black-diamond-wa-policy-june-2026":{
  "agency":"Black Diamond Police Department","pages":7,"date":"2026-06-23",
  "method":"original_pdf_sha256_visually_reviewed_raster_pages",
  "sha":"8ccf182125bf61bc624be72cb389f5ce218d36cf60f9db62d5ba8d58418f2446",
  "anchors":{1:(),4:()}
 }
}
URLS={
 "auburn-wa-policy-july-2026":"https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Auburn%20PD%20ALPR%20Policy.pdf?VersionId=bPOrBG6TYUmkpHt6dVALLEcyhx2utLnH",
 "black-diamond-wa-policy-june-2026":"https://blackdiamondwa.gov/DocumentCenter/View/4324/BDPD-ALPR-Policy",
 "normandy-park-wa-policy-june-2026":"https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Normandy%20Park%20PD%20Policy.pdf?VersionId=18O0TMpqPRPGCuXKIAFSRKWNSwGnRuaY",
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Original policy redirect is unreviewed")
def fetch(url):
 if url not in URLS.values():raise ValueError("Unapproved government policy URL")
 req=urllib.request.Request(url,headers={
  "Accept":"application/pdf","User-Agent":"Katoptron-WA-original-government-policy-verifier/1.0"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Original source URL changed")
  data=res.read(8_000_001)
 if not 100<len(data)<=8_000_000 or not data.startswith(b"%PDF-"):
  raise ValueError("Unbounded or non-PDF response")
 return data
def validate(data,registry):
 if (not isinstance(data,dict) or data.get("schema_version")!=1 or
     not isinstance(data.get("documents"),list) or len(data["documents"])!=3):
  raise ValueError("Three-policy evidence catalog invalid")
 if (not isinstance(registry,dict) or registry.get("source_url")!="https://www.atg.wa.gov/ALPR" or
     not isinstance(registry.get("registrations"),list)):raise ValueError("Official AGO registry invalid")
 indexed={r["agency_name"]:r for r in registry["registrations"]}
 seen=set()
 for row in data["documents"]:
  ident=row.get("id")
  if ident not in EXPECTED or ident in seen:raise ValueError("Unknown or duplicate reviewed policy")
  seen.add(ident)
  spec=EXPECTED[ident]
  if (row.get("agency_name")!=spec["agency"] or row.get("state")!="WA" or
      row.get("source_url")!=URLS[ident] or row.get("content_sha256")!=spec["sha"] or
      row.get("page_count")!=spec["pages"] or row.get("policy_manual_imprint")!=spec["date"] or
      row.get("source_tier")!="agency_published_policy_via_state_ag_registry" or
      row.get("verification_method")!=spec["method"]):
   raise ValueError("Source identity, original hash, or provenance changed")
  entry=indexed.get(row["agency_name"])
  if (not entry or entry.get("policy_links_from_official_ago_page")!=[URLS[ident]] or
      row.get("ago_registration_date")!=entry.get("submitted_on")):
   raise ValueError("Policy not exactly linked by official AGO registration snapshot")
  pages=row.get("pages_reviewed")
  if not isinstance(pages,list) or sorted(pages)!=sorted(spec["anchors"]) or len(set(pages))!=len(pages):
   raise ValueError("Reviewed-page evidence scope changed")
  findings=row.get("findings",[])
  if (not isinstance(findings,list) or len(findings)<2 or
      any(f.get("page") not in pages or
          not isinstance(f.get("statement"),str) or not 80<=len(f["statement"])<=900
          for f in findings)):
   raise ValueError("Public page-linked policy finding invalid")
  if ident.startswith("black-diamond") and "visually" not in row.get("verification_note",""):
   raise ValueError("Scanned source needs visual-review labeling")
 return data["documents"]
def verify(row,raw,reader=PdfReader):
 if not isinstance(raw,bytes) or not raw.startswith(b"%PDF-") or not 100<len(raw)<=8_000_000:
  raise ValueError("Original PDF bytes not available")
 if hashlib.sha256(raw).hexdigest()!=row["content_sha256"]:
  raise ValueError("Original policy byte hash drift")
 pdf=reader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or len(pdf.pages)!=row["page_count"]:
  raise ValueError("Original policy page count or encryption changed")
 for page,phrases in EXPECTED[row["id"]]["anchors"].items():
  obj=pdf.pages[page-1]
  if row["verification_method"]=="original_pdf_sha256_visually_reviewed_raster_pages":
   if not obj.images:raise ValueError("Reviewed scanned policy page image missing")
  else:
   text=" ".join((obj.extract_text() or "").casefold().split())
   missing=[phrase for phrase in phrases if phrase not in text]
   if missing:raise ValueError("Page-text anchor drift in policy original p"+str(page))
 return len(pdf.pages)
def main():
 data=json.loads(PATH.read_text(encoding="utf8"))
 registry=json.loads(AGO_PATH.read_text(encoding="utf8"))
 for row in validate(data,registry):
  verify(row,fetch(row["source_url"]))
  print("PAGE_REVIEWED_WA_POLICY_VERIFIED",row["agency_name"],"PAGES",
        row["page_count"],"SHA256",row["content_sha256"],
        "SOURCE_TIER",row["verification_method"])
 print("THREE ORIGINAL AGO-LINKED POLICIES VERIFIED; SOURCE-ATTRIBUTED FLOCK POLICY REFERENCE DOES NOT PROVE CURRENT DEPLOYMENT, CAMERA COUNT, ACCESS OR COMPLIANCE")
if __name__=="__main__":
 try:main()
 except Exception as exc:
  raise SystemExit("Washington original-policy verification held: "+type(exc).__name__+" "+str(exc)[:140]) from None
