const assert=require('node:assert/strict');
const {summary,record,statusOf}=require('./publish_provider_health.cjs');
(async()=>{
 assert.deepEqual(summary({routing:[200,200],geocoding:[200]},true),{
  result_code:'passed',routing_http_status:200,geocoding_http_status:200,
  browser_test_passed:true
 });
 assert.equal(summary({routing:[429],geocoding:[]},false).result_code,'provider_error');
 assert.equal(summary({routing:[],geocoding:[]},false).result_code,'inconclusive');
 assert.equal(statusOf([200,503]),503);
 let received;
 const fetcher=async(uri,options)=>{
  assert.equal(uri,'https://bpvkapswslmgfazbzpsv.supabase.co/rest/v1/flock_provider_health_checks');
  received=options;
  return {ok:true,status:204};
 };
 const kind=await record({routing:[200],geocoding:[200]},true,fetcher,{
  SUPABASE_URL:'https://bpvkapswslmgfazbzpsv.supabase.co',
  SUPABASE_SERVICE_ROLE_KEY:'private-test-key-of-at-least-twenty-chars'
 });
 assert.equal(kind,'passed');
 assert.deepEqual(JSON.parse(received.body),[{
   result_code:'passed',routing_http_status:200,geocoding_http_status:200,
   browser_test_passed:true
 }]);
 assert.ok(!received.body.includes('Sacramento'));
 await assert.rejects(()=>record({routing:[],geocoding:[]},false,fetcher,{}),/not configured/);
 console.log('PROVIDER HEALTH PUBLIC FIXTURE REPORTING PASS');
})().catch(err=>{console.error(err);process.exitCode=1});
