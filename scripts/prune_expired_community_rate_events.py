"""Scheduled one-day community anti-abuse event minimization.

Run with existing server-only GitHub Actions credential. Does not read report
content, camera coordinates, email addresses or private photo storage.
"""
import json
import os
import urllib.request

def main():
 if os.environ.get("GITHUB_ACTIONS")!="true" or os.environ.get("GITHUB_REPOSITORY")!="ayeemecee0/Katoptron":
  raise SystemExit("Prune must run in authorized CI")
 key=os.environ.get("SUPABASE_SERVICE_ROLE_KEY","")
 if not key.startswith(("sb_secret_","eyJ")):
  raise SystemExit("Service-only credential not configured")
 url="https://bpvkapswslmgfazbzpsv.supabase.co/rest/v1/rpc/prune_expired_community_submission_rate_events"
 h={"apikey":key,"Content-Type":"application/json","Accept":"application/json"}
 if key.startswith("eyJ"):h["Authorization"]="Bearer "+key
 req=urllib.request.Request(url,data=b"{}",headers=h,method="POST")
 try:
  with urllib.request.urlopen(req,timeout=25) as response:
   if response.status!=200 or response.geturl()!=url:
    raise RuntimeError("Unexpected prune response")
   n=json.load(response)
   if type(n) is not int or n<0:
    raise RuntimeError("Prune count missing or invalid")
   print("M5 private rate ledger cleanup PASS; expired events purged:",n)
 except Exception as exc:
  raise SystemExit("M5 community privacy pruning FAILED: "+type(exc).__name__) from None
if __name__=="__main__":main()
