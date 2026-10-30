#!/usr/bin/env python3
"""GitHub OIDC -> private immutable Supabase evidence archive, with cold-cache restore.

No service key is ever sent to GitHub or stored in the repository. GitHub's
short-lived, main-branch OIDC JWT authorizes narrowly scoped signed object URLs.
Only SHA-256 authenticated original documents are exported. No editorial claims.
"""
import argparse
import concurrent.futures
import tempfile
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / ".katoptron-ci/nationwide-original-baselines"
SNAPSHOT = ROOT / ".katoptron-ci/nationwide-monitor-snapshot.json"
ID = re.compile(r"^[a-z0-9_-]{7,120}$")
SHA = re.compile(r"^[a-f0-9]{64}$")
MAX_SIZE = 34_000_000
AUDIENCE = "katoptron-originals-archive"
BUCKET = "katoptron-original-archive"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def request(url, *, data=None, method=None, headers=None, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(
        url, data=data, method=method, headers=headers or {}), timeout=timeout).read()

class Gateway:
    def __init__(self):
        origin = os.environ["SUPABASE_URL"].rstrip("/")
        host = urllib.parse.urlsplit(origin)
        if host.scheme != "https" or not re.fullmatch(r"[a-z0-9-]+\.supabase\.co", host.hostname or ""):
            raise ValueError("Untrusted archive service origin")
        self.origin = origin
        self.endpoint = origin + "/functions/v1/private-original-archive"
        token_url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
        separator = "&" if "?" in token_url else "?"
        body = request(token_url + separator + "audience=" + AUDIENCE, headers={
            "Authorization": "bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
        self.oidc = json.loads(body)["value"]
    def sign(self, action, *, source_id=None, sha256=None, kind=None, state=False):
        payload = {"action":action,"state":state}
        if not state:
            payload.update(source_id=source_id,sha256=sha256,kind=kind)
        data = request(self.endpoint, method="POST", data=json.dumps(payload).encode(), headers={
            "Authorization":"Bearer " + self.oidc, "Content-Type":"application/json"})
        result = json.loads(data)
        signed = result["signed_url"]
        parsed = urllib.parse.urlsplit(signed)
        if parsed.scheme != "https" or parsed.hostname != urllib.parse.urlsplit(self.origin).hostname:
            raise ValueError("Untrusted signed archive URL")
        if "/storage/v1/object/" not in parsed.path:
            raise ValueError("Unexpected signed storage path")
        return signed
    def upload(self, content, *, source_id=None, sha256=None, kind=None, state=False):
        if len(content)>MAX_SIZE: raise ValueError("Original larger than private bucket limit")
        signed = self.sign("sign_upload",source_id=source_id,sha256=sha256,kind=kind,state=state)
        mime = "application/json" if state or kind=="json" else ("application/pdf" if kind=="pdf" else "text/html")
        request(signed, data=content, method="PUT",headers={
            "Content-Type":mime,"x-upsert":"true" if state else "false"},timeout=90)
    def download(self, *, source_id=None, sha256=None, kind=None, state=False):
        signed = self.sign("sign_download",source_id=source_id,sha256=sha256,kind=kind,state=state)
        raw = request(signed,timeout=90)
        if len(raw)>MAX_SIZE: raise ValueError("Archived file exceeds bound")
        if not state and digest(raw)!=sha256: raise ValueError("Archived original failed SHA-256 verification")
        return raw

def valid_file(source_id, kind, sha):
    if not ID.fullmatch(source_id) or kind not in ("pdf","html","json") or not SHA.fullmatch(str(sha)):
        raise ValueError("Invalid archive source identity")

def collect(baseline=BASELINE,snapshot=SNAPSHOT):
    snap = json.loads(snapshot.read_text(encoding="utf8"))
    manifest = json.loads((baseline/"manifest.json").read_text(encoding="utf8"))
    if snap.get("schema_version")!=2 or snap.get("monitored_urls",0)<100 or manifest.get("schema_version")!=1:
        raise ValueError("Incomplete original-source snapshot/manifest")
    receipts = {s["source_id"]:s for s in snap["receipts"]}
    if len(receipts)!=snap["monitored_urls"]: raise ValueError("Duplicate original source")
    items={}
    for sid,meta in manifest.get("sources",{}).items():
        kind=meta["kind"];sha=meta["sha256"];valid_file(sid,kind,sha)
        r=receipts.get(sid)
        if not r or r.get("last_usable_sha256")!=sha or r.get("kind")!=kind:
            raise ValueError("Archived original and monitored receipt mismatch")
        p=baseline/(sid+"."+kind)
        data=p.read_bytes()
        if len(data)>MAX_SIZE or digest(data)!=sha:
            raise ValueError("Local publisher original failed SHA-256 verification")
        items[(sid,kind,sha)]=data
    for sid_dir in (baseline/"versions").glob("*") if (baseline/"versions").exists() else []:
        if not sid_dir.is_dir() or not ID.fullmatch(sid_dir.name): raise ValueError("Unsafe version directory")
        for p in sid_dir.iterdir():
            if not p.is_file() or p.suffix not in (".html",".pdf"): raise ValueError("Unsafe version archive")
            kind=p.suffix[1:];sha=p.stem
            valid_file(sid_dir.name,kind,sha)
            data=p.read_bytes()
            if len(data)>MAX_SIZE or digest(data)!=sha: raise ValueError("Corrupt original version")
            items[(sid_dir.name,kind,sha)]=data
    index={"schema_version":1,"observed_on":snap.get("observed_on"),
           "snapshot":snap,"manifest":manifest,
           "archives":[{"source_id":sid,"kind":kind,"sha256":sha}
                       for sid,kind,sha in sorted(items)]}
    return index,items

def backup(gateway,baseline=BASELINE,snapshot=SNAPSHOT):
    index,items=collect(baseline,snapshot)
    written=0;already=0
    def preserve(item):
        (sid,kind,sha),blob=item
        args={"source_id":sid,"kind":kind,"sha256":sha}
        try:
            old=gateway.download(**args)
            if old!=blob:raise ValueError("Archived original has mismatched bytes")
            return "already"
        except urllib.error.HTTPError as ex:
            if ex.code!=404:raise
            gateway.upload(blob,**args)
            if gateway.download(**args)!=blob:raise ValueError("Upload/restore mismatch")
            return "written"
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(preserve,items.items()):
            if result=="written":written+=1
            else:already+=1
    record=json.dumps(index,sort_keys=True,separators=(",",":")).encode()
    if len(record)>MAX_SIZE:raise ValueError("Archive index too large")
    gateway.upload(record,state=True)
    if gateway.download(state=True)!=record:raise ValueError("Archive index restore failed")
    return {"state":"verified","new_originals":written,"retained_originals":already,
            "source_count":len(index["manifest"]["sources"]),
            "archive_versions":len(items),"cold_restore_test":"passed_current_bytes"}

def restore(gateway,baseline=BASELINE,snapshot=SNAPSHOT,require=False):
    try:raw=gateway.download(state=True)
    except urllib.error.HTTPError as ex:
        if ex.code==404 and not require:return {"state":"no_prior_private_archive"}
        raise
    index=json.loads(raw)
    if index.get("schema_version")!=1 or not isinstance(index.get("archives"),list):
        raise ValueError("Untrusted private archive index")
    snap=index["snapshot"];manifest=index["manifest"]
    if snap.get("schema_version")!=2 or manifest.get("schema_version")!=1:
        raise ValueError("Invalid private archived snapshot")
    receipts={r["source_id"]:r for r in snap["receipts"]}
    if len(receipts)!=snap.get("monitored_urls") or len(receipts)<100:raise ValueError("Incomplete restore index")
    restored={}
    for item in index["archives"]:
        sid=item["source_id"];sha=item["sha256"];kind=item["kind"]
        valid_file(sid,kind,sha)
        restored[(sid,kind,sha)]=gateway.download(source_id=sid,kind=kind,sha256=sha)
    for sid,meta in manifest.get("sources",{}).items():
        key=(sid,meta["kind"],meta["sha256"])
        if key not in restored or receipts.get(sid,{}).get("last_usable_sha256")!=meta["sha256"]:
            raise ValueError("Missing original publisher in restored archive")
    baseline.mkdir(parents=True,exist_ok=True)
    for (sid,kind,sha),blob in restored.items():
        p=baseline/"versions"/sid/(sha+"."+kind)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
    for sid,meta in manifest.get("sources",{}).items():
        (baseline/(sid+"."+meta["kind"])).write_bytes(restored[(sid,meta["kind"],meta["sha256"])])
    (baseline/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    snapshot.parent.mkdir(parents=True,exist_ok=True)
    snapshot.write_text(json.dumps(snap,indent=2)+"\n")
    return {"state":"restored","originals":len(manifest.get("sources",{})),
            "versions":len(restored),"all_sha256_verified":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["backup","restore","restore-if-missing","cold-restore-test"])
    a=p.parse_args()
    if a.mode=="restore-if-missing" and SNAPSHOT.is_file() and (BASELINE/"manifest.json").is_file():
        print("PRIVATE_GOVERNMENT_ORIGINAL_ARCHIVE",json.dumps({"state":"cache_present"}));return
    gw=Gateway()
    if a.mode=="backup":result=backup(gw)
    elif a.mode=="cold-restore-test":
        # A fresh directory represents total CI cache loss. Never read a local
        # fingerprint or document. Validate all hashes against remote objects.
        with tempfile.TemporaryDirectory(prefix="katoptron-archive-cold-test-") as root:
            restored=restore(gw,Path(root)/"baselines",Path(root)/"snapshot.json",require=True)
            index,blobs=collect(Path(root)/"baselines",Path(root)/"snapshot.json")
            if not blobs or len(blobs)!=restored["versions"]:
                raise ValueError("Incomplete cold archive validation")
            result={"state":"verified_complete_cold_restore","originals":restored["originals"],
                    "versions":restored["versions"],"all_sha256_verified":True}
    else:result=restore(gw,require=a.mode=="restore")
    print("PRIVATE_GOVERNMENT_ORIGINAL_ARCHIVE",json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
