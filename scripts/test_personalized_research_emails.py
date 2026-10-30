#!/usr/bin/env python3
"""Deterministic research digest opt-in, relevance, no replay and SMTP idempotency tests."""
import importlib.util,unittest,datetime as dt
from pathlib import Path
P=Path(__file__).with_name("send_personalized_research_emails.py")
spec=importlib.util.spec_from_file_location("research_sender",P)
import sys
sys.path.insert(0,str(P.parent))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
NOW=dt.datetime.now(dt.timezone.utc)
iso=lambda d:d.isoformat()
SUB={"user_id":"11111111-1111-1111-1111-111111111111","email":"test@example.org","locality_key":"houston|TX",
     "topics":["contract"],"keyword":"agreement","opted_in_at":iso(NOW-dt.timedelta(hours=6))}
EVENT={"event_key":"new_government_contract_2026","locality_key":"houston|TX",
       "source_agency_id":"houston city secretary","kind":"contract_document",
       "title":"Original agency agreement approval",
       "summary":"Source-dated original government agreement with unresolved execution status",
       "source_url":"https://www.houstontx.gov/source-agreement",
       "source_date":"2026-10-29","evidence_tier":"original_government",
       "observed_at":iso(NOW-dt.timedelta(hours=1))}
class DigestTests(unittest.TestCase):
 def test_consent_and_strict_evidence_matching(self):
  self.assertTrue(M.qualified(EVENT,SUB))
  for invalid in [
   {**EVENT,"observed_at":iso(NOW-dt.timedelta(days=3))},
   {**EVENT,"evidence_tier":"vendor_portal"},
   {**EVENT,"source_url":"http://bad.example/original"},
   {**EVENT,"source_date":None},
   {**EVENT,"kind":"vendor_portal_snapshot"},
   {**EVENT,"locality_key":"oakland|CA"},
   {**EVENT,"event_key":"_bad"}]:
   self.assertFalse(M.qualified(invalid,SUB))
  self.assertFalse(M.qualified(EVENT,{**SUB,"topics":["policy"]}))
  self.assertFalse(M.qualified(EVENT,{**SUB,"keyword":"unmatchedword"}))
  self.assertFalse(M.qualified(EVENT,{**SUB,"opted_in_at":iso(NOW+dt.timedelta(minutes=1))}))
  msg=M.email_for(SUB,[EVENT],"no-reply@example.org")
  self.assertEqual(msg["To"],SUB["email"])
  body=msg.get_content()
  self.assertIn(EVENT["source_url"],body)
  self.assertIn("Manage or disable",body)
  self.assertNotIn("actual plate reads",body)
  with self.assertRaisesRegex(ValueError,"qualified"):
   M.email_for(SUB,[{**EVENT,"evidence_tier":"vendor"}],"no-reply@example.org")
 def test_end_to_end_at_most_once_and_pre_smtp_cancel(self):
  claims={};receipts=set();sends=[]
  from copy import deepcopy
  subscription={"enabled":True,"opted_in_at":SUB["opted_in_at"],
    "topics":SUB["topics"],"keyword":SUB["keyword"]}
  old=(M.api,M.query,M.claims_api,M.transition)
  def api(url,secret,path,method="GET",payload=None):
   if path=="rpc/research_email_delivery_candidates":return [dict(SUB)]
   raise AssertionError(path)
  def query(url,secret,table,filters):
   if table=="flock_agency_watch_events":return [EVENT]
   if table=="research_email_send_claims":
    return [{"event_key":k,"status":x["status"],"status_changed_at":x.get("status_changed_at")}
            for k,x in claims.items()]
   if table=="research_email_delivery_receipts":return [{"event_key":x} for x in receipts]
   if table=="research_email_subscriptions":return [dict(subscription)]
   raise AssertionError(table)
  def claim(url,secret,path,method="GET",payload=None):
   if method=="POST":
    if path.startswith("research_email_send_claims"):
     record=payload[0];key=record["event_key"]
     if key in claims:return []
     claims[key]={"status":"queued"};return [record]
    if path.startswith("research_email_delivery_receipts"):
     for r in payload:receipts.add(r["event_key"])
     return payload
   raise AssertionError((path,method))
  def transition(url,secret,sub,key,prev,new,code=None):
   assert claims[key]["status"]==prev
   claims[key]={"status":new,"status_changed_at":iso(NOW)}
   return claims[key]
  M.api,M.query,M.claims_api,M.transition=api,query,claim,transition
  try:
   send=lambda m,s:sends.append(m)
   settings=("smtp.example.org",465,"x","y","no-reply@example.org")
   self.assertEqual(M.run("https://example.supabase.co","secret",settings,send=send),1)
   self.assertEqual(len(sends),1)
   self.assertEqual(claims[EVENT["event_key"]]["status"],"smtp_submitted")
   self.assertEqual(receipts,{EVENT["event_key"]})
   self.assertEqual(M.run("https://example.supabase.co","secret",settings,send=send),0)
   self.assertEqual(len(sends),1)
   # Existing digest record is never retried after change to consent.
   receipts.clear();subscription["enabled"]=False
   self.assertEqual(M.run("https://example.supabase.co","secret",settings,send=send),0)
   self.assertEqual(len(sends),1)
  finally:M.api,M.query,M.claims_api,M.transition=old
 def test_uncertain_smtp_cannot_auto_retry(self):
  claims={};sent=0
  old=(M.api,M.query,M.claims_api,M.transition)
  def api(url,secret,path,method="GET",payload=None):return [dict(SUB)]
  def query(url,secret,table,criteria):
   return ([EVENT] if table=="flock_agency_watch_events" else
       [{"event_key":k,"status":v,"status_changed_at":iso(NOW)} for k,v in claims.items()]
       if table=="research_email_send_claims" else []
       if table=="research_email_delivery_receipts" else
       [{"enabled":True,"opted_in_at":SUB["opted_in_at"],"topics":SUB["topics"],"keyword":SUB["keyword"]}])
  def req(url,secret,path,method="GET",payload=None):
   if path.startswith("research_email_delivery_receipts"):return payload
   key=payload[0]["event_key"]
   if key in claims:return []
   claims[key]="queued";return payload
  def trans(url,secret,sub,key,prev,new,code=None):
   claims[key]=new;return {"status":new}
  M.api,M.query,M.claims_api,M.transition=api,query,req,trans
  try:
   def bad_send(*args):raise TimeoutError("unknown smtp outcome")
   with self.assertRaises(TimeoutError):M.run("https://example.supabase.co","secret",("host",465,"u","p","sender@example.org"),send=bad_send)
   self.assertEqual(claims[EVENT["event_key"]],"uncertain")
   self.assertEqual(M.run("https://example.supabase.co","secret",("host",465,"u","p","sender@example.org"),send=bad_send),0)
  finally:M.api,M.query,M.claims_api,M.transition=old
if __name__=="__main__":unittest.main()
