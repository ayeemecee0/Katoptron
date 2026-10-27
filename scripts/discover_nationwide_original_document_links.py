#!/usr/bin/env python3
"""Discover new original-government *document links* behind 51 state source seeds.

Does not fetch candidate documents or publish facts about contracts, Flock
equipment, camera positions, live sharing, plate reads or legal compliance.
Rejects off-host links, raw search logs and identity-ambiguous references.
"""
import argparse,concurrent.futures,datetime as dt,hashlib,html.parser,json,re,urllib.parse
from pathlib import Path

import watch_nationwide_government_originals as gov

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data"/"nationwide-government-jurisdiction-registry.json"
PREVIOUS=ROOT/"data"/"nationwide-original-government-source-receipts.json"
OUTPUT=ROOT/".katoptron-ci"/"nationwide-original-government-document-link-candidates.json"
MAX_LINKS=1100
MAX_PER_SOURCE=24
MAX_TOTAL=450
TOPIC=re.compile(r"(?i)(?:\bflock\b|\balpr\b|license[-\s_]*plate[-\s_]*(?:readers?|recognition)|\blpr\b)")
EXCLUDE=re.compile(r"(?i)(?:raw[-\s_]*(?:alpr[-\s_]*)?(?:plate[-\s_]*)?(?:reads?|search[-\s_]*logs?)|individual[-\s_]*plate|vehicle[-\s_]*(?:movements?|reads?)|live[-\s_]*search[-\s_]*logs?)")
RELEVANT=re.compile(r"(?i)(?:policy|procedures?|contract|agenda|council|minutes?|report|assessment|audit|original|flock|alpr|license[-\s_]*plate|transparency|ordinance|proposal|resolution)")
class Links(html.parser.HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.links=[];self.active=None
 def handle_starttag(self,tag,attrs):
  if tag=="a" and len(self.links)<MAX_LINKS:
   d=dict(attrs);self.active=[d.get("href") or "",[]]
 def handle_data(self,text):
  if self.active is not None and len(self.active[1])<12:self.active[1].append(text[:180])
 def handle_endtag(self,tag):
  if tag=="a" and self.active is not None:
   self.links.append((self.active[0]," ".join(" ".join(self.active[1]).split())[:220]))
   self.active=None
def exact_related(url,source):
 if not isinstance(url,str) or len(url)>1100 or re.search(r"%2e|\\|/\.\.?/",url.split("?")[0],re.I):return None
 try:
  p=urllib.parse.urlsplit(url)
  base=urllib.parse.urlsplit(source["source_url"])
  if (p.scheme!="https" or p.hostname!=base.hostname or p.netloc!=base.netloc or
   p.username or p.password or p.fragment or not p.path.startswith("/") or len(p.query)>200):
   return None
  if EXCLUDE.search(p.path):return None
  # Restrict to an exact original government publishing authority already
  # registered for the state; do not discover cross-domain links without review.
  return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,p.query,""))
 except (TypeError,ValueError):return None
def category(text):
 x=text.casefold()
 if re.search(r"audit|review|assessment|oversight",x):return "unreviewed_original_audit_or_oversight_link"
 if re.search(r"contract|agreement|procure|proposal|purchase|order",x):return "unreviewed_government_contract_or_procurement_link"
 if re.search(r"policy|procedure|retention|privacy|ordinance",x):return "unreviewed_government_policy_link"
 if re.search(r"agenda|minutes|council|resolution|decision",x):return "unreviewed_civic_decision_or_meeting_link"
 return "unreviewed_official_alpr_reference"
def extract(source,raw):
 if source["kind"]!="html" or not isinstance(raw,bytes) or len(raw)>gov.MAX_BYTES_HTML:
  raise ValueError("Original government HTML not bounded")
 p=Links();p.feed(raw.decode("utf8",errors="replace"))
 matched=[]
 for href,label in p.links[:MAX_LINKS]:
  if not href or href.startswith(("#","mailto:","tel:","javascript:","data:")):continue
  # Check the unnormalized relative href before URL joining.
  if re.search(r"(?:^|/)\.\.?/",href.split("?")[0]):continue
  url=exact_related(urllib.parse.urljoin(source["source_url"],href),source)
  if not url or url==source["source_url"]:continue
  topic=urllib.parse.unquote(urllib.parse.urlsplit(url).path).replace("-"," ")+ " "+label
  if not TOPIC.search(topic) or EXCLUDE.search(topic) or not RELEVANT.search(topic):continue
  matched.append({"source_id":source["id"],"state":source["state"],"publisher":source["publisher"],
   "parent_government_source_url":source["source_url"],"candidate_url":url,
   "linked_title":label[:180] or "(unlabeled original government link)",
   "candidate_category":category(topic),
   "publication_status":"unverified_link_needs_individual_original_content_review",
   "flock_installed":False,"camera_coordinates_verified":False,"policy_adopted":False,
   "original_document_fetched":False})
  if len(matched)>=MAX_PER_SOURCE:break
 unique={}
 for r in matched:unique.setdefault(r["candidate_url"],r)
 return list(unique.values())
