#!/usr/bin/env python3
"""Source freshness for curated original public independent audit reports.

Never republishes inferred audit conclusions or changes the content-reviewed
manifest; a failed fetch is UNAVAILABLE, not evidence of withdrawal, and must
be independently resolved. No private documents, account identifiers, or
ALPR records are retrieved.
"""
import io
import hashlib
import json
import re
import socket
import urllib.parse
import urllib.request
from pathlib import Path

MAX_BYTES=3*1024*1024
MAX_PAGES=30
AUDIT_HOSTS={"www.lrl.mn.gov"}
MANIFEST=Path(__file__).resolve().parents[1]/"data"/"verified-independent-audits.json"

class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):
  raise ValueError("Government audit moved; new source must be independently verified")

def allowed(url):
 if not isinstance(url,str) or len(url)>1500:return False
 try:
  u=urllib.parse.urlsplit(url)
  return u.scheme=="https" and u.netloc==u.hostname and u.hostname in AUDIT_HOSTS and (
   u.port is None) and not u.fragment and not u.username and not u.password and (
    u.path.startswith("/docs/") and u.path.endswith(".pdf")) and not u.query and not any(
     x in (".","..") for x in u.path.split("/"))
 except (TypeError,ValueError,AttributeError):
  return False

def manifest_rows(source):
 if not isinstance(source,dict) or source.get("schema_version")!=1:
  raise ValueError("Invalid source audit manifest")
 rows=source.get("reports")
 if not isinstance(rows,list) or len(rows)>200:raise ValueError("Unbounded original audit catalog")
 ids=set()
 for row in rows:
  if not isinstance(row,dict) or not allowed(row.get("source_url")):
   raise ValueError("Original government audit provenance invalid")
  key=row.get("id")
  if not isinstance(key,str) or not re.fullmatch(r"[a-z0-9-]{5,120}",key) or key in ids:
   raise ValueError("Duplicate or invalid audit ID")
  ids.add(key)
  if not isinstance(row.get("content_sha256"),str) or not re.fullmatch(r"[0-9a-f]{64}",row["content_sha256"]):
   raise ValueError("Verified source requires a pinned PDF digest")
  if not isinstance(row.get("findings"),list) or not row["findings"] or len(row["findings"])>25:
   raise ValueError("Invalid bounded original claims")
  if not all(isinstance(f,dict) and isinstance(f.get("page"),int) and
             f["page"] in row.get("pages_reviewed",[]) and
             isinstance(f.get("statement"),str) and 40<=len(f["statement"])<850
             for f in row["findings"]):
   raise ValueError("Unverified page references")
 return rows

def get_pdf(url,fetcher=None):
 if not allowed(url):raise ValueError("Unapproved source URL")
 if fetcher is not None:return fetcher(url)
 req=urllib.request.Request(url,headers={"Accept":"application/pdf","User-Agent":"Katoptron-PublicAudits/1.0"})
 opener=urllib.request.build_opener(DenyRedirect())
 with opener.open(req,timeout=15) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Original audit source unavailable or redirected")
  body=res.read(MAX_BYTES+1)
 if len(body)>MAX_BYTES or not body.startswith(b"%PDF-"):
  raise ValueError("PDF not bounded and readable")
 return body

