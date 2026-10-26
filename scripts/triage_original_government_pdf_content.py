#!/usr/bin/env python3
"""Bounded private PDF signal triage. NEVER a content verification publisher.

Input is an already indexed original-government PDF byte receipt; no raw
document text, personal identifiers, legal conclusion, date, amount or
contract/signature details are persisted. Signals mean only keywords seen.
"""
import datetime as dt
import hashlib
import io
import os
import re
from acquire_original_government_documents import page_all, rest, fetch
from observe_original_government_pdfs import pdf_link_candidate,pdf_digest,MAX_PDF_BYTES

MAX_PER_RUN=10
MAX_PAGES_EXAMINED=12
MAX_PAGES_REPORTED=1000
UTC=dt.timezone.utc
SIGNALS={
 "flock_word":r"\bflock\b",
 "alpr_word":r"\bALPR\b|automated license plate read",
 "contract_word":r"\b(contract|agreement|purchase order)\b",
 "retention_word":r"\b(retention|retain|delete)\b",
 "sharing_word":r"\b(shar(?:e|ed|ing)|receiving agenc(?:y|ies)|access grant)\b",
 "governing_action_word":r"\b(council|resolution|motion|vote)\b",
 "signature_reference_word":r"\b(signature|signed|execution)\b"
}
def metadata_flags(text):
 """Boolean-only terms: no amounts, names, plates or raw excerpts."""
 text=text[:120000]
 return {key:bool(re.search(pattern,text,re.I)) for key,pattern in SIGNALS.items()}

def select_pending(leads,receipts,prior,now=None,limit=MAX_PER_RUN):
 now=now or dt.datetime.now(UTC)
 permitted={x["document_url"] for x in leads if pdf_link_candidate(x)}
 pending=[]
 for receipt in receipts:
  key=(receipt["document_url"],receipt["content_sha256"])
  if key[0] not in permitted or not re.fullmatch(r"[0-9a-f]{64}",key[1]):
   continue
  prior_row=prior.get(key)
  if prior_row:
   if prior_row.get("triage_status")!="held_parse_error":
    continue
   try:
    stamp=dt.datetime.fromisoformat(prior_row["triaged_at"].replace("Z","+00:00"))
    if stamp.tzinfo is None or stamp+dt.timedelta(days=7)>now:continue
   except (KeyError,ValueError,TypeError,AttributeError):
    continue
  pending.append((bool(prior_row),receipt))
 pending.sort(key=lambda pair:(pair[0],pair[1]["document_url"],pair[1]["content_sha256"]))
 # Prevent repeated historical receipts from starving unseen current versions.
 return [item for _,item in pending[:limit]]

def read_metadata(payload,reader_factory=None):
 if reader_factory is None:
  from pypdf import PdfReader
  reader_factory=PdfReader
 try:
  pdf=reader_factory(io.BytesIO(payload),strict=False)
  pages=len(pdf.pages)
  if pages>MAX_PAGES_REPORTED:
   return {"pages_reported":MAX_PAGES_REPORTED,"pages_examined":0,
           "triage_status":"held_page_limit","document_signal_flags":{}}
  pieces=[]
  for idx in range(min(pages,MAX_PAGES_EXAMINED)):
   text=pdf.pages[idx].extract_text()
   if text:pieces.append(text[:10000])
  joined=" ".join(pieces)
  return {"pages_reported":pages,"pages_examined":min(pages,MAX_PAGES_EXAMINED),
          "triage_status":"readable_document_indicators_only" if joined.strip() else "no_extractable_text",
          "document_signal_flags":metadata_flags(joined)}
 except Exception:
  return {"pages_reported":0,"pages_examined":0,
          "triage_status":"held_parse_error","document_signal_flags":{}}

def triage(leads,receipts,prior,fetcher=fetch,reader_factory=None,now=None):
 now=now or dt.datetime.now(UTC)
 rows=[]
 for receipt in select_pending(leads,receipts,prior,now):
  try:
   payload,media=fetcher(receipt["document_url"],MAX_PDF_BYTES)
   # If a source changed since its receipt, do NOT attach content flags to
   # the older hash; next receipt run must observe the new PDF first.
   digest=pdf_digest(payload,media)
   if digest!=receipt["content_sha256"]:continue
  except Exception:continue
  record=read_metadata(payload,reader_factory)
  rows.append({"document_url":receipt["document_url"],
               "content_sha256":digest,"triaged_at":now.isoformat(),
               "evidence_tier":"automated_private_unverified_indicators",
               **record})
 return rows

def main():
 api=os.environ.get("SUPABASE_URL","")
 secret=os.environ.get("SUPABASE_SERVICE_ROLE_KEY","")
 if not api or not secret:raise RuntimeError("Protected original-document triage credentials missing")
 leads=page_all(api,secret,"flock_original_document_leads",
    "document_url,government_page_url,link_label,review_status")
 receipts=page_all(api,secret,"flock_original_document_pdf_receipts",
    "document_url,content_sha256,last_observed_at")
 previous=page_all(api,secret,"flock_original_pdf_content_triage",
    "document_url,content_sha256,triage_status,triaged_at")
 previous_by_key={(p["document_url"],p["content_sha256"]):p for p in previous}
 results=triage(leads,receipts,previous_by_key)
 for entry in results:
  rest(api,secret,"flock_original_pdf_content_triage",method="POST",
    params={"on_conflict":"document_url,content_sha256"},body=[entry],
    prefer="resolution=merge-duplicates,return=minimal")
 # Publish only aggregate counts of successful machine-readable triage;
 # never raw private URL, content, name, page, or pattern match.
 merged={ (r["document_url"],r["content_sha256"]):r for r in previous }
 merged.update({(r["document_url"],r["content_sha256"]):r for r in results})
 n=len({u for (u,_),r in merged.items()
     if r["triage_status"] in ("readable_document_indicators_only","no_extractable_text")})
 day=dt.datetime.now(UTC).date().isoformat()
 rest(api,secret,"flock_original_acquisition_public_metrics",method="PATCH",
      params={"metric_date":"eq."+day},body={"pdf_content_triaged_documents":n},
      prefer="return=minimal")
 print("Original linked PDF receipt versions:",len(receipts),
       "metadata triage attempts saved:",len(results),
       "PDF URLs metadata-triaged:",n,
       "independently content-verified by this worker: 0")

if __name__=="__main__":
 try:main()
 except Exception as exc:
  raise SystemExit("Original PDF content triage held: "+type(exc).__name__) from None
