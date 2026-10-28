#!/usr/bin/env python3
"""Monitor two verified government policy-publication authorities, read-only.

A source listing disappearing or a PDF link changing creates a REVIEW lead,
never an automatically adopted policy, government decision, or notification.
The source ledger remains frozen until independently re-reviewed.
"""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data"/"verified-policy-adoption-status-2026-10-27.json"
MAX_BYTES=1_500_000
class TextAndLinks(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.text=[]
  self.links=[]
  self.anchor=None
 def handle_starttag(self,tag,attrs):
  if tag=="a":
   self.anchor=dict(attrs).get("href","")
 def handle_endtag(self,tag):
  if tag=="a":self.anchor=None
 def handle_data(self,s):
  x=" ".join(s.split())
  if x:self.text.append(x)
  if self.anchor and x:self.links.append((self.anchor,x))
def parse(source):
 if not isinstance(source,str) or len(source)>MAX_BYTES:
  raise ValueError("Government source exceeded bounded HTML size")
 p=TextAndLinks();p.feed(source)
 return " ".join(p.text),p.links
def review_green_bay(source):
 text,links=parse(source)
 seen=re.search(r"Policy 424 Automated License Plate Readers \(ALPR\) May 2026",text,re.I)
 proposed=re.search(r"DRAFTED REVISION\s*-\s*Policy 424 Automated License Plate Readers \(ALPR\) September 2026",text,re.I)
 label_may=any("May 2026" in label and "Policy 424" in label and
  re.search(r"/DocumentCenter/View/18791(?:/|$)",href) for href,label in links)
 label_draft=any("DRAFTED" in label.upper() and "Policy 424" in label and
  re.search(r"/DocumentCenter/View/19136(?:/|$)",href) for href,label in links)
 candidates=sorted({href for href,label in links if
  "Policy 424" in label and "/DocumentCenter/View/" in href
  and not any("/DocumentCenter/View/"+id in href for id in ("18791","19136"))})[:20]
 good=bool(seen and proposed and label_may and label_draft)
 return {
  "source_status":"confirmed_original_index_still_marks_draft" if good and not candidates
    else "needs_review_index_changed_or_new_policy_link",
  "adoption_verified":False,
  "page_contains_expected_may_and_draft_labels":good,
  "new_original_policy_candidates_needing_review":candidates,
  "note":"Even a matching draft listing cannot exclude an unlisted internal adoption or prove system retention."
 }
def review_apache_junction(source):
 text,links=parse(source)
 adopted=re.search(r"(?:have been adopted|have\s+been\s+adopted)",text,re.I)
 at=re.search(r"Ordinance No\. 1579",text,re.I)
 first=at.start() if at else -1
 section=text[first:first+450] if first>=0 else ""
 approved=bool(adopted and first>adopted.start() and
  re.search(r"Automated\s+License\s+Plate\s+Readers",section,re.I)
  and re.search(r"10/06/2026",section))
 return {
  "source_status":"confirmed_city_clerk_adoption_register_entry_present" if approved
    else "needs_review_city_clerk_entry_changed_or_archived",
  "adoption_verified_from_registered_source":approved,
  "effective_date_verified":False,
  "note":"Original adopted action remains source-dated; a later missing city posting does not revoke it. City clerk leaves effective date blank."
 }
def fetch_exact(url):
 req=urllib.request.Request(url,headers={
  "User-Agent":"Katoptron-original-policy-source-review/1.0 (public evidence only)",
  "Accept":"text/html"})
 with urllib.request.urlopen(req,timeout=24) as res:
  if res.status!=200:raise ValueError("Government source not HTTP 200")
  from urllib.parse import urlparse
  original=urlparse(url);destination=urlparse(res.geturl())
  if destination.scheme!="https" or destination.hostname!=original.hostname:
   raise ValueError("Original government publisher redirect not validated")
  payload=res.read(MAX_BYTES+1)
  if len(payload)>MAX_BYTES:raise ValueError("Government HTML exceeded size cap")
  return payload.decode("utf8",errors="replace")
def run(ledger,fetch=fetch_exact,clock=None):
 now=clock or dt.datetime.now(dt.timezone.utc)
 if ledger.get("reviewed_on")!="2026-10-27":
  raise ValueError("Source review baseline changed; deliberate re-review required")
 records={r["id"]:r for r in ledger.get("records",[])}
 expected={
  "green-bay-wi-policy-424-draft-still-listed-2026-10-27":review_green_bay,
  "apache-junction-az-ordinance-1579-adopted-2026-10-06":review_apache_junction
 }
 if set(records)!=set(expected):raise ValueError("Monitored government publisher identities changed")
 responses=[]
 for ident,check in expected.items():
  row=records[ident]
  try:
   response=check(fetch(row["source_url"]))
  except Exception as exc:
   response={"source_status":"needs_review_source_unreachable",
    "reason":type(exc).__name__+"; source was not confirmed during this check",
    "adoption_verified":False}
  responses.append({"id":ident,"jurisdiction":row["jurisdiction"],
   "baseline_status":row["status"],
   "source_url":row["source_url"],
   "source_rechecked_at":now.isoformat(),
   **response})
 return {"schema_version":1,"reviewed_baseline":"2026-10-27",
  "checked_at":now.isoformat(),
  "scope":"original_government_HTML_source_freshness_only_never_automatic_policy_adoption",
  "sources":responses,
  "needs_review":sum(x["source_status"].startswith("needs_review") for x in responses),
  "new_enacted_policy_records_auto_published":0}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--output",type=Path,default=ROOT/"policy-adoption-monitor.json")
 args=p.parse_args()
 ledger=json.loads(LEDGER.read_text(encoding="utf8"))
 result=run(ledger)
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
 print("OFFICIAL_POLICY_ADOPTION_ORIGINAL_SOURCE_RECHECK",json.dumps({
  "sources":len(result["sources"]),
  "needs_review":result["needs_review"],
  "auto_enacted_policy_claims":0
 },sort_keys=True))
 for item in result["sources"]:
  print("POLICY_SOURCE_RECHECK",item["id"],item["source_status"])
if __name__=="__main__":main()