ADDITIONAL_REVIEWED_PAGE_ANCHORS = {
  "champlin-mn-independent-flock-alpr-audit-2025": {
    "2": [
      "champlin police department",
      "6 active stationary/flex flock alpr devices",
      "default 30-"
    ],
    "4": [
      "recommend that the champlin police department develop a breach policy"
    ]
  },
  "corcoran-mn-independent-flock-alpr-audit-2026": {
    "2": [
      "corcoran police department",
      "9 active stationary flock alpr units",
      "default 30-day retention period"
    ],
    "3": [
      "sample for the whole month of april",
      "documented in the flock system by agency and justification"
    ]
  },
  "edina-mn-independent-flock-alpr-audit-2025": {
    "2": [
      "edina police department",
      "18 active stationary flock alpr units",
      "default 30-"
    ],
    "3": [
      "documented by agency name, reason and case number",
      "redacted version of this tracking spreadsheet"
    ]
  },
  "hopkins-mn-independent-flock-alpr-audit-2026": {
    "2": [
      "hopkins police department",
      "14 devices, 13 fixed and one flex",
      "default 30-"
    ],
    "3": [
      "documented by agency name",
      "requesting party and case number"
    ]
  },
  "minnetrista-mn-independent-flock-alpr-audit-2026": {
    "2": [
      "minnetrista police department",
      "4 stationary flock alpr units",
      "default 30-day retention period"
    ],
    "3": [
      "a sample of the whole month of may 2026",
      "documented in the flock system by agency and justification"
    ]
  },
  "orono-mn-independent-flock-alpr-audit-2025": {
    "2": [
      "orono police department",
      "3 active stationary/flex alpr devices",
      "default 30-"
    ],
    "4": [
      "recommend that the orono police department develop a standalone breach policy"
    ]
  },
  "robbinsdale-mn-independent-flock-alpr-audit-2025": {
    "2": [
      "robbinsdale police department",
      "two active stationary flock alpr units",
      "default 30-day retention period"
    ],
    "3": [
      "documented by agency name",
      "requesting party and case number"
    ]
  },
  "south-lake-minnetonka-mn-independent-flock-alpr-audit-2026": {
    "2": [
      "south lake minnetonka police department",
      "4 stationary flock alpr units",
      "default 30-day retention period"
    ],
    "3": [
      "whole month of december",
      "documented in the flock system by agency and justification"
    ]
  },
  "umn-mn-independent-flock-alpr-audit-2025": {
    "2": [
      "umn police department",
      "10 active stationary alpr units",
      "default 30-"
    ],
    "3": [
      "documented by agency name",
      "requesting party and case number"
    ]
  }

  ,"woodbury-mn-independent-alpr-audit-2021": {
    "2": ["woodbury public safety department","up to 2 squad cars","no stationary alpr units","60 day retention period"],
    "3": ["termination of their mobile alpr program in june 2021","requests are documented by agency name"]
  },
  "edina-mn-independent-alpr-audit-2021": {
    "2": ["edina police department","9 squad cars and no stationary alpr units","alpr boss administrative control panel","no more than 60 days"],
    "3": ["sharing among law enforcement agencies","documented by agency name, requesting party and case number"]
  },
  "shakopee-mn-independent-alpr-audit-2022": {
    "1": ["shakopee police department","elsag plate hunter","three patrol vehicles","no stationary or fixed location readers"],
    "2": ["elsag eoc is hard coded","60 days"],
    "3": ["received no requests to share alpr data"]
  },
  "west-saint-paul-mn-independent-flock-alpr-audit-2026": {
    "2": ["west saint paul police department","10 stationary flock alpr units","no mobile flock units","default 30-day retention period"],
    "3": ["sharing among law enforcement agencies","a sample of the whole month of may 2026","documented in the flock system by agency and justification"]
  },
  "wyoming-mn-independent-flock-alpr-audit-2026": {
    "2": ["wyoming police department","4 stationary flock alpr units","no mobile flock units","default 30-day retention period"],
    "3": ["three agencies in which they allow access","written data sharing agreements","a sample of the whole month of july 2026"]
  }
}

