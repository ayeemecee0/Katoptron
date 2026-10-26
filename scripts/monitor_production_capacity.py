"""Fail-closed, PII-free Supabase Free-plan capacity/retention monitor.

Only one fixed service-role RPC is called; no row-level data, objects, address,
credentials, account IDs or images are downloaded or logged.
"""
import json
import os
import urllib.error
import urllib.request

PROJECT='https://bpvkapswslmgfazbzpsv.supabase.co'
RPC=PROJECT+'/rest/v1/rpc/katoptron_private_launch_capacity'
FREE_DB_BYTES=500_000_000  # conservative vs 500 MiB
FREE_STORAGE_BYTES=1_000_000_000  # bucket lower bound only; not org usage
DATABASE_WARN_AT=0.60
DATABASE_FAIL_AT=0.80
BUCKET_WARN_AT=0.70
BUCKET_FAIL_AT=0.85
MAX_BYTES=4096
FIELDS=('database_bytes','private_community_report_count',
        'private_community_photo_count','private_community_photo_metadata_bytes',
        'private_photo_size_metadata_missing','retained_one_day_rate_events',
        'expired_one_day_rate_events','active_auth_accounts',
        'registered_private_bucket_count')

def fetch(key):
    if not (isinstance(key,str) and key.startswith(('sb_secret_','eyJ'))
            and len(key)<2048):
        raise ValueError('Server-only Supabase credential is required')
    request=urllib.request.Request(RPC,method='POST',data=b'{}',headers={
        'apikey':key,'Authorization':'Bearer '+key,
        'Content-Type':'application/json','Accept':'application/json',
        'User-Agent':'Katoptron-service-only-capacity/1.0'
    })
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):
            raise ValueError('Unexpected credential-bearing redirect')
    with urllib.request.build_opener(NoRedirect).open(request,timeout=25) as result:
        if result.geturl()!=RPC or result.status!=200:
            raise ValueError('Private capacity RPC unavailable')
        raw=result.read(MAX_BYTES+1)
        if not raw or len(raw)>MAX_BYTES or not result.headers.get('Content-Type','').startswith('application/json'):
            raise ValueError('Malformed private capacity response')
    return json.loads(raw)

def evaluate(data):
    if not isinstance(data,dict) or set(data)!=set(FIELDS):
        raise ValueError('Private capacity report shape changed')
    for name in FIELDS:
        if type(data[name]) is not int or data[name]<0:
            raise ValueError('Invalid capacity count: '+name)
    if data['registered_private_bucket_count']!=1:
        raise ValueError('Critical: private report Storage bucket missing/not private')
    if data['private_photo_size_metadata_missing']>0:
        raise ValueError('Private Storage size metadata unavailable; no reliable file-byte estimate')
    if data['expired_one_day_rate_events']>0:
        raise ValueError('Expired private one-day rate-event metadata not purged within grace window')
    size=data['database_bytes'];bucket=data['private_community_photo_metadata_bytes']
    if size>=FREE_DB_BYTES*DATABASE_FAIL_AT:
        raise ValueError('Database >=80% Free limit; stop nonessential acquisition and repair capacity')
    if bucket>=FREE_STORAGE_BYTES*BUCKET_FAIL_AT:
        raise ValueError('Private community photo bucket >=85% Free organization Storage allowance')
    warnings=[]
    if size>=FREE_DB_BYTES*DATABASE_WARN_AT:
        warnings.append('Database >=60% of the Free limit; plan capacity and prioritize verified data')
    if bucket>=FREE_STORAGE_BYTES*BUCKET_WARN_AT:
        warnings.append('Private photo bucket >=70% of the Free organization Storage allowance')
    return {'database_percent':round(size/FREE_DB_BYTES*100,1),
            'private_bucket_percent_lower_bound':round(bucket/FREE_STORAGE_BYTES*100,1),
            'reports':data['private_community_report_count'],
            'photos':data['private_community_photo_count'],
            'accounts':data['active_auth_accounts'],
            'rate_events':data['retained_one_day_rate_events'],
            'warnings':warnings}

def run():
    key=os.environ.get('SUPABASE_SERVICE_ROLE_KEY','')
    report=evaluate(fetch(key))
    print('M9 PRIVATE CAPACITY GUARD PASS: database',report['database_percent'],
          '% conservative Free-plan 500MB allowance')
    print('PRIVATE STORAGE lower-bound',report['private_bucket_percent_lower_bound'],
          '% of Free organization 1GB quota; NOT organization-wide Storage usage')
    print('COUNTS ONLY: reports',report['reports'],'private photos',report['photos'],
          'accounts',report['accounts'],'unexpired private rate events',report['rate_events'])
    for warning in report['warnings']:
        print('::warning::'+warning)
    print('No account details, routes, private row contents, object paths or credentials read.')

if __name__=='__main__':
    try:run()
    except Exception as error:
        raise SystemExit('M9 PRIVATE CAPACITY GATE FAILED: '+str(error)) from None
