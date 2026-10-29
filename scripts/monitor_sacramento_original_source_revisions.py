#!/usr/bin/env python3
"""Review-only original Sacramento government source revision watcher.

Only three explicitly allowlisted official documents. An observed HTTP/PDF
content change opens a *review issue*, never an enacted government action, a
public camera record or a Government Watch subscription alert.

An owner-controlled GitHub issue stores first-observation source fingerprints
for ongoing comparison; no subscriber emails or private data leave Supabase.
"""
import hashlib
import json
import os
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data/sacramento-original-watch-source-registry.json"
TITLE="Katoptron original-source revision baseline - Sacramento County"
BEGIN="KATOPTRON_ORIGINAL_WATCH_STATE_BEGIN"
END="KATOPTRON_ORIGINAL_WATCH_STATE_END"
TRUSTED={
 "sacramento-da-alpr-access-policy":
    "https://www.sacda.org/policies/alpr/",
 "sacramento-sheriff-historic-alpr-pdf":
    "https://www.sacsheriff.com/documents/Auto%20License%20Plate%20Reader%20Program.pdf",
 "sacramento-flock-ceqa-notice":
    "https://ceqanet.lci.ca.gov/2025051277"
}
ALLOWED_HOSTS={"www.sacda.org","www.sacsheriff.com","ceqanet.lci.ca.gov"}

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.parts=[];self.skipped=0
    def handle_starttag(self,name,attrs):
        if name in ("script","style","svg","noscript"):self.skipped+=1
    def handle_endtag(self,name):
        if name in ("script","style","svg","noscript"):self.skipped=max(0,self.skipped-1)
    def handle_data(self,data):
        if self.skipped==0:self.parts.append(data)

def validated_sources(path=CATALOG):
    raw=json.loads(Path(path).read_text(encoding="utf8"))
    if (raw.get("schema_version")!=1 or
        raw.get("scope")!="fixed_trusted_sacramento_original_source_urls_for_revision_review_only" or
        not isinstance(raw.get("sources"),list) or len(raw["sources"])!=3):
        raise ValueError("Unverified Sacramento original source watch catalog")
    sources={x.get("id"):x for x in raw["sources"]}
    if set(sources)!=set(TRUSTED):raise ValueError("Unexpected official source identity")
    for ident,s in sources.items():
        if s.get("url")!=TRUSTED[ident] or s.get("mode") not in ("pdf","html"):
            raise ValueError("Source URL or kind identity drift")
        parts=urllib.parse.urlsplit(s["url"])
        if parts.scheme!="https" or parts.hostname not in ALLOWED_HOSTS or parts.username or parts.password or parts.port:
            raise ValueError("Unknown source publisher")
        if s["mode"]=="html" and not all(
            isinstance(s.get(k),str) and 8<len(s[k])<90
            for k in ("start_anchor","end_anchor","required_phrase")
        ):raise ValueError("Required source-body fingerprint anchors missing")
    return list(raw["sources"])

def fingerprint(doc,raw):
    """Hash only the government publication's bounded substantive content."""
    if not isinstance(raw,bytes) or len(raw)>16_000_000:raise ValueError("Original source too large")
    if doc["mode"]=="pdf":
        if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-4096:] or len(raw)<1000:
            raise ValueError("Not an intact source PDF")
        return hashlib.sha256(raw).hexdigest()
    if not (500<len(raw)<5_000_000):raise ValueError("Unexpected government HTML response")
    extractor=Text();extractor.feed(raw.decode("utf-8","replace"))
    normalized=" ".join(" ".join(extractor.parts).split())
    start=normalized.find(doc["start_anchor"])
    if start<0:raise ValueError("Expected official policy / filing heading missing")
    end=normalized.find(doc["end_anchor"],start+len(doc["start_anchor"]))
    if end<=start+160:raise ValueError("Government document section changed unexpectedly")
    scoped=normalized[start:end]
    if doc["required_phrase"].casefold() not in scoped.casefold():
        raise ValueError("Original document topic phrase absent")
    return hashlib.sha256(scoped.encode("utf-8")).hexdigest()

def safe_response(doc,request=urllib.request.urlopen):
    source=urllib.request.Request(doc["url"],headers={
        "User-Agent":"KatoptronOriginalGovernmentSourceAudit/1.0 (+https://ayeemecee0.github.io/Katoptron/)",
        "Accept":"application/pdf,text/html;q=0.9,*/*;q=0.4"})
    with request(source,timeout=35) as response:
        final=urllib.parse.urlsplit(response.geturl())
        initial=urllib.parse.urlsplit(doc["url"])
        if final.scheme!="https" or final.hostname!=initial.hostname or final.username or final.password:
            raise ValueError("Government document left verified publisher host")
        data=response.read(16_000_001)
    return fingerprint(doc,data)