HISTORICAL_CURATED_PAGE_ANCHORS = {
  "mn-original-alpr-review-231274": {
    "2": [
      "hennepin county sheriff",
      "3 patrol vehicles",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-260804": {
    "2": [
      "richfield police department",
      "3 squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-200577": {
    "1": [
      "shakopee police department",
      "elsag plate hunter",
      "three patrol vehicles",
      "no stationary or fixed"
    ]
  },
  "mn-original-alpr-review-200436": {
    "2": [
      "robbinsdale police department",
      "2 squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-191277": {
    "2": [
      "edina police department",
      "7 squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-190963": {
    "1": [
      "brooklyn center police department",
      "3 squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-190962": {
    "1": [
      "richfield police department",
      "3 squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-191276": {
    "2": [
      "woodbury public safety",
      "3m boss",
      "three mobile squads"
    ]
  },
  "mn-original-alpr-review-191258": {
    "1": [
      "edina police department",
      "six squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-191256": {
    "1": [
      "brooklyn center police department",
      "three squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-191266": {
    "1": [
      "robbinsdale pd",
      "two squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-191265": {
    "1": [
      "richfield pd",
      "2 squad cars",
      "no stationary alpr units"
    ]
  },
  "mn-original-alpr-review-200649": {
    "2": [
      "shakopee alpr system",
      "elsag",
      "three mobile squads"
    ]
  },
  "mn-original-alpr-review-261168": {
    "2": [
      "west saint paul police department",
      "14 mobile axon units"
    ]
  },
  "mn-original-alpr-review-260189": {
    "2": [
      "robbinsdale police department",
      "11 active mobile axon alpr units"
    ]
  },
  "mn-original-alpr-review-251684": {
    "2": [
      "hennepin county",
      "approximately 32 active axon alpr systems",
      "patrol vehicles"
    ]
  },
  "mn-original-alpr-review-251686": {
    "2": [
      "champlin police department",
      "approximately 14 active axon mobile alpr units"
    ]
  },
  "mn-original-alpr-review-251640": {
    "2": ["umn police department", "approximately 29 active mobile alpr units"]
  },
  "mn-original-alpr-review-191307": {
    "3": ["woodbury", "2 squad cars", "no stationary alpr units"]
  },
  "mn-original-alpr-review-200290": {
    "7": ["hennepin county", "four mobile alprs", "september 24, 2019", "fixed stationary alpr"]
  }
}

def verify_pdf(report,payload,reader_class=None):
 if not isinstance(payload,bytes) or len(payload)>MAX_BYTES or not payload.startswith(b"%PDF-"):
  raise ValueError("Invalid original audit PDF bytes")
 if hashlib.sha256(payload).hexdigest()!=report.get("content_sha256"):
  raise ValueError("Original auditor PDF version changed; needs manual independent re-review")
 if reader_class is None:
  from pypdf import PdfReader
  reader_class=PdfReader
 pdf=reader_class(io.BytesIO(payload),strict=True)
 if pdf.is_encrypted:
  # The exact official Hennepin state-auditor 2020 report is a publicly
  # accessible PDF encrypted with an empty *user* password. Do not accept
  # nonempty credentials, redirects, different report hashes or other PDFs.
  if report["id"]!="mn-original-alpr-review-200290" or not pdf.decrypt(""):
   raise ValueError("Encrypted original is not approved for public anonymous reading")
 if len(pdf.pages)<max(report["pages_reviewed"]) or len(pdf.pages)>MAX_PAGES:
  raise ValueError("Audited page range unavailable")

 def normalized(page):
  return " ".join(str(pdf.pages[page-1].extract_text() or "").lower().split())
 if report["id"]=="shakopee-mn-alpr-independent-audit-2026":
  # These four textual anchors are limited to the five original pages
  # manually reviewed Oct 26, 2026. Content changes require renewed review.
  anchors={
   1:("shakopee police department","flock"),
   2:("flock","retention period"),
   4:("authorization to access data","audit"),
   5:("lynn lembcke","june 15, 2026"),
  }
  for page,phrases in anchors.items():
   text=normalized(page)
   if not all(p in text for p in phrases):
    raise ValueError("Original auditor page text differs; held for independent re-review")
 elif report["id"]=="stillwater-mn-independent-flock-alpr-audit-2026":
  anchors={
   2:("stillwater police department","17 stationary flock","default 30-day retention period"),
   3:("sharing among law enforcement agencies","out-of-state sharing","shared network section"),
  }
  for page,phrases in anchors.items():
   content=normalized(page)
   if not all(p in content for p in phrases):
    raise ValueError("Stillwater original auditor PDF page changed; hold for review")
 elif report["id"]=="hennepin-county-mn-independent-flock-alpr-audit-2025":
  anchors={
   2:("hennepin county","4 active stationary flock","default 30-day retention period"),
   3:("sharing among law enforcement agencies","agency command"),
  }
  for page,phrases in anchors.items():
   content=normalized(page)
   if not all(p in content for p in phrases):
    raise ValueError("Hennepin original auditor PDF page changed; hold for review")
 elif report["id"]=="richfield-mn-independent-flock-alpr-audit-2026":
  anchors={
   2:("richfield police department","8 stationary flock alpr units","default 30-day retention period"),
   3:("the whole month of march","documented in the flock system by agency and justification"),
  }
  for page,phrases in anchors.items():
   if not all(p in normalized(page) for p in phrases):
    raise ValueError("Richfield original auditor PDF page changed; hold for review")
 elif report["id"]=="woodbury-mn-independent-flock-alpr-audit-2026":
  anchors={
   2:("woodbury public safety","17 active stationary flock alpr units","no mobile flock units","default 30-"),
   3:("documented by agency name","requesting party and case number"),
  }
  for page,phrases in anchors.items():
   if not all(p in normalized(page) for p in phrases):
    raise ValueError("Woodbury original auditor PDF page changed; hold for review")
 elif report["id"]=="brooklyn-center-mn-independent-flock-alpr-audit-2025":
  anchors={
   2:("brooklyn center police department","9 active stationary alpr units","no flock mobile units","default 30-day retention period"),
   3:("documented by agency name","requesting party and case number"),
  }
  for page,phrases in anchors.items():
   if not all(p in normalized(page) for p in phrases):
    raise ValueError("Brooklyn Center original auditor PDF page changed; hold for review")
 elif report["id"] in ADDITIONAL_REVIEWED_PAGE_ANCHORS:
  for page,phrases in ADDITIONAL_REVIEWED_PAGE_ANCHORS[report["id"]].items():
   if not all(p in normalized(int(page)) for p in phrases):
    raise ValueError("Additional original auditor PDF page text changed; hold for review")
 elif report["id"] in HISTORICAL_CURATED_PAGE_ANCHORS:
  for page,phrases in HISTORICAL_CURATED_PAGE_ANCHORS[report["id"]].items():
   if not all(p in normalized(int(page)) for p in phrases):
    raise ValueError("Historically reviewed original government auditor page changed; hold for re-review")
 elif report["id"]=="woodbury-mn-independent-flock-alpr-audit-2024":
  anchors={
   2:("woodbury public safety department","flock alpr system","15 active stationary","retention period was set for 30 days"),
   3:("sharing among law enforcement agencies","documented by agency name, requesting party and case number"),
  }
  for page,phrases in anchors.items():
   if not all(p in normalized(page) for p in phrases):
    raise ValueError("Woodbury 2024 original auditor PDF page changed; hold for review")
 elif report["id"]=="shakopee-mn-alpr-independent-audit-2024":
  anchors={
   1:("shakopee police department","elsag plate hunter","three patrol vehicles","no stationary or fixed location readers"),
   2:("elsag eoc","destroy alpr data 60 days","no data older than 60"),
  }
  for page,phrases in anchors.items():
   if not all(p in normalized(page) for p in phrases):
    raise ValueError("Shakopee 2024 original auditor PDF page changed; hold for review")
 else:
  raise ValueError("New audit requires a scoped independent verifier")
 return len(pdf.pages)

def run():
 records=manifest_rows(json.loads(MANIFEST.read_text(encoding="utf-8")))
 for row in records:
  data=get_pdf(row["source_url"])
  pages=verify_pdf(row,data)
  print("Original independent audit source OK:",row["id"],"pages",pages,
        "SHA256",hashlib.sha256(data).hexdigest(),
        "manual findings retained only at their documented source dates")
 print("SOURCE CHECK PASS: original audit bytes checked; no raw plates, source file or private data retained")
if __name__=="__main__":
 try:run()
 except Exception as exc:
  raise SystemExit("SOURCE CHECK UNAVAILABLE OR DRIFTED: "+type(exc).__name__+": "+str(exc)) from None
