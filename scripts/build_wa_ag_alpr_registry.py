#!/usr/bin/env python3
"""Extract public, unverified-by-AGO agency ALPR self-certifications from the
Washington Attorney General's official 2026 registration page. The original
HTML is hashed. No device manufacturer, position, live status or raw plate
data inferred. Third-party policy URLs are *only* displayed if the AGO page
itself actually links them, and never auto-fetched.
"""
import argparse,datetime as dt,hashlib,ipaddress,json,re,urllib.parse
from pathlib import Path
from inspect_wa_ag_alpr_registry import Rows
from scan_national_government_audit_sources import catalog,fetch,PORTALS,ROOT

OUT=ROOT/".katoptron-ci"/"wa-alpr-public-registration-snapshot.json"
AGO="https://www.atg.wa.gov/ALPR"
def safe_policy(url):
 if not isinstance(url,str) or not 8<len(url)<=950:return None
 try:
  u=urllib.parse.urlsplit(url)
  if u.scheme!='https' or u.netloc!=u.hostname or not u.hostname or u.username or u.password or u.fragment:return None
  host=u.hostname.lower()
  if host in {'localhost','127.0.0.1','0.0.0.0'} or host.endswith(('.local','.internal','.test','.example')):return None
  try:ipaddress.ip_address(host);return None
  except ValueError:pass
  if re.search(r'\\|\.\./|/%2e',u.path,re.I):return None
  if u.query and len(u.query)>250:return None
  return url
 except (ValueError,TypeError):return None
def normalize_date(raw):
 if not isinstance(raw,str):return None
 t=re.sub(r'\s+',' ',raw.strip())
 t=re.sub(r',\s*',', ',t)
 for fmt in ('%B %d, %Y','%b %d, %Y'):
  try:return dt.datetime.strptime(t,fmt).date().isoformat()
  except ValueError:pass
 return None

def convert(html,as_of=None):
 if not isinstance(html,bytes) or not 300<=len(html)<=1_600_000:
  raise ValueError("Unbounded original AGO page")
 rows=Rows();rows.feed(html.decode('utf-8',errors='replace'))
 if rows.tables<1 or not 20<=len(rows.rows)<=500:raise ValueError("AGO agency registration table missing")
 head=[' '.join(x['text'].lower().split()) for x in rows.rows[0]]
 if head[:3]!=['agency name','submitted date','agency policy']:
  raise ValueError("AGO original registration table headings changed")
 seen=set();registrations=[]
 for n,cols in enumerate(rows.rows[1:],1):
  if len(cols)<3:raise ValueError("Incomplete original AGO entry")
  agency=' '.join(cols[0]['text'].split())
  if not 4<=len(agency)<=160 or agency.lower() in seen:raise ValueError("Duplicate or invalid agency name in AGO original")
  seen.add(agency.lower())
  date_text=' '.join(cols[1]['text'].split())
  if len(date_text)>80:raise ValueError("Unbounded submission date")
  raw_policy_links=cols[2].get('links',[])
  if len(raw_policy_links)>3:raise ValueError("Too many public policy links on original agency row")
  policies=[]
  for url in raw_policy_links:
   u=safe_policy(urllib.parse.urljoin(AGO,url))
   if u and u not in policies:policies.append(u)
  note=' '.join(cols[2]['text'].split())
  if len(note)>180:raise ValueError("Unbounded original AGO policy link label")
  registrations.append({'id':hashlib.sha256(agency.lower().encode()).hexdigest()[:20],
     'agency_name':agency,'submitted_on':normalize_date(date_text),
     'submitted_date_as_published':date_text,'policy_link_label':note,
     'policy_links_from_official_ago_page':policies,
     'registry_status':'agency_self_certification_listed_by_state_AG_not_independently_verified'})
 if as_of is None:as_of=dt.datetime.now(dt.timezone.utc).date().isoformat()
 return {'schema_version':1,'source_url':AGO,'captured_on':as_of,
   'source_sha256':hashlib.sha256(html).hexdigest(),
   'provenance':'Washington Attorney General public agency ALPR self-certification registration table',
   'warning':'The Washington Attorney General states it has not independently verified each agency head certification. A registration is NOT proof of Flock vendor, operational camera count, camera placement, current compliance or approved data sharing.',
   'registrations':registrations,
   'camera_points_published':0,'flock_vendor_assertions_published':0,
   'sharing_network_edges_published':0}
def compare_published(fresh,previous):
 """Summary of original agency self-certification changes, not manufacturer or
 location deltas. A deleted/renamed index row must not mean a system shut down.
 """
 curr={r['id']:r for r in fresh['registrations']}
 old={r['id']:r for r in previous.get('registrations',[])}
 added=sorted(curr.keys()-old.keys())
 missing=sorted(old.keys()-curr.keys())
 changed=sorted(k for k in curr.keys()&old.keys() if (
  curr[k]['submitted_on']!=old[k]['submitted_on'] or
  curr[k]['policy_links_from_official_ago_page']!=old[k]['policy_links_from_official_ago_page'] or
  curr[k]['policy_link_label']!=old[k]['policy_link_label']))
 return {'registered_name_entries_added_to_original_index':len(added),
  'registered_name_entries_no_longer_listed_unknown_reason':len(missing),
  'existing_original_policy_or_date_metadata_changed':len(changed),
  'new_agency_names':[curr[k]['agency_name'] for k in added[:20]],
  'omitted_agency_names_needs_followup':[old[k]['agency_name'] for k in missing[:20]],
  'changed_agency_names':[curr[k]['agency_name'] for k in changed[:20]],
  'verified_flock_camera_additions':0,'confirmed_shutdowns':0}

def run():
 src=next(s for s in catalog(json.loads(PORTALS.read_text(encoding='utf-8')))
          if s['id']=='wa-ag-public-alpr-agency-registrations')
 body=fetch(src)
 return convert(body)
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--out',type=Path,default=OUT)
 parser.add_argument('--print-snapshot-json',action='store_true')
 opts=parser.parse_args()
 d=run();path=opts.out.resolve()
 if not path.is_relative_to(ROOT):raise ValueError("Output must be bounded to working repository CI tree")
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
 count=len(d['registrations'])
 print("WA_STATE_AG_ORIGINAL_REGISTRATIONS",count,"POLICIES_LINKED",sum(bool(r['policy_links_from_official_ago_page']) for r in d['registrations']),
   "UNKNOWN_SUBMISSION_DATES",sum(r['submitted_on'] is None for r in d['registrations']),
   "SOURCE_SHA256",d['source_sha256'])
 print("WA_AG_WARNING_AGENCY_CERTIFICATIONS_NOT_INDEPENDENTLY_VERIFIED")
 published=ROOT/"data"/"wa-original-agency-alpr-registrations.json"
 if published.exists():
  prev=json.loads(published.read_text(encoding='utf-8'))
  if prev.get('source_url')!="https://www.atg.wa.gov/ALPR":raise ValueError("Published registry original source identity changed")
  changes=compare_published(d,prev)
  print("WA_AG_ORIGINAL_PUBLISHED_SNAPSHOT_DIFF",json.dumps(changes,sort_keys=True,ensure_ascii=False))

 if opts.print_snapshot_json:print('WA_AG_OFFICIAL_SNAPSHOT_JSON '+json.dumps(d,separators=(',',':'),ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception as e:raise SystemExit('WA AGO original held: '+type(e).__name__+' '+str(e)[:120]) from None
