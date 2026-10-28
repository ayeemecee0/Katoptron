#!/usr/bin/env python3
"""FBI-derived ORI agency research directory; source is CC0 secondary mirror.

Agency list inclusion does NOT verify active police operations, Flock vendor,
ALPR programs, source-effective policies, or current organization status.
No geographic coordinates are imported or published as camera locations.
"""
import argparse,csv,datetime as dt,hashlib,io,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL="https://iropo.org/data/agencies.csv"
OUT=ROOT/".katoptron-ci"/"fbi-derived-ori-agency-directory-research.json"
STATES="AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split()
MAX_BYTES=5_000_000
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError("Secondary agency directory publisher redirected")
def fetch():
 req=urllib.request.Request(URL,headers={
  "User-Agent":"Katoptron-public-FBI-derived-agency-directory-research/1.0",
  "Accept":"text/csv,text/plain"})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as res:
  if res.status!=200 or res.geturl()!=URL:raise ValueError("Agency directory original publisher changed")
  data=res.read(MAX_BYTES+1)
 if not 100_000<len(data)<=MAX_BYTES:raise ValueError("Secondary agency directory unusually small or oversized")
 return data
def normalized(x):
 return re.sub("[^a-z0-9]","",str(x or "").lower())
def choose(names,*options):
 index={normalized(x):x for x in names if isinstance(x,str)}
 for option in options:
  if normalized(option) in index:return index[normalized(option)]
 return None
def parse(data,require_count=True):
 if not isinstance(data,bytes) or len(data)>MAX_BYTES:raise ValueError("Agency mirror byte limit")
 try:content=data.decode("utf-8-sig")
 except UnicodeError as e:raise ValueError("Agency directory decoding changed") from e
 rd=csv.DictReader(io.StringIO(content,newline=""))
 headers=rd.fieldnames or []
 ori=choose(headers,"ori","agency_ori","ori_code","oricd")
 state=choose(headers,"state_abbr","state","state_code")
 name=choose(headers,"agency_name","name","agency")
 agency_type=choose(headers,"agency_type","type")
 county=choose(headers,"county","counties","county_name")
 if not ori or not state or not name:
  raise ValueError("FBI-derived ORI, state, agency schema changed: "+str(headers[:12]))
 out=[];seen=set()
 for line,row in enumerate(rd,2):
  if not row or None in row:raise ValueError("Broken ORI directory line "+str(line))
  st=(row.get(state) or "").strip().upper()
  if st not in STATES:continue  # The scope is specifically 50 US states plus DC.
  code=(row.get(ori) or "").strip().upper()
  label=" ".join((row.get(name) or "").split())
  if (not re.fullmatch(r"[A-Z0-9]{7,12}",code) or not 3<=len(label)<=180 or
      any(ord(ch)<32 for ch in label)):
   raise ValueError("Unusable FBI-derived ORI / agency name at line "+str(line))
  if code in seen:raise ValueError("Duplicate ORI in secondary FBI directory")
  seen.add(code)
  out.append({
   "ori":code,"state":st,"name":label,
   "agency_type":" ".join((row.get(agency_type) or "").split())[:110] if agency_type else "",
   "county_text":" ".join((row.get(county) or "").split())[:180] if county else "",
   "evidence_tier":"secondary_FBI_CDE_derived_ORI_roster_not_live_Flock_or_agency_confirmation",
   "original_federal_directory_directly_fetched":False,
   "current_law_enforcement_operation_verified":False,
   "flock_vendor_verified":False,"alpr_program_verified":False,
   "policy_adoption_verified":False,"camera_coordinates_added":0
  })
 if require_count and not 15000<=len(out)<=25000:raise ValueError("FBI directory population unexpectedly changed")
 if require_count and {x["state"] for x in out}!=set(STATES):
  raise ValueError("FBI secondary agency directory state coverage incomplete")
 return out
def build(fetcher=fetch,strict=True):
 content=fetcher();rows=parse(content,require_count=strict)
 counts={s:sum(x["state"]==s for x in rows) for s in STATES}
 return {
  "schema_version":1,"retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(),
  "secondary_source_url":URL,"original_source_reference":"FBI Crime Data Explorer /agency/byStateAbbr/{state}",
  "secondary_publisher":"IROPO CC0 agencies.csv; FBI-derived ORI data, not directly fetched original federal agency list",
  "original_csv_sha256":hashlib.sha256(content).hexdigest(),
  "scope":"all_50_us_states_DC_2026_secondary_FBI_CDE_derived_agency_directory",
  "research_agency_count":len(rows),"states_count":51,
  "state_counts":counts,"agency_rows":rows,
  "fbi_agency_currently_operating_verified":0,
  "flock_deployments_verified":0,"adopted_policies_verified":0,
  "individual_camera_coordinates_published":0,
  "warning":"FBI-derived agencies and ORI identifiers form a secondary research lead roster, not a currently operating government police agency census. Never identify Flock programs, policies, sharing links, or camera equipment by geography or agency-name resemblance."
 }
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,default=OUT)
 opts=parser.parse_args();dest=opts.out.resolve()
 if not dest.is_relative_to(ROOT):raise ValueError("Unsafe directory output")
 result=build();dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
 print("FBI_DERIVED_ORI_AGENCY_DIRECTORY",json.dumps({
  "states":result["states_count"],"research_leads":result["research_agency_count"],
  "sha256":result["original_csv_sha256"],"source":URL,
  "verified_flock_systems":0,"verified_current_agencies":0},sort_keys=True))
 for code,n in result["state_counts"].items():
  print("ORI_STATE_RESEARCH_AGENCY_COUNT",json.dumps({"state":code,"count":n},sort_keys=True))
if __name__=="__main__":main()
