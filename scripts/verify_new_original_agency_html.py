#!/usr/bin/env python3
"""Live first-party HTML receipt and anchor verification for new civic dossiers.

Receipts prove original publisher text, NOT live camera operation, signed
termination or executed contracts. Fail closed on drift and untrusted redirect.
Never send historical docket rows to subscribers as newly observed changes.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
from convert_official_flock_disclosures import PlainText,normalize

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data"/"qualified-original-government-docket-2026-10-29.json"
OUT=ROOT/".katoptron-ci"/"extended-civic-original-html-receipts.json"
MAX_BYTES=2_500_000
ANCHORS={
 "lakewood-ca-council-rejects-flock-2026":"voted 3–2 not to move forward",
 "sheboygan-wi-flock-termination-request-2026":"to end the city's contract with Flock Safety",
 "grand-rapids-mi-flock-oversight-order-proposed-2026":"issue an administrative order by mid-September",
 "henrico-va-flock-contract-termination-announced-2026":"terminating its contract with Flock Safety",
 "fridley-mn-flock-access-restrictions-2026":"decided to continue the program",
 "richland-wa-flock-suspension-announced-2026":"temporarily suspend use of its automated license plate reader",
 "liberty-hill-tx-flock-removal-city-statement-2026":"were removed by City staff",
 "elgin-tx-flock-program-pause-2026":"pause its use of the FLOCK Safety ALPR system",
 "redmond-wa-flock-contract-termination-vote-2026":"voted 7-0 in favor of terminating",
 "tukwila-wa-revised-flock-contract-adoption-2026":"adopted the revised contract on 5/18/26",
 "mill-valley-ca-flock-alpr-disabled-government-statement-2026":"Both the ALPR and live-feed cameras have been disabled since September 9, 2026.",
 "richmond-va-flock-nonrenewal-mayor-announcement-2026":"the City will not move forward with the Flock ALPR contract when it’s up for renewal.",
 "panama-city-beach-fl-police-flock-suspension-2026":"suspending its use of the Flock Automated License Plate Reader system effective immediately",
 "fort-wayne-in-flock-discontinuation-chief-statement-2026":"the decision was made to discontinue the Fort Wayne Police Department’s use of Flock.",
 "lynchburg-va-flock-alpr-pause-police-original-2026":"temporarily pause the operation of its fifteen fixed Flock"
}

def valid(url):
 try:
  p=urllib.parse.urlsplit(url)
  return (p.scheme=="https" and p.hostname and p.hostname.endswith(".gov") and
   p.netloc==p.hostname and not p.username and not p.password and not p.fragment
   and p.port is None and len(p.path)>4)
 except (ValueError,TypeError):return False

class SameHostOnly(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if not valid(newurl) or urllib.parse.urlsplit(newurl).hostname!=urllib.parse.urlsplit(req.full_url).hostname:
   raise ValueError("Original source redirect changed publisher")
  return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch(url):
 if not valid(url):raise ValueError("Government source is not .gov HTTPS")
 req=urllib.request.Request(url,headers={"User-Agent":"Katoptron-original-government-evidence-review/1.0","Accept":"text/html"})
 with urllib.request.build_opener(SameHostOnly()).open(req,timeout=22) as res:
  if res.status!=200:raise ValueError("Original source unavailable")
  result=res.read(MAX_BYTES+1)
  if len(result)>MAX_BYTES:raise ValueError("Original source exceeds bound")
  if res.geturl()!=url:raise ValueError("Original publisher URL changed")
  if b"<html" not in result[:3000].lower():raise ValueError("Original response not HTML")
  return result

def review(row,fetcher=fetch):
 base={"id":row["id"],"agency":row["agency"],"state":row["state"],
       "source_url":row["source_url"],"source_date":row["source_date"],
       "source_statement_verified":False,"sha256":None,"status":"held_original_unavailable"}
 if row["watch_category"]!="historical_research_only" or not valid(row["source_url"]):
  base["status"]="held_source_identity";return base
 try:raw=fetcher(row["source_url"])
 except Exception as e:
  base["status"]="held_fetch_"+type(e).__name__;return base
 if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:return base
 p=PlainText()
 try:p.feed(raw.decode("utf-8","replace"))
 except Exception:base["status"]="held_parse";return base
 body=normalize(" ".join(p.blocks))
 anchor=ANCHORS[row["id"]]
 if normalize(anchor) not in body:
  base["status"]="held_claim_anchor_changed";return base
 base.update(source_statement_verified=True,sha256=hashlib.sha256(raw).hexdigest(),
   status="verified_original_government_html_statement",
   evidence_tier="original_government_published_text_not_independent_operational_verification")
 return base

def run(doc,fetcher=fetch):
 rows=[r for r in doc["sources"] if r["id"] in ANCHORS]
 if len(rows)!=15 or len({r["id"] for r in rows})!=15 or len({r["locality_key"] for r in rows})!=15:
  raise ValueError("Missing/duplicate new government agencies")
 if len({r["state"] for r in rows})<5:raise ValueError("Insufficient new publisher states")
 result=[review(row,fetcher) for row in rows]
 return {"schema_version":1,"as_of":dt.datetime.now(dt.timezone.utc).isoformat(),
  "verified_original_html_statements":sum(x["source_statement_verified"] for x in result),
  "new_agencies_checked":len(result),"states":sorted({x["state"] for x in result}),
  "facts_not_established":["current_camera_uptime","physical_camera_removal_independent",
      "current_access_permissions","signed_agreement_not_in_original"],
  "records":result}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,default=OUT);args=ap.parse_args()
 result=run(json.loads(CATALOG.read_text()))
 out=args.out.resolve()
 if not out.is_relative_to(ROOT):raise ValueError("Verification output outside repo")
 out.parent.mkdir(exist_ok=True,parents=True)
 out.write_text(json.dumps(result,indent=2)+"\n")
 print("NEW_GOV_ORIGINAL_VERIFICATION",json.dumps({
  "verified":result["verified_original_html_statements"],
  "checked":result["new_agencies_checked"],"states":result["states"]}))
 for row in result["records"]:
  print("GOV_ORIGINAL_CHECK",json.dumps({k:row[k] for k in ("id","status","sha256")}))
if __name__=="__main__":main()
