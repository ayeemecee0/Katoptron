#!/usr/bin/env python3
"""Build an all-state official US Census 2026 geographic *research* universe.

Uses bounded official .gov Gazetteer archives for counties, Census places and
county subdivisions. A Census geography is NOT necessarily an incorporated
local government, an operating police agency, a known ALPR user or a camera
location. This code never matches government names to Flock records.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/".katoptron-ci"/"2026-us-census-government-geography-research-universe.json"
BASE="https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2026_Gazetteer/"
ARCHIVES={
 "county":"2026_Gaz_counties_national.zip",
 "place":"2026_Gaz_place_national.zip",
 "county_subdivision":"2026_Gaz_cousubs_national.zip"
}
STATES="AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split()
MIN_COUNTS={"county":2900,"place":24000,"county_subdivision":25000}
MAX_COUNTS={"county":3600,"place":42000,"county_subdivision":45000}
ARCHIVE_LIMIT=5_000_000
CONTENT_LIMIT=30_000_000
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):
  raise ValueError("Official Census publisher redirect held for independent review")
def url_for(name):
 if name not in ARCHIVES:raise ValueError("Unsupported Census archive type")
 return BASE+ARCHIVES[name]
def fetch(name):
 url=url_for(name)
 req=urllib.request.Request(url,headers={
  "Accept":"application/zip","User-Agent":"Katoptron-Census-locality-research/1.0"})
 with urllib.request.build_opener(DenyRedirect()).open(req,timeout=28) as res:
  if res.status!=200 or res.geturl()!=url:raise ValueError("Government archive publisher changed")
  payload=res.read(ARCHIVE_LIMIT+1)
 if not 100<len(payload)<=ARCHIVE_LIMIT:raise ValueError("Government archive unavailable or too large")
 return payload
def parse_archive(kind,data):
 if kind not in ARCHIVES or not isinstance(data,bytes) or not 100<len(data)<=ARCHIVE_LIMIT:
  raise ValueError("Government archive input not valid or bounded")
 if not zipfile.is_zipfile(io.BytesIO(data)):raise ValueError("Official government data is not a ZIP")
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  members=[i for i in z.infolist() if not i.is_dir()]
  if (len(members)!=1 or members[0].file_size>CONTENT_LIMIT or
      not members[0].filename.endswith(".txt") or
      "/" in members[0].filename or "\\" in members[0].filename):
   raise ValueError("Unexpected Census archive layout")
  payload=z.read(members[0],pwd=None)
  if len(payload)>CONTENT_LIMIT:raise ValueError("Expanded government archive exceeded size cap")
 try:decoded=payload.decode("utf-8-sig")
 except UnicodeDecodeError as exc:raise ValueError("Census text decoding changed") from exc
 header=decoded.splitlines()[0].lstrip("\ufeff")
 delim="|" if "|" in header else "\t" if "\t" in header else None
 if delim is None:raise ValueError("Census original delimited header unavailable")
 reader=csv.DictReader(io.StringIO(decoded),delimiter=delim)
 if not reader.fieldnames or not {"USPS","GEOID","NAME"}.issubset(
  {str(x).strip() for x in reader.fieldnames}):
  raise ValueError("Government original Census fields changed")
 out=[];seen=set()
 for row in reader:
  if not isinstance(row,dict):raise ValueError("Malformed Census government row")
  entry={k.strip():str(v or "").strip() for k,v in row.items() if k is not None}
  state=entry.get("USPS","").upper()
  if state not in STATES:continue  # Puerto Rico not in the requested 50+DC scope.
  geoid=entry.get("GEOID","")
  if not re.fullmatch(r"\d{5,12}",geoid):
   raise ValueError("Missing census geographic ID for "+kind)
  name=entry.get("NAME","")
  if not 1<=len(name)<=180 or any(ord(c)<32 for c in name):
   raise ValueError("Invalid named Census geographic area")
  key=kind+":"+state+":"+geoid
  if key in seen:raise ValueError("Duplicated original Census GEOID")
  seen.add(key)
  out.append({
   "id":key,"state":state,"geo_type":kind,"census_geoid":geoid,
   "name":name,
   "lsad":entry.get("LSAD","")[:6],
   "funcstat":entry.get("FUNCSTAT","")[:6],
   "census_2026_geography":True,
   "known_law_enforcement_agency":False,
   "flock_vendor_verified":False,
   "alpr_policy_reviewed":False,
   "camera_locations_inferred":0
  })
 return out
def build(fetcher=fetch,strict_counts=True):
 source_receipts=[]
 all_rows=[]
 for kind in ARCHIVES:
  payload=fetcher(kind)
  records=parse_archive(kind,payload)
  if strict_counts and not MIN_COUNTS[kind]<=len(records)<=MAX_COUNTS[kind]:
   raise ValueError("Census geography count or boundary changed: "+kind+" "+str(len(records)))
  source_receipts.append({
   "geo_type":kind,"url":url_for(kind),
   "original_zip_sha256":hashlib.sha256(payload).hexdigest(),
   "rows_50_states_dc":len(records),"max_bytes":ARCHIVE_LIMIT,
   "source":"U.S. Census Bureau 2026 Gazetteer, federal original"})
  all_rows.extend(records)
 if len({r["id"] for r in all_rows})!=len(all_rows):
  raise ValueError("Cross-category geographic identity collision")
 county_states={r["state"] for r in all_rows if r["geo_type"]=="county"}
 if strict_counts and county_states!=set(STATES):
  raise ValueError("Census 2026 geography excludes a U.S. state or DC")
 by_state=[{
  "state":s,
  "counties":sum(r["state"]==s and r["geo_type"]=="county" for r in all_rows),
  "places_including_unincorporated_cdps":sum(r["state"]==s and r["geo_type"]=="place" for r in all_rows),
  "county_subdivisions_not_all_governments":sum(r["state"]==s and r["geo_type"]=="county_subdivision" for r in all_rows),
  "police_agencies_verified":0,"flock_programs_verified":0,
  "policy_adoptions_verified":0,"municipal_government_census_complete":False
 } for s in STATES]
 return {
  "schema_version":1,"source_year":2026,
  "generated_at":dt.datetime.now(dt.timezone.utc).isoformat(),
  "scope":"census_50_states_dc_place_county_county_subdivision_geography_not_law_enforcement_roster",
  "source_receipts":source_receipts,
  "states":51,"total_geographic_entities":len(all_rows),
  "total_verified_flock_agencies":0,
  "total_verified_policy_adoptions":0,
  "complete_municipal_agency_census":False,
  "warning":"Census places include census-designated places; county subdivisions include statistical rather than governmental areas. This is not a census of police agencies, Flock deployments or adopted ALPR policies. No matched jurisdiction name is treated as an agency or verified operational entity.",
  "by_state":by_state,
  "geographic_research_queue":all_rows
 }
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,default=OUT)
 args=p.parse_args()
 dest=args.out.resolve()
 if not dest.is_relative_to(ROOT):raise ValueError("Unsafe Census research artifact path")
 record=build()
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
 print("2026_OFFICIAL_CENSUS_GEOGRAPHIC_RESEARCH_QUEUE",json.dumps({
  "states":record["states"],
  "source_rows":{x["geo_type"]:x["rows_50_states_dc"] for x in record["source_receipts"]},
  "total_geographies":record["total_geographic_entities"],
  "flock_agencies_verified":0,"census_as_law_enforcement_roster":False
 },sort_keys=True))
 for r in record["by_state"]:
  print("CENSUS_STATE_RESEARCH_GEO_COUNTS",json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
