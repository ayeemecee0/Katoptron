#!/usr/bin/env python3
"""Verify dated official city ALPR operating statements (not live surveillance status)."""
import hashlib,html.parser,json,re,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"data"/"verified-city-alpr-operational-statements.json"
KNOWN={
 "moline-il-planned-flock-pause-2026":{
  "url":"https://www.moline.il.us/1955/License-Plate-Readers",
  "agency":"Moline Police Department","date":"2026-09-15",
  "status":"agency_announced_future_deactivation_not_confirmed_completed",
  "effective":None,
  "sha":"7dadb1a974f8021faa4e196ffb8b0a19d6641202bf47089cff41f7dc60fc3048",
  "anchors":["september 15, 2026","fully deactivated within approximately 14 days"]
 },
 "mill-valley-ca-city-reported-disabled-2026":{
  "url":"https://www.cityofmillvalley.gov/m/newsflash/home/detail/1639",
  "agency":"City of Mill Valley","date":"2026-10-19",
  "status":"city_reports_flock_cameras_already_disabled_as_of_dated_statement",
  "effective":"2026-09-09",
  "sha":"6cb358755f107c9e424ff2f352932bf22513ed0b98145d5012e7a5dff8f4c20b",
  "anchors":["october 19, 2026","both the alpr and live-feed cameras have been disabled since september 9, 2026"]
 }
}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Changed official source URL, redirect held")
class SourceText(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,value):self.parts.append(value)
def fetch(url):
 if url not in {r["url"] for r in KNOWN.values()}:raise ValueError("Unapproved city source URL")
 req=urllib.request.Request(url,headers={"Accept":"text/html",
  "User-Agent":"Katoptron-original-city-ALPR-status-verifier/1.0"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Unexpected city page response")
  raw=res.read(1_500_001)
 if not 100<len(raw)<=1_500_000:raise ValueError("City source not bounded")
 return raw
def catalog(data):
 if not isinstance(data,dict) or data.get("schema_version")!=1 or not isinstance(data.get("documents"),list) or len(data["documents"])!=2:
  raise ValueError("Original city statement catalog invalid")
 seen=set()
 for row in data["documents"]:
  ident=row.get("id")
  if ident not in KNOWN or ident in seen:raise ValueError("Duplicate or unknown city statement")
  seen.add(ident);spec=KNOWN[ident]
  for key,value in [
    ("source_url",spec["url"]),("agency",spec["agency"]),
    ("statement_published_on",spec["date"]),("evidence_as_of",spec["date"]),
    ("classification",spec["status"]),("effective_as_of",spec["effective"]),
    ("original_html_sha256_at_review",spec["sha"]),
    ("source_text_anchors",spec["anchors"])]:
   if row.get(key)!=value:raise ValueError("Original agency identity, date, or status boundary changed")
  if not isinstance(row.get("summary"),str) or len(row["summary"])<110:
   raise ValueError("Original source statement missing narrative caveat")
  if ident.startswith("moline") and (("neither" not in row["summary"].casefold() or "confirms" not in row["summary"].casefold()) or "unverified" not in row["evidence_limit"]):
   raise ValueError("Moline may not be upgraded to completed status without an additional source")
  if ident.startswith("mill-valley") and "not a third-party" not in row["evidence_limit"]:
   raise ValueError("City-reported status cannot become independent forensic verification")
 return data["documents"]
def verify(row,raw):
 if not isinstance(raw,bytes) or not 100<len(raw)<=1_500_000:raise ValueError("Invalid original HTML body")
 p=SourceText();p.feed(raw.decode("utf8",errors="replace"))
 text=" ".join(" ".join(p.parts).casefold().split())
 missing=[a for a in row["source_text_anchors"] if a not in text]
 if missing:raise ValueError("Dated official operational status source text changed or removed")
 return {"sha256":hashlib.sha256(raw).hexdigest(),
  "original_html_changed":hashlib.sha256(raw).hexdigest()!=row["original_html_sha256_at_review"]}
def main():
 for row in catalog(json.loads(PATH.read_text(encoding="utf8"))):
  result=verify(row,fetch(row["source_url"]))
  print("ORIGINAL_CITY_OPERATIONAL_STATEMENT_RECHECK",row["agency"],
   "CLASSIFICATION",row["classification"],
   "PUB_DATE",row["statement_published_on"],
   "SHA256",result["sha256"],
   "HTML_CHANGED",result["original_html_changed"])
 print("MOLINE INTENDED DEACTIVATION NOT PROMOTED; MILL VALLEY CITY-REPORTED DISABLEMENT IS HISTORICAL SELF-REPORT")
if __name__=="__main__":
 try:main()
 except Exception as exc:
  raise SystemExit("Original city operational source recheck held: "+type(exc).__name__+" "+str(exc)[:120]) from None
