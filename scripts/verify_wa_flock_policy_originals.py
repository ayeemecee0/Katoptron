#!/usr/bin/env python3
"""Fail-closed verification of eight individually reviewed AGO-sourced WA Flock documents.

No invented implementation claims. Policy text differs from dated agency
inventory assertions and from verified installed camera positions.
"""
import hashlib,io,json,urllib.request
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"data"/"verified-wa-flock-policy-originals.json"
AGO=ROOT/"data"/"wa-original-agency-alpr-registrations.json"
TRIAGE=ROOT/"data"/"wa-ago-original-policy-source-inspection.json"
# Only original page-text anchors manually checked in the nine-document review.
EXPECTED={
 "arlington-wa-fleet-policy-2026":("Arlington Police Department","2026-03-30","agency_alpr_policy",{1:("arlington police department policy 708","flock safety systems","axon fleet 3")}),
 "des-moines-wa-flock-search-policy-2026":("Des Moines Police Department","2026-07-08","agency_alpr_policy",{3:("when conducting searches using flock safety software","the specific crime you are investigating")}),
 "federal-way-wa-bulletin-2026":("Federal Way Police Department","2026-05-15","agency_training_bulletin",{2:("one flock safety location consisting of four fixed cameras","proposed addition of two cameras at one additional location","four licensed avigilon alpr cameras","vehicle-mounted alpr systems")}),
 "mukilteo-wa-flock-retention-policy-2026":("Mukilteo Police Department",None,"agency_alpr_policy",{6:("flock safety stores data","flock safety purges this data after twenty one (21) days","digital evidence")}),
 "prosser-wa-flock-transparency-policy-2026":("Prosser Police Department","2026-05-13","agency_alpr_policy",{2:("flock safety alpr use metrics","the number of alprs owned or operated by prosser police department")}),
 "sedro-woolley-wa-flock-policy-2026":("Sedro-Woolley Police Department","2026-06-18","agency_alpr_policy",{4:("when conducting searches using flock safety software","the case number, or cad incident number"),5:("shall not be retained longer than 21 days","the vendor purges this data after thirty (21) days of storage")}),
 "walla-walla-wa-flock-policy-2026":("Walla Walla Police Department","2026-09-16","agency_alpr_policy",{3:("flock safety alpr use metrics","the number of searches in a 21-day period")}),
 "whitman-wa-flock-system-policy-2026":("Whitman County Sheriff's Office",None,"agency_alpr_policy",{1:("flock safety system","deployed exclusively in fixed locations"),4:("alpr data shall not be retained longer than 21 days","6.2 external sharing")})
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Changed source URL redirect denied")
def originals():
 return (json.loads(CAT.read_text(encoding="utf8")),json.loads(AGO.read_text(encoding="utf8")),
         json.loads(TRIAGE.read_text(encoding="utf8")))
def validate(cat,ago,triage):
 if (cat.get("schema_version")!=1 or not isinstance(cat.get("documents"),list) or
     len(cat["documents"])!=len(EXPECTED) or
     ago.get("source_url")!="https://www.atg.wa.gov/ALPR" or
     triage.get("scope")!="source_metadata_only_no_automatic_fact_publication"):
  raise ValueError("Eight government-source policies or AGO provenance unavailable")
 indexed={r["agency_name"]:r for r in ago["registrations"]}
 pinned={r["agency_name"]:r for r in triage["receipts"]}
 seen=set()
 for r in cat["documents"]:
  id=r.get("id")
  if id not in EXPECTED or id in seen:raise ValueError("Duplicated, missing or unreviewed source identity")
  seen.add(id)
  agency,imprint,kind,anchors=EXPECTED[id]
  meta=pinned.get(agency)
  state=indexed.get(agency)
  if (not meta or not state or
      r.get("agency_name")!=agency or r.get("document_imprint_date")!=imprint or
      r.get("policy_kind")!=kind or r.get("state")!="WA" or
      r.get("source_tier")!="individual_page_review_of_agency_submitted_original_policy_or_bulletin" or
      r.get("ago_registration_date")!=state.get("submitted_on") or
      state.get("policy_links_from_official_ago_page")!=[r.get("source_url")] or
      meta.get("inspection_status")!="exact_pdf_text_detected" or
      r.get("source_url")!=meta.get("policy_source_url") or
      r.get("content_sha256")!=meta.get("sha256") or
      r.get("page_count")!=meta.get("page_count") or
      r.get("pages_reviewed")!=sorted(anchors)):
   raise ValueError("Source content, publisher, dated category or reviewed page provenance mismatch")
  finds=r.get("findings")
  if (not isinstance(finds,list) or not 1<=len(finds)<=4 or
      {f.get("page") for f in finds}!=set(anchors) or
      any(f.get("page") not in anchors or not isinstance(f.get("category"),str) or
          not isinstance(f.get("statement"),str) or
          not 95<=len(f["statement"])<=650 for f in finds) or
      any(k in r for k in ("camera_coordinates","operational_status","verified_deployed_camera_count","sharing_edges"))):
   raise ValueError("Unreviewed or unsupported public original-page claim")
  if id=="federal-way-wa-bulletin-2026" and not any("proposed" in f["statement"].lower() for f in finds):
   raise ValueError("Federal Way must distinguish proposal from historically reported installation")
  if id=="sedro-woolley-wa-flock-policy-2026" and not any("contradictory" in f["statement"].lower() for f in finds):
   raise ValueError("Sedro-Woolley internally contradictory number must be exposed")
 if set(EXPECTED)!=seen:raise ValueError("Missing original agency publisher")
 return cat["documents"]
def fetch(url):
 if not isinstance(url,str) or not url.startswith("https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/") or "VersionId=" not in url:
  raise ValueError("Unapproved public source")
 req=urllib.request.Request(url,headers={"Accept":"application/pdf",
  "User-Agent":"Katoptron-reviewed-Washington-original-government-policy/1.0"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Original source moved")
  raw=res.read(8_000_001)
 if not 100<len(raw)<=8_000_000 or not raw.startswith(b"%PDF-"):raise ValueError("Not a bounded original PDF")
 return raw
def verify(row,raw,reader=PdfReader):
 if hashlib.sha256(raw).hexdigest()!=row["content_sha256"]:
  raise ValueError("Original PDF content changed")
 pdf=reader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or len(pdf.pages)!=row["page_count"]:
  raise ValueError("Original PDF page count changed or encrypted")
 for p,terms in EXPECTED[row["id"]][3].items():
  t=" ".join((pdf.pages[p-1].extract_text() or "").casefold().split())
  for term in terms:
   if term not in t:raise ValueError("Original page anchor changed: "+row["agency_name"]+" page "+str(p))
 return row["page_count"]
def main():
 cat,ago,triage=originals()
 for r in validate(cat,ago,triage):
  n=verify(r,fetch(r["source_url"]))
  print("SOURCE_DATED_WA_FLOCK_POLICY_REVIEW_PASS",r["agency_name"],n,"pages",
        "SHA256",r["content_sha256"],"FINDINGS",len(r["findings"]))
 print("EIGHT INDIVIDUALLY SOURCE-VERIFIED DOCUMENTS: POLICIES AND BULLETIN; NO CURRENT CAMERA INVENTORY OR COMPLIANCE CLAIM")
if __name__=="__main__":
 try:main()
 except Exception as exc:
  raise SystemExit("Washington Flock original-page review held: "+type(exc).__name__+" "+str(exc)[:150]) from None
