"""M9 read-only, daily release-safety workflow heartbeat.

Validates that the actual public GitHub main-branch release, provider and
private-data guard workflows have recently succeeded. Never fetches job logs,
artifacts, source tokens, account data or private report contents.
"""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request

ROOT='https://api.github.com/repos/ayeemecee0/Katoptron'
REPO='ayeemecee0/Katoptron'
MAX_BYTES=450_000
# Accepted age budgets include ordinary GitHub scheduled-workflow delays.
REQUIRED={
 'validate.yml':7,
 'browser_smoke.yml':7,
 'monitor_public_health.yml':3,
 'monitor_private_launch_gates.yml':3,
 'monitor_route_providers.yml':3,
 'live_community_acceptance.yml':10,
 'snapshot_public_evidence.yml':10,
 'prune_community_rate_events.yml':3,
 'monitor_production_capacity.yml':3
}
def fetch_runs(workflow,token):
 if workflow not in REQUIRED:raise ValueError('Unapproved workflow probe')
 if not token:raise ValueError('GitHub Actions read-only token required')
 url=ROOT+'/actions/workflows/'+workflow+'/runs?'+urllib.parse.urlencode({
   'branch':'main','per_page':8})
 request=urllib.request.Request(url,headers={
   'Authorization':'Bearer '+token,
   'Accept':'application/vnd.github+json',
   'X-GitHub-Api-Version':'2022-11-28',
   'User-Agent':'Katoptron-release-readiness/1.0'
 })
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*args,**kwargs):
   raise ValueError('Unexpected GitHub metadata redirect')
 with urllib.request.build_opener(NoRedirect).open(request,timeout=25) as res:
  if res.geturl()!=url or res.status!=200:
   raise ValueError('GitHub release-health metadata unavailable')
  raw=res.read(MAX_BYTES+1)
  if not raw or len(raw)>MAX_BYTES:raise ValueError('Invalid GitHub metadata length')
 val=json.loads(raw)
 if not isinstance(val,dict) or not isinstance(val.get('workflow_runs'),list):
  raise ValueError('GitHub workflow history missing')
 return val['workflow_runs']

def evaluate(workflow,runs,now=None):
 if workflow not in REQUIRED:raise ValueError('Unexpected release gate')
 now=now or dt.datetime.now(dt.timezone.utc)
 if not isinstance(runs,list):raise ValueError('Missing workflow executions')
 previous=[]
 for run in runs:
  if not isinstance(run,dict) or run.get('head_branch')!='main':
   continue
  stamp=run.get('created_at')
  if not isinstance(stamp,str):raise ValueError('Workflow run timestamp missing')
  try:created=dt.datetime.fromisoformat(stamp.replace('Z','+00:00'))
  except ValueError as error:raise ValueError('Invalid workflow run timestamp') from error
  if created.tzinfo is None or created>now+dt.timedelta(minutes=15):
   raise ValueError('Future/untrusted GitHub workflow timestamp')
  if run.get('status') not in ('queued','in_progress','completed','waiting','pending'):
   raise ValueError('Unknown GitHub workflow state')
  previous.append((created,run.get('conclusion'),run.get('status')))
 if not previous:raise ValueError(workflow+' has no main-branch runs')
 previous.sort(key=lambda x:x[0],reverse=True)
 age=now-previous[0][0]
 # A freshly started workflow is not success; allow <=2 hour execution
 # pending with recent previous green; never let a new failed run pass.
 recent=previous[0]
 if recent[2]=='completed' and recent[1]!='success':
  raise ValueError(workflow+' most recent release guard FAILED')
 good=next((x for x in previous if x[2]=='completed' and x[1]=='success'),None)
 if not good:
  raise ValueError(workflow+' lacks successful main-branch acceptance')
 if any(x[2]=='completed' and x[1]!='success' and x[0]>good[0]
        for x in previous):
  raise ValueError(workflow+' newer failed or cancelled execution still unresolved')
 age=now-good[0]
 if age>dt.timedelta(days=REQUIRED[workflow]):
  raise ValueError(workflow+' success is stale beyond '+str(REQUIRED[workflow])+' days')
 if recent[2]!='completed' and now-recent[0]>dt.timedelta(hours=2):
  raise ValueError(workflow+' has a stuck pending/in-progress release guard')
 return int(age.total_seconds()/3600)

def run():
 if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!=REPO:
  raise SystemExit('Daily release-health monitor only runs in trusted GitHub Actions')
 token=os.environ.get('GITHUB_TOKEN','')
 for workflow in REQUIRED:
  age=evaluate(workflow,fetch_runs(workflow,token))
  print('M9 RELEASE HEARTBEAT PASS',workflow,'last passed',age,'hour(s) ago')
 print('M9 release guard PASS: no unread job logs, private data or secret contents')

if __name__=='__main__':
 try:run()
 except Exception as exc:
  raise SystemExit('M9 RELEASE HEALTH FAILED: '+str(exc)) from None