def scan(originals,baseline,fetcher=gov.fetch,workers=5):
 j,seeds,prior=gov.catalog(originals,json.loads((ROOT/"data"/"national-government-audit-source-portals.json").read_text(encoding="utf8")))
 by_id={r["source_id"]:r for r in baseline.get("receipts",[])}
 if len(by_id)!=len(seeds):raise ValueError("Exact original source baseline missing")
 def check(src):
  b=by_id.get(src["id"])
  if not b or b["source_url"]!=src["source_url"] or b["state"]!=src["state"]:
   raise ValueError("Original government provenance mismatch")
  if src["kind"]!="html":
   return {"source_id":src["id"],"state":src["state"],"status":"original_is_pdf_no_link_extraction","links":[]}
  try:
   raw=fetcher(src)
   if not raw.startswith((b"<!doctype",b"<html",b"<?xml")) and b"<html" not in raw[:1200].lower():
    raise ValueError("Not an original government HTML index")
   links=extract(src,raw)
   return {"source_id":src["id"],"state":src["state"],
    "status":"read_only_official_html_links_examined","source_html_sha256":hashlib.sha256(raw).hexdigest(),
    "links":links}
  except Exception as e:
   return {"source_id":src["id"],"state":src["state"],
    "status":"original_source_unavailable_link_extraction_held","error_type":type(e).__name__,"links":[]}
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  scan_results=list(pool.map(check,seeds))
 all_rows=[];seen=set()
 for r in scan_results:
  for x in r["links"]:
   if x["candidate_url"] not in seen and len(all_rows)<MAX_TOTAL:
    all_rows.append(x);seen.add(x["candidate_url"])
 return {"schema_version":1,"inspected_on":dt.datetime.now(dt.timezone.utc).date().isoformat(),
  "scope":"nationwide_original_government_link_metadata_not_camera_facts",
  "jurisdictions_enrolled":len(j),"original_government_seeds_checked":len(seeds),
  "html_originals_link_scanned":sum(x["status"]=="read_only_official_html_links_examined" for x in scan_results),
  "source_checks":[{k:v for k,v in r.items() if k!="links"} for r in scan_results],
  "candidate_links":all_rows,"candidate_links_truncated":len(all_rows)>=MAX_TOTAL,
  "warning":"A government-linked anchor is NOT independently verified Flock equipment, a contract execution, adopted policy, source document content, a camera location or sharing event."}
def main():
 p=argparse.ArgumentParser();p.add_argument("--workers",type=int,default=5)
 p.add_argument("--out",type=Path,default=OUTPUT);a=p.parse_args()
 if not 1<=a.workers<=8:raise ValueError("Request rate must remain bounded")
 result=scan(json.loads(REGISTRY.read_text(encoding="utf8")),json.loads(PREVIOUS.read_text(encoding="utf8")),workers=a.workers)
 out=a.out.resolve()
 if not out.is_relative_to(ROOT):raise ValueError("Untrusted output path")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
 print("NATIONWIDE_ORIGINAL_DOCUMENT_LINK_DISCOVERY",json.dumps({
  "jurisdictions_enrolled":result["jurisdictions_enrolled"],
  "original_seeds":result["original_government_seeds_checked"],
  "html_sources_examined":result["html_originals_link_scanned"],
  "linked_original_candidates_unverified":len(result["candidate_links"]),
  "source_held":sum(x["status"]=="original_source_unavailable_link_extraction_held" for x in result["source_checks"])
 },sort_keys=True))
 for x in result["source_checks"]:
  print("ORIGINAL_GOV_LINK_DISCOVERY_STATE",json.dumps({"state":x["state"],"source_id":x["source_id"],"status":x["status"]},sort_keys=True))
if __name__=="__main__":main()
