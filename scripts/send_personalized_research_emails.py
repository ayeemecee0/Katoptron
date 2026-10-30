#!/usr/bin/env python3
"""Separate, explicitly consented, source-qualified research email digests.

No subscriber on enrollment, no historical event replay, no email to unconfirmed
accounts. At-most-once SMTP handoff, NOT a guarantee of inbox delivery.
"""
import json,os,re,sys,urllib.parse
from datetime import datetime,timezone
from email.message import EmailMessage
from send_government_watch_alerts import api,query,smtp_send,iso_datetime

TOPICS={
 "contract_document":{"contract","procurement"},
 "contract_renewal":{"contract"},
 "government_decision":{"oversight"},
 "policy_original_reviewed":{"policy"},
 "policy_draft_reviewed":{"policy"},
 "retention_changed":{"policy"},
 "sharing_list_changed":{"sharing"},
}
SOURCE_URL=re.compile(r"^https://[A-Za-z0-9.-]{5,220}/[^ \r\n<>]*$")
KEY=re.compile(r"^[a-z0-9_-]{8,160}$")
LOCALITY=re.compile(r"^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$")
MANAGE="https://ayeemecee0.github.io/Katoptron/professional-intelligence.html#researchEmail"

def qualified(event,sub):
 if not isinstance(event,dict) or not isinstance(sub,dict):return False
 if (event.get("evidence_tier")!="original_government" or
     event.get("kind") not in TOPICS or
     not KEY.fullmatch(str(event.get("event_key",""))) or
     not LOCALITY.fullmatch(str(event.get("locality_key",""))) or
     not SOURCE_URL.fullmatch(str(event.get("source_url",""))) or
     event["locality_key"]!=sub.get("locality_key") or
     not event.get("source_date") or not event.get("title") or not event.get("summary")):return False
 try:
  observed=iso_datetime(event["observed_at"])
  since=iso_datetime(sub["opted_in_at"])
 except (KeyError,ValueError,TypeError):return False
 if observed<=since or observed>datetime.now(timezone.utc):return False
 if not (TOPICS[event["kind"]] & set(sub.get("topics") or [])):return False
 keyword=(sub.get("keyword") or "").strip().lower()
 if keyword and len(keyword)>=3 and keyword not in (" ".join(str(event.get(k,"")) for k in
      ("title","summary","kind","source_agency_id"))).lower():return False
 return True

def email_for(sub,events,from_address):
 if not events or len(events)>8 or not all(qualified(e,sub) for e in events):
  raise ValueError("Source-qualified events and current explicit consent required")
 msg=EmailMessage()
 msg["From"]=from_address
 msg["To"]=sub["email"]
 msg["Subject"]="Katoptron Research — "+str(len(events))+" newly reviewed government source"+("s" if len(events)!=1 else "")+" for "+sub["locality_key"]
 lines=["Katoptron research email digest",
  "Only original-government evidence published after your separate research-email opt-in is included.",
  "Government source disclosures are not independent proof of violations or current camera status.",
  "No private plate observations, vehicle movements or private case records are included.",""]
 for e in events:
  lines.extend([
   e["title"][:220],
   "Original government source: "+e["source_url"],
   "Government source date: "+str(e["source_date"]),
   "Published evidence status: "+e["kind"],
   "Source-attributed summary: "+e["summary"][:500],
   "What to verify: Retrieve the original and check signed/adopted status and subsequent changes.",
   ""])
 lines.extend(["Manage or disable this separate research-email subscription:",
               MANAGE,
               "SMTP acceptance is not confirmation of inbox delivery."])
 msg.set_content("\n".join(lines))
 return msg

def claims_api(url,secret,path,method="GET",payload=None):
 # All claims and receipts are private and service-only. Return representation
 # to fail closed on missing/duplicate conditional state transitions.
 headers={"apikey":secret,"Authorization":"Bearer "+secret,
  "Content-Type":"application/json","Accept":"application/json"}
 if method=="POST":headers["Prefer"]="resolution=ignore-duplicates,return=representation"
 if method=="PATCH":headers["Prefer"]="return=representation"
 req_url=url.rstrip("/")+"/rest/v1/"+path
 import urllib.request
 body=json.dumps(payload).encode("utf8") if payload is not None else None
 req=urllib.request.Request(req_url,data=body,method=method,headers=headers)
 with urllib.request.urlopen(req,timeout=35) as r:
  data=r.read()
  return json.loads(data) if data else []

def transition(url,secret,sub,event_key,old,new,code=None):
 uid=sub["user_id"];locality=sub["locality_key"]
 path="research_email_send_claims?"+urllib.parse.urlencode({
   "user_id":"eq."+uid,"locality_key":"eq."+locality,
   "event_key":"eq."+event_key,"status":"eq."+old})
 data={"status":new,"status_changed_at":datetime.now(timezone.utc).isoformat()}
 if new=="smtp_submitted":data["smtp_accepted_at"]=datetime.now(timezone.utc).isoformat()
 if code:data["failure_code"]=code
 rows=claims_api(url,secret,path,"PATCH",data)
 if len(rows)!=1 or rows[0].get("status")!=new:raise RuntimeError("Atomic research outbox transition failed")
 return rows[0]