def parse_state(body):
    if not isinstance(body,str) or BEGIN not in body or END not in body:
        raise ValueError("Official source baseline marker missing")
    content=body.split(BEGIN,1)[1].split(END,1)[0].strip()
    data=json.loads(content)
    if not isinstance(data,dict) or set(data)-set(TRUSTED):
        raise ValueError("Untrusted fingerprint baseline shape")
    if any(not re.fullmatch("[a-f0-9]{64}",str(x)) for x in data.values()):
        raise ValueError("Untrusted original fingerprint")
    return data

def state_body(states):
    return ("Katoptron private-action original-source audit state.\n\n"
      "These are **observation hashes**, not accepted government claims.\n"
      "No automatically observed edit represents an adopted contract or sends subscriber mail.\n\n"
      +BEGIN+"\n"+json.dumps(states,sort_keys=True,indent=2)+"\n"+END+
      "\n\nOnly government publisher pages from the pinned source registry are monitored.")

def compare(previous,observed):
    """Return newly bootstrapped and revision-flagged rows. Never claim enacted changes."""
    baseline=dict(previous)
    bootstrapped=[];modified=[]
    for ident,newhash in observed.items():
        if ident not in TRUSTED or not re.fullmatch("[0-9a-f]{64}",newhash):
            raise ValueError("Unapproved revision fingerprint")
        prior=baseline.get(ident)
        if prior is None:bootstrapped.append(ident)
        elif prior!=newhash:modified.append((ident,prior,newhash))
        baseline[ident]=newhash
    return baseline,bootstrapped,modified

def github_api(repo,token,verb,resource,payload=None):
    if repo!="ayeemecee0/Katoptron" or not token:
        raise ValueError("Protected repository identity or action token absent")
    req=urllib.request.Request("https://api.github.com"+resource,
      headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
               "X-GitHub-Api-Version":"2022-11-28","User-Agent":"katoptron-original-watch"},
      method=verb,data=json.dumps(payload).encode() if payload is not None else None)
    with urllib.request.urlopen(req,timeout=30) as r:
        result=json.loads(r.read().decode("utf-8"))
    return result

def find_baseline(repo,token,api=github_api):
    # Closed baseline issues would be suspicious; fail closed, do not create duplicates.
    for page in range(1,5):
        data=api(repo,token,"GET","/repos/"+repo+"/issues?state=all&per_page=100&page="+str(page))
        if not isinstance(data,list):raise RuntimeError("GitHub issues unavailable")
        matches=[x for x in data if x.get("title")==TITLE and not x.get("pull_request")]
        if len(matches)>1:raise RuntimeError("Duplicate watch baseline issue")
        if matches:
            return matches[0]
        if len(data)<100:break
    return None

def publish(repo,token,observed,sources,api=github_api):
    issue=find_baseline(repo,token,api)
    previous=parse_state(issue["body"]) if issue else {}
    current,bootstrapped,changed=compare(previous,observed)
    if issue is None:
        created=api(repo,token,"POST","/repos/"+repo+"/issues",{
          "title":TITLE,"body":state_body(current)})
        return {"baseline_created":bool(created.get("number")),
                "source_baselines_added":len(bootstrapped),
                "source_revisions_held_for_review":0,"alert_events_created":0}
    if changed:
        index={s["id"]:s for s in sources}
        for ident,prior,now in changed:
            s=index[ident]
            title="Review original Sacramento government source revision: "+ident+" ("+now[:12]+")"
            body=("**Source edit requires original evidence review.**\n\n"
                  "This is an observed content/hash change, **NOT** evidence that a "
                  "contract, policy or surveillance setting was adopted, operational or changed.\n\n"
                  "Government source: "+s["url"]+"\n"
                  "Prior observed SHA256: `"+prior+"`\n"
                  "New observed SHA256: `"+now+"`\n"
                  "First review the issuer, text, substantive change, date and status.\n"
                  "**Do not publish a Government Watch alert from this hash alone.**")
            api(repo,token,"POST","/repos/"+repo+"/issues",{"title":title,"body":body})
    if changed or bootstrapped:
        api(repo,token,"PATCH","/repos/"+repo+"/issues/"+str(issue["number"]),
            {"body":state_body(current)})
    return {"baseline_created":False,"source_baselines_added":len(bootstrapped),
            "source_revisions_held_for_review":len(changed),"alert_events_created":0}

def main():
    sources=validated_sources()
    results={};holds=[]
    for doc in sources:
        try:
            results[doc["id"]]=safe_response(doc)
        except Exception as exc:
            holds.append(doc["id"]+": "+type(exc).__name__)
    if not results:raise RuntimeError("All verified Sacramento publisher sources held")
    repo=os.environ.get("GITHUB_REPOSITORY","")
    token=os.environ.get("GH_TOKEN","")
    result=publish(repo,token,results,sources)
    print("Sacramento source observation:",json.dumps({
        "official_sources_attempted":len(sources),"official_sources_retrieved":len(results),
        "original_sources_held":len(holds),**result}))
    if holds:print("Source availability holds (no inference):",json.dumps(holds))

if __name__=="__main__":main()
