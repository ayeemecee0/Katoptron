#!/usr/bin/env python3
"""Resolve the government hyperlink triage queue into actionable private dispositions.

This does NOT publish facts or decide whether a government actually installed
Flock technology. It closes only irrelevant navigation-link candidates; real
government originals require independently observed bytes and content review.
"""
import datetime as dt
import os
import re
import urllib.parse
from acquire_original_government_documents import page_all,rest

KEYWORDS=re.compile(r"\bflock\b|\balpr\b|license[-_ ]plate[-_ ]read|\blpr\b",re.I)
GENERIC_NAV=re.compile(r"(?:^|[/ _-])(?:city[-_ ]?council|mayor[-_ ]?city[-_ ]?council|"
 "city[-_ ]?auditor|independent[-_ ]?police[-_ ]?auditor|"
 "purchasing[-_ ]?contract[-_ ]?administration|"
 "council[-_ ]?agendas?[-_ ]?(?:and[-_ ])?minutes|"
 "council[-_ ]?appointed[-_ ]?officers|policy[-_ ]?and[-_ ]?services[-_ ]?committee|"
 "city[-_ ]?policy[-_ ]?initiatives|privacy[-_ ]?policy|"
 "city[-_ ]?clerk|body[-_ ]?cam(?:era)?[-_ ]?audit)(?:$|[/ _.?-])",re.I)

def classify(lead,receipt_urls,verified_urls):
    url=lead["document_url"]
    label=lead.get("link_label") or ""
    path=urllib.parse.urlsplit(url).path
    kind=lead.get("document_class") or "unclassified"
    name=label+" "+path.replace("-"," ").replace("_"," ")
    specific=bool(KEYWORDS.search(name))
    ext=path.lower()
    if url in verified_urls and lead.get("review_status")=="document_content_verified":
        status,reason,action=("verified_original_content","prior_content_review_receipt",
          "Retain original-page review and periodically recheck source hash")
    elif not specific and GENERIC_NAV.search(name) and not ext.endswith((".pdf",".csv",".doc",".docx")):
        status,reason,action=("rejected_generic_navigation","generic_citywide_navigation_not_flock_original",
          "No publication; only reopen if a new source-specific child document is discovered")
    elif ".csv" in ext or kind=="sharing_export" and "csv" in name.lower():
        status,reason,action=("held_original_csv_authentication","csv_not_reviewed_for_first_party_access",
          "Download same-government CSV; verify headers, date, agency and written permission scope")
    elif ext.endswith(".pdf") or "pdf" in label.lower() or ".pdf" in ext:
        if url in receipt_urls:
            status,reason,action=("held_original_pdf_content_review","bytes_observed_not_claim_verified",
              "Independently inspect original PDF pages, execution status, terms and dates")
        else:
            status,reason,action=("held_original_pdf_acquisition","no_confirmed_original_pdf_receipt",
              "Fetch original government PDF bytes and record SHA-256 before content review")
    elif ext.endswith((".doc",".docx",".xls",".xlsx")):
        status,reason,action=("held_original_other_file_review","file_contents_not_authenticated",
          "Acquire original bytes, validate file and inspect claims independently")
    elif specific:
        status,reason,action=("held_original_web_content_review","flock_alpr_web_link_unreviewed",
          "Inspect source publisher and source-specific original statements; record review receipt")
    else:
        status,reason,action=("held_government_context_review","unverified_government_context_link",
          "Verify a direct ALPR/Flock-specific record is present before publication")
    return {"document_url":url,"disposition":status,"reason_code":reason,
      "next_action":action,"document_class":kind,
      "classified_at":dt.datetime.now(dt.timezone.utc).isoformat()}

def classify_all(leads,receipts,reviews):
    receipt_urls={x["document_url"] for x in receipts}
    verified_urls={x["document_url"] for x in reviews}
    result=[classify(row,receipt_urls,verified_urls) for row in leads]
    if len({x["document_url"] for x in result})!=len(leads):
        raise ValueError("Nonunique original lead identities")
    return result

def main():
    url=os.environ.get("SUPABASE_URL")
    key=os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:raise RuntimeError("Private original-lead classification credentials absent")
    leads=page_all(url,key,"flock_original_document_leads",
      "document_url,link_label,document_class,review_status")
    receipts=page_all(url,key,"flock_original_document_pdf_receipts","document_url")
    reviews=page_all(url,key,"flock_original_document_content_review_receipts","document_url")
    classified=classify_all(leads,receipts,reviews)
    for i in range(0,len(classified),100):
        rest(url,key,"flock_original_lead_dispositions",method="POST",
          params={"on_conflict":"document_url"},body=classified[i:i+100],
          prefer="resolution=merge-duplicates,return=minimal")
    counts={}
    for row in classified:counts[row["disposition"]]=counts.get(row["disposition"],0)+1
    # Report category counts only, no URLs, person or private text.
    print("ORIGINAL_GOV_LEAD_DISPOSITIONS",dict(sorted(counts.items())))
    print("Classified",len(classified),"original source links; new independently verified fact claims: 0")

if __name__=="__main__":
    main()