def run(url,secret,settings,send=smtp_send):
 subs=api(url,secret,"rpc/research_email_delivery_candidates","POST",{})
 if not isinstance(subs,list):raise RuntimeError("Protected research email candidates unavailable")
 count=0
 for sub in subs[:500]:
  if (not isinstance(sub,dict) or not LOCALITY.fullmatch(str(sub.get("locality_key",""))) or
      not sub.get("user_id") or not sub.get("email")):continue
  locality=sub["locality_key"];uid=sub["user_id"]
  events=query(url,secret,"flock_agency_watch_events",{
    "select":"event_key,locality_key,source_agency_id,kind,title,summary,source_url,source_date,evidence_tier,observed_at",
    "locality_key":"eq."+locality,"observed_at":"gt."+sub["opted_in_at"],
    "order":"observed_at.asc","limit":"150"})
  existing=query(url,secret,"research_email_send_claims",{
    "select":"event_key,status,status_changed_at","user_id":"eq."+uid,
    "locality_key":"eq."+locality,"limit":"1000"})
  known={x["event_key"]:x for x in existing}
  receipts=query(url,secret,"research_email_delivery_receipts",{
    "select":"event_key","user_id":"eq."+uid,"locality_key":"eq."+locality,"limit":"1000"})
  received={r["event_key"] for r in receipts}
  # SMTP-submitted claims may lack a receipt after an interrupted database write.
  # Reconcile the receipt without generating another email.
  for key,row in known.items():
   if row["status"]=="smtp_submitted" and key not in received:
    claims_api(url,secret,"research_email_delivery_receipts?on_conflict=user_id,locality_key,event_key",
       "POST",[{"user_id":uid,"locality_key":locality,"event_key":key}]);received.add(key)
   if row["status"]=="claimed" and key not in received and row.get("status_changed_at"):
    if (datetime.now(timezone.utc)-iso_datetime(row["status_changed_at"])).total_seconds()>600:
     transition(url,secret,sub,key,"claimed","uncertain","stale_smtp_outcome_unverified")
  eligible=[x for x in events if qualified(x,sub) and x["event_key"] not in received
      and x["event_key"] not in known][:8]
  if not eligible:continue
  # Queue once. A crash after a claim NEVER causes an automatic re-send.
  queued=[]
  for e in eligible:
   key=e["event_key"]
   rows=claims_api(url,secret,
    "research_email_send_claims?on_conflict=user_id,locality_key,event_key",
    "POST",[{"user_id":uid,"locality_key":locality,"event_key":key,"status":"queued"}])
   if len(rows)==1:queued.append(e)
  if not queued:continue
  # Recheck fresh, explicitly separate consent immediately before SMTP.
  updated=query(url,secret,"research_email_subscriptions",{
    "select":"enabled,opted_in_at,topics,keyword",
    "user_id":"eq."+uid,"locality_key":"eq."+locality,"limit":"2"})
  fresh=updated[0] if len(updated)==1 else {}
  same_consent=(fresh.get("enabled") is True and fresh.get("opted_in_at")==sub["opted_in_at"] and
    fresh.get("topics")==sub.get("topics") and fresh.get("keyword")==sub.get("keyword"))
  if not same_consent:
   for e in queued:transition(url,secret,sub,e["event_key"],"queued","canceled","consent_changed")
   continue
  candidates=[e for e in queued if qualified(e,{**sub,**fresh})]
  for e in queued:
   if e not in candidates:transition(url,secret,sub,e["event_key"],"queued","canceled","relevance_changed")
  if not candidates:continue
  for e in candidates:transition(url,secret,sub,e["event_key"],"queued","claimed")
  msg=email_for(sub,candidates,settings[4])
  try:send(msg,settings)
  except Exception:
   for e in candidates:
    transition(url,secret,sub,e["event_key"],"claimed","uncertain","smtp_outcome_unknown")
   raise
  for e in candidates:transition(url,secret,sub,e["event_key"],"claimed","smtp_submitted")
  claims_api(url,secret,"research_email_delivery_receipts?on_conflict=user_id,locality_key,event_key",
   "POST",[{"user_id":uid,"locality_key":locality,"event_key":e["event_key"]} for e in candidates])
  count+=1
 return count

def main():
 url=os.environ.get("SUPABASE_URL");secret=os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
 env=("WATCH_SMTP_HOST","WATCH_SMTP_PORT","WATCH_SMTP_USER","WATCH_SMTP_PASSWORD","WATCH_SMTP_FROM")
 if not url or not secret:raise RuntimeError("Service-role credential unavailable")
 if not all(os.environ.get(k) for k in env):
  print("PERSONALIZED_RESEARCH_EMAIL_INACTIVE: encrypted SMTP is not fully configured; no sends.")
  return
 settings=(os.environ[env[0]],int(os.environ[env[1]]),os.environ[env[2]],os.environ[env[3]],os.environ[env[4]])
 if settings[1] not in (465,587):raise ValueError("Only encrypted SMTP allowed")
 count=run(url,secret,settings)
 print("RESEARCH_DIGEST_SMTP_ACCEPTED_WITH_RECEIPTS",count,"(not inbox confirmations; no addresses logged)")
if __name__=="__main__":
 try:main()
 except Exception as e:
  raise SystemExit("RESEARCH_DIGEST_HELD "+type(e).__name__+"; inspect restricted workflow logs") from None
