#!/usr/bin/env python3
"""Extract *private* bounded numeric/policy candidates from pinned .gov PDF receipts.

No raw PDF text, names, license plates, vehicle searches, or contract excerpts
stored. 'Candidate' does not mean adopted, signed, paid or live. Page-indexed,
hash-pinned suggestions must pass separate human original-document review.
"""
import datetime as dt
import io
import os
import re
import urllib.parse
from acquire_original_government_documents import page_all,rest,fetch
from observe_original_government_pdfs import pdf_link_candidate,pdf_digest,MAX_PDF_BYTES

MAX_PER_RUN=10
MAX_PAGES=12
MAX_CANDIDATES_PER_DOCUMENT=10
AMOUNT=re.compile(r"\$\s*(\d{1,3}(?:,\d{3})+(?:\.\d{2})?|\d{4,7}(?:\.\d{2})?)\b")
RETENTION=re.compile(r"\b(?:retention|retained|retain|purged?|deleted?)\b.{0,110}?\b(\d{1,3})\s+days?\b",re.I|re.S)
EFFECTIVE=re.compile(r"\b(?:effective\s+date|effective\s+on|approval\s+date)\b.{0,60}?\b(20\d{2}[-/](?:0?[1-9]|1[012])[-/](?:0?[1-9]|[12]\d|3[01]))\b",re.I|re.S)
SHARING=re.compile(r"\b(?:data\s+sharing|external\s+agenc(?:y|ies)|sharing\s+permissions?)\b",re.I)
SOURCE=re.compile(r"\bflock\b|\balpr\b|automated\s+license\s+plate",re.I)
PRIVACY_TERMS=re.compile(r"\bretention\b|\baccess\b|\bshare\b|\bpolicy\b|\bcontract\b",re.I)

def candidates(pages,document_url,sha):
    """Use only original page number, typed bound values and receipt identity."""
    if not re.fullmatch(r"[0-9a-f]{64}",sha) or len(pages)>MAX_PAGES:
        raise ValueError("Unbounded or unidentified government original pages")
    out=[];seen=set()
    for number,raw in enumerate(pages,1):
        if not isinstance(raw,str):continue
        # No plate, personal or vehicle identifiers from text are retained.
        body=" ".join(raw[:60000].split())
        if not SOURCE.search(body):continue
        def add(kind,value):
            key=(number,kind,str(value))
            if key not in seen and len(out)<MAX_CANDIDATES_PER_DOCUMENT:
                seen.add(key)
                out.append({"document_url":document_url,"content_sha256":sha,
                    "page_number":number,"fact_type":kind,
                    "normalized_value":str(value),
                    "verification_status":"requires_independent_page_review"})
        for m in list(AMOUNT.finditer(body))[:4]:
            # This is a source-page price-like number, NOT proven Flock cost.
            n=m.group(1).replace(",","")
            if 1000<=float(n)<=10000000:add("amount_candidate",n)
        for m in list(RETENTION.finditer(body))[:4]:
            days=int(m.group(1))
            if 1<=days<=365:add("retention_days_candidate",days)
        for m in list(EFFECTIVE.finditer(body))[:3]:
            date=m.group(1).replace("/","-")
            try:
                import datetime
                parsed=datetime.date.fromisoformat(date)
                add("effective_date_candidate",parsed.isoformat())
            except ValueError:pass
        if SHARING.search(body) and PRIVACY_TERMS.search(body):
            add("sharing_terms_candidate","topic_present_unverified")
    return out

def inspect(receipt,fetcher=fetch,reader_factory=None):
    url=receipt["document_url"]
    sha=receipt["content_sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}",sha):return []
    if reader_factory is None:
        from pypdf import PdfReader
        reader_factory=PdfReader
    try:
        blob,ctype=fetcher(url,MAX_PDF_BYTES)
        if pdf_digest(blob,ctype)!=sha:return []
        pdf=reader_factory(io.BytesIO(blob),strict=False)
        if not 1<=len(pdf.pages)<=250:return []
        pages=[p.extract_text() or "" for p in list(pdf.pages)[:MAX_PAGES]]
        return candidates(pages,url,sha)
    except Exception:
        return []  # Strict hash mismatch, parse errors and inaccessible originals held.

def process(leads,receipts,fetcher=fetch,reader_factory=None):
    eligible={x["document_url"] for x in leads if pdf_link_candidate(x)}
    fresh=sorted([x for x in receipts if x["document_url"] in eligible],
                 key=lambda x:(x["document_url"],x["content_sha256"]))
    records=[]
    for row in fresh[:MAX_PER_RUN]:
        records.extend(inspect(row,fetcher,reader_factory))
    return records,len(fresh)

def main():
    url=os.environ.get("SUPABASE_URL")
    secret=os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not secret:raise RuntimeError("Protected PDF fact candidate credentials missing")
    leads=page_all(url,secret,"flock_original_document_leads",
      "document_url,government_page_url,link_label,review_status")
    receipts=page_all(url,secret,"flock_original_document_pdf_receipts",
      "document_url,content_sha256")
    rows,seen=process(leads,receipts)
    for row in rows:
        rest(url,secret,"flock_original_fact_candidates",method="POST",
          params={"on_conflict":"document_url,content_sha256,page_number,fact_type,normalized_value"},
          body=[row],prefer="resolution=ignore-duplicates,return=minimal")
    print("PRIVATE_ORIGINAL_FACT_EXTRACTION",{
      "receipt_versions_considered":seen,"receipt_version_limit":MAX_PER_RUN,
      "numeric_term_date_review_candidates":len(rows),
      "automatically_published_contract_or_policy_facts":0
    })
if __name__=="__main__":main()
