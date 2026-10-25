/* Node-only daily fixed public Geoapify health audit reporter.
 * Do not import into browser; the CI service key is never sent to page code.
 */
'use strict';
const PROJECT='https://bpvkapswslmgfazbzpsv.supabase.co';
function statusOf(list){
 if(!Array.isArray(list)||list.length===0)return null;
 const bad=list.find(x=>!Number.isInteger(x)||x!==200);
 return bad===undefined?200:Number.isInteger(bad)&&bad>=100&&bad<=599?bad:null;
}
function summary(results,completed){
 const route=statusOf(results?.routing),geo=statusOf(results?.geocoding);
 const passed=Boolean(completed&&route===200&&geo===200);
 const providerError=[route,geo].some(x=>Number.isInteger(x)&&x>=400);
 return {result_code:passed?'passed':providerError?'provider_error':'inconclusive',
   routing_http_status:route,geocoding_http_status:geo,
   browser_test_passed:passed};
}
async function record(results,completed,fetcher=fetch,env=process.env){
 const data=summary(results,completed);
 const key=env.SUPABASE_SERVICE_ROLE_KEY;
 if(env.SUPABASE_URL!==PROJECT||typeof key!=='string'||key.length<20)
  throw Error('Private monitored provider-health destination is not configured');
 const response=await fetcher(PROJECT+'/rest/v1/flock_provider_health_checks',{
  method:'POST',headers:{apikey:key,Authorization:'Bearer '+key,
   'Content-Type':'application/json',Prefer:'return=minimal'},
  body:JSON.stringify([data]),redirect:'error',cache:'no-store'
 });
 if(!response.ok)throw Error('Public synthetic provider-health receipt was not published, HTTP '+response.status);
 return data.result_code;
}
module.exports={statusOf,summary,record};
