#!/usr/bin/env python3
"""Preserve public government original bytes across runs for real source-version review.

No approval, emails or database writes. Old and new bytes must match independent
SHA-256 receipts. Missing prior bytes remain explicit holds, not false differences.
"""
import argparse,difflib,hashlib,io,json,re,shutil,datetime as dt
from pathlib import Path
from html.parser import HTMLParser
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/".katoptron-ci/nationwide-original-current"
BASELINE=ROOT/".katoptron-ci/nationwide-original-baselines"
SNAPSHOT=ROOT/".katoptron-ci/nationwide-monitor-snapshot.json"
OUT=ROOT/".katoptron-ci/nationwide-before-after-document-candidates.json"
VALID_ID=re.compile(r"^[a-z0-9_-]{7,120}$")
SHA=re.compile(r"^[a-f0-9]{64}$")

def pair_id(source_id,before_sha,after_sha):
 """Stable identity across outages or a source reverting to prior bytes."""
 return hashlib.sha256((source_id+"\x00"+before_sha+"\x00"+after_sha).encode("utf8")).hexdigest()

class Plain(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.ignore=0
 def handle_starttag(self,tag,attrs):
  if tag in ("script","style","noscript"):self.ignore+=1
 def handle_endtag(self,tag):
  if tag in ("script","style","noscript") and self.ignore:self.ignore-=1
 def handle_data(self,raw):
  if not self.ignore:self.parts.append(raw)

def paragraphs(raw,kind):
 if kind=="html":
  p=Plain();p.feed(raw.decode("utf8",errors="replace"))
  t=" ".join(" ".join(p.parts).split())[:600000]
  return [(1,t)]
 pdf=PdfReader(io.BytesIO(raw),strict=True)
 if pdf.is_encrypted or len(pdf.pages)>200:raise ValueError("Unsupported restricted PDF")
 return [(i+1," ".join((p.extract_text() or "").split())[:40000]) for i,p in enumerate(pdf.pages)]

def substantive(before,after,kind):
 # Machine suggestions are NOT editorial decisions; include a bounded page candidate.
 a=paragraphs(before,kind);b=paragraphs(after,kind);out=[]
 for i in range(min(len(a),len(b),200)):
  earlier,later=a[i][1],b[i][1]
  # Filter generated site timing markers. Raw checksums can differ even if the government-authored text does not.
  def dynamic(t):
   t=re.sub(r"\bLoading Articles\s+\d+(?:\.\d+)?", "Loading Articles [runtime]",t)
   if kind=="html":
    # Explicit chrome-only transforms for confirmed dynamic government-site elements.
    t=re.sub(r"(West Virginia Code \| §17C-6-7A )\w+, \w+ \d{1,2}, \d{4}",r"\1[site clock]",t)
    t=re.sub(r"\b\d{2,3}°F(?= X Hot Key:)", "[site weather]",t)
   return t
  if dynamic(earlier)==dynamic(later):continue
  opcodes=difflib.SequenceMatcher(None,earlier,later,autojunk=True).get_opcodes()
  candidates=[(x,y,z,w) for tag,x,y,z,w in opcodes if tag!="equal"]
  if not candidates:continue
  x,y,z,w=candidates[0]
  out.append({"page":i+1,
   "before_excerpt":earlier[max(0,x-140):min(len(earlier),max(y,x+1)+180)],
   "after_excerpt":later[max(0,z-140):min(len(later),max(w,z+1)+180)],
   "machine_text_difference_only":True,"human_review_required":True,
   "citation_kind":"pdf_page" if kind=="pdf" else "unpaginated_html_text_not_page_citation"})
  if len(out)>=12:break
 return out

def reconcile(snapshot,current= CURRENT,baseline=BASELINE):
 rows=snapshot.get("receipts",[])
 if (snapshot.get("schema_version")!=2 or not isinstance(rows,list) or
    len(rows)<100 or len({x.get("source_id") for x in rows})!=len(rows)):
  raise ValueError("Complete national original-fingerprint snapshot required")
 baseline.mkdir(parents=True,exist_ok=True)
 manifest_path=baseline/"manifest.json"
 old=json.loads(manifest_path.read_text()) if manifest_path.exists() else {"sources":{}}
 if old.get("schema_version",1)!=1 or not isinstance(old.get("sources"),dict):
  raise ValueError("Untrusted source-byte archive manifest")
 seen=old.setdefault("seen_pairs",{})
 if not isinstance(seen,dict):raise ValueError("Invalid archived original version-pair ledger")
 out=[];saved=0;new_pairs=0;version_pairs_archived=0
 for row in rows:
  sid=row.get("source_id");kind=row.get("kind")
  if not VALID_ID.fullmatch(str(sid)) or kind not in ("html","pdf"):
   raise ValueError("Unsafe original identity")
  archive=baseline/(sid+"."+kind)
  observed=current/(sid+"."+kind)
  prior=old["sources"].get(sid)
  new_sha=row.get("current_observation_sha256")
  previous_sha=row.get("previous_usable_sha256")
  if prior:
   if prior.get("source_url") and prior["source_url"]!=row.get("source_url"):
    raise ValueError("Original publisher identity changed without reviewed migration")
   if archive.is_file() and (prior.get("kind")!=kind or
       not SHA.fullmatch(str(prior.get("sha256"))) or
       hashlib.sha256(archive.read_bytes()).hexdigest()!=prior["sha256"]):
    raise ValueError("Previously authenticated original bytes corrupted")
  if row.get("status","").startswith("original_"):
   if (not SHA.fullmatch(str(new_sha)) or not observed.is_file() or
      hashlib.sha256(observed.read_bytes()).hexdigest()!=new_sha):
    raise ValueError("Source bytes failed receipt-hash verification")
  if row.get("change")=="source_bytes_changed_review_required":
   candidate={"source_id":sid,"state":row.get("state"),"government_source_url":row.get("source_url"),
     "before_sha256":previous_sha,"after_sha256":new_sha,
     "editorial_status":"held_before_and_after_page_review",
     "verified_documentary_policy_change":False,"automatic_watch_event_published":False,
     "machine_page_candidates":[]}
   if (prior and prior.get("sha256")==previous_sha and
       prior.get("kind")==kind and archive.is_file() and
       hashlib.sha256(archive.read_bytes()).hexdigest()==previous_sha):
    try:
     candidate["machine_page_candidates"]=substantive(archive.read_bytes(),observed.read_bytes(),kind)
     candidate["editorial_status"]=("machine_text_difference_requires_editorial_check" if candidate["machine_page_candidates"] else "authenticated_byte_pair_no_substantive_text_difference_identified")
    except Exception:
     candidate["editorial_status"]="held_unreadable_original_pair"
   else:candidate["editorial_status"]="held_missing_authentic_prior_document_bytes"
   if candidate["editorial_status"] in (
       "machine_text_difference_requires_editorial_check",
       "authenticated_byte_pair_no_substantive_text_difference_identified"):
    identity=pair_id(sid,previous_sha,new_sha)
    candidate["document_version_pair_id"]=identity
    candidate["newly_observed_fingerprint_pair"]=identity not in seen
    if identity not in seen:
     seen[identity]={"source_id":sid,"before_sha256":previous_sha,
      "after_sha256":new_sha,"first_observed_on":snapshot["observed_on"]}
     new_pairs+=1
    # Keep publisher bytes under immutable content-addressed filenames.
    # Byte preservation does not establish enacted policy or contract execution.
    version_dir=baseline/"versions"/sid
    version_dir.mkdir(parents=True,exist_ok=True)
    for fingerprint,raw in ((previous_sha,archive.read_bytes()),(new_sha,observed.read_bytes())):
     destination=version_dir/(fingerprint+"."+kind)
     if destination.is_file():
      if hashlib.sha256(destination.read_bytes()).hexdigest()!=fingerprint:
       raise ValueError("Content-addressed government original archive corrupted")
     else:destination.write_bytes(raw)
    version_pairs_archived+=1
   out.append(candidate)
  if row.get("status","").startswith("original_"):
   shutil.copyfile(observed,archive)
   old["sources"][sid]={"kind":kind,"sha256":new_sha,"observed_on":snapshot["observed_on"],
    "source_url":row.get("source_url"),"retrieved_url":row.get("retrieved_url")}
   saved+=1
 old["schema_version"]=1
 manifest_path.write_text(json.dumps(old,indent=2)+"\n",encoding="utf8")
 return {"schema_version":1,"observed_on":snapshot.get("observed_on"),
   "source_bytes_verified_and_archived":saved,
   "source_hash_changes_checked":len(out),
   "authenticated_before_after_original_byte_pairs":sum(x["editorial_status"] in ("machine_text_difference_requires_editorial_check","authenticated_byte_pair_no_substantive_text_difference_identified") for x in out),
   "machine_differences_for_human_review":sum(x["editorial_status"]=="machine_text_difference_requires_editorial_check" for x in out),
   "new_authentic_document_version_pairs":new_pairs,
   "previously_seen_document_pairs_not_new_findings":sum(x.get("newly_observed_fingerprint_pair") is False for x in out),
   "immutable_version_pairs_archived":version_pairs_archived,
   "original_version_pairs":out,
   "automatic_editorial_approvals":0,"automatic_watch_emails":0,
   "caveat":"The diff engine preserves original publisher bytes and page hints. No machine diff alone establishes a contract or policy change."}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--current",type=Path,default=CURRENT)
 p.add_argument("--baseline",type=Path,default=BASELINE)
 p.add_argument("--snapshot",type=Path,default=SNAPSHOT)
 p.add_argument("--out",type=Path,default=OUT)
 a=p.parse_args()
 for directory in (a.current,a.baseline,a.out.parent):
  if not directory.resolve().is_relative_to(ROOT):raise ValueError("Path outside safe repository runtime")
 result=reconcile(json.loads(a.snapshot.read_text(encoding="utf8")),a.current,a.baseline)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
 print("ORIGINAL_BYTES_ARCHIVAL",json.dumps({k:result[k] for k in (
  "source_bytes_verified_and_archived","source_hash_changes_checked","authenticated_before_after_original_byte_pairs","machine_differences_for_human_review",
  "automatic_editorial_approvals")},sort_keys=True))
if __name__=="__main__":main()
