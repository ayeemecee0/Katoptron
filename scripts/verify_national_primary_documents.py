#!/usr/bin/env python3
"""Verify source-pinned original government ALPR primary documents.

Nine exact public government PDFs, mutually exclusive role and status types.
A PDF with an unreviewed redirect is HELD rather than grandfathered into facts.
No full PDF, person-level plate read, private search log or movement data stored.
"""
import hashlib,io,json,re,urllib.request
from pathlib import Path
from pypdf import PdfReader
from inspect_national_link_candidates import SOURCES,fetch
MOLINE_ID="moline-il-signed-flock-order-2024"
MOLINE_URL="https://www.moline.il.us/DocumentCenter/View/15716/Flock-Safety-2023"
VISUAL_PAGES={2,3,5}
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Original government publisher redirect")
def fetch_scanned_moline_original():
 op=urllib.request.build_opener(DenyRedirect())
 req=urllib.request.Request(MOLINE_URL,headers={"Accept":"application/pdf","User-Agent":"Katoptron-original-government-Moline/1.0"})
 with op.open(req,timeout=25) as res:
  if res.status!=200 or res.geturl()!=MOLINE_URL:raise ValueError("Unexpected original URL")
  payload=res.read(8_000_001)
 if not 100<len(payload)<=8_000_000 or not payload.startswith(b"%PDF-"):
  raise ValueError("Source no longer a bounded PDF")
 return payload
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"data"/"verified-national-government-documents.json"
ANCHORS={
 "san-mateo-ca-press-advisory":{1:["august 3, 2026","civil grand jury","policy maintenance","in-state data-sharing"]},
 "austin-tx-auditor-slides":{5:["~117 million","audits generally complied"],9:["contract with flock safety","unintended use"]},
 "green-bay-wi-monthly-2026":{1:["october 1, 2026","443,664","9,534","522","brown county","de pere"]},
 "austin-tx-oversight-memo-2023":{1:["march 31, 2023","state of development","resolution 56"],3:["february 7th meeting","zoombombed"]},
 "green-bay-wi-policy-may-2026":{2:["2026/05/04","no longer than 30 days","political rallies"]},
 "green-bay-wi-policy-draft-sept-2026":{2:["***draft***","immigration law"],4:["***draft***","maintained for 7 days"],6:["***draft***","one percent of all searches"]},
 "green-bay-wi-flock-order-2025":{2:["60 months","renewal term: 36 months","retention period: 30 days","42","1,392,000.00"],4:["year 5","$291,000.00","$1,392,000.00"]},
 "austin-tx-commission-recommendation":{1:["recommendation 20250602-006","june 2, 2025"],3:["recommends an immediate halt","vote: 6-0"]}
}
ROLE={
 "san-mateo-ca-press-advisory":("official_press_release_derivative","government_independent_oversight"),
 "austin-tx-auditor-slides":("official_auditor_presentation_derivative","government_independent_oversight"),
 "green-bay-wi-monthly-2026":("agency_monthly_aggregate_report","police_department"),
 "austin-tx-oversight-memo-2023":("original_government_oversight_memo","government_independent_oversight"),
 "green-bay-wi-policy-may-2026":("published_department_policy","police_department"),
 "green-bay-wi-policy-draft-sept-2026":("draft_policy_unadopted","police_department"),
 "green-bay-wi-flock-order-2025":("government_published_vendor_order_form","police_department"),
 "austin-tx-commission-recommendation":("advisory_recommendation_not_binding_action","government_advisory_commission"),
 "moline-il-signed-flock-order-2024":("signed_city_published_vendor_order_form_scanned","police_department")
}
def valid(records):
 if not isinstance(records,dict) or records.get("schema_version")!=1 or not isinstance(records.get("documents"),list) or len(records["documents"])!=9:
  raise ValueError("Original government document ledger count/schema invalid")
 seen=set()
 for row in records["documents"]:
  ident=row.get("id")
  if ident not in ROLE or ident in seen:raise ValueError("Original document identity unknown/duplicate")
  seen.add(ident)
  source_url=MOLINE_URL if ident==MOLINE_ID else SOURCES[ident][0]
  if row.get("source_url")!=source_url or (row.get("kind"),row.get("publisher_role"))!=ROLE[ident]:
   raise ValueError("Original source or document status changed")
  if not re.fullmatch("[a-f0-9]{64}",row.get("content_sha256","")):raise ValueError("Missing full original SHA")
  if row.get("page_count") not in range(1,121):
   raise ValueError("Original PDF page bounds invalid")
  if ident==MOLINE_ID:
   if (row["page_count"]!=6 or set(row.get("pages_reviewed",[]))!=VISUAL_PAGES or
       row.get("verification_method")!="visual_page_review_sha256_pinned_scanned_pdf" or
       row.get("source_date")!="2024-12-04" or
       "visually_reviewed_original_signatures" not in row.get("status","")):
    raise ValueError("Visual review scope or original signed date changed")
  elif not set(ANCHORS[ident]).issubset(set(row.get("pages_reviewed",[]))):
   raise ValueError("Page review trace incomplete")
  findings=row.get("findings",[])
  if not isinstance(findings,list) or not 1<=len(findings)<=8 or any(not isinstance(f,dict) or f.get("page") not in row["pages_reviewed"] or len(f.get("statement",""))<45 for f in findings):
   raise ValueError("Page-bound public findings incomplete")
  if row["kind"]=="draft_policy_unadopted" and "draft" not in row.get("status",""):
   raise ValueError("Never promote unadopted proposal")
  if row["kind"]=="advisory_recommendation_not_binding_action" and "not_city_council" not in row.get("status",""):
   raise ValueError("Commission recommendation cannot become city action")
  if row["kind"]=="government_published_vendor_order_form" and "execution_date_not" not in row.get("status",""):
   raise ValueError("Execution not established")
 held=records.get("source_review_held",[])
 if len(held)!=1 or held[0].get("id")!="san-bruno-ca-alpr-policy" or "redirect" not in held[0].get("reason","").lower():raise ValueError("Held San Bruno source cannot be silently classified as verified")
 return records["documents"]
def verify(row,raw,reader=PdfReader):
 if not isinstance(raw,bytes) or not raw.startswith(b"%PDF-") or len(raw)>8_000_000 or len(raw)<100:
  raise ValueError("Original source bytes unavailable")
 if hashlib.sha256(raw).hexdigest()!=row["content_sha256"]:
  raise ValueError("Original government document hash drift")
 pdf=reader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or len(pdf.pages)!=row["page_count"]:raise ValueError("Original page count or encryption changed")
 for page,need in ANCHORS[row["id"]].items():
  text=" ".join((pdf.pages[page-1].extract_text() or "").lower().split())
  if not all(x in text for x in need):
   raise ValueError("Original page anchor drift: "+row["id"]+" p"+str(page)+" missing "+",".join(x for x in need if x not in text)[:120])
 return len(pdf.pages)
def main():
 ledger=json.loads(PATH.read_text(encoding="utf-8"))
 for row in valid(ledger):
  pdf=fetch(row["id"])
  print("GOVERNMENT_PRIMARY_ORIGINAL_VERIFIED",row["state"],row["id"],"PAGES",verify(row,pdf),
        "SHA",row["content_sha256"],"ROLE",row["kind"])
 print("EIGHT ORIGINALS VERIFIED; 1 BLOCKED SOURCE REMAINS HELD; no raw personal plate or nonpublic data")
if __name__=="__main__":
 try:main()
 except Exception as exc:
  raise SystemExit("Original government document held: "+type(exc).__name__+" "+str(exc)[:220]) from None
