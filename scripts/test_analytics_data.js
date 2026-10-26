const assert=require('node:assert/strict');
const data=require('../analytics-data.js');
function response(rows,header,status=200){
 return {ok:status===200,status,headers:{get:k=>k.toLowerCase()==='content-range'?header:null},
         json:async()=>rows};
}
async function run(){
 const dummy={state_code:'CA'};
 const rows=Array.from({length:415},(_,i)=>({state_code:'S'+String(i).padStart(3,'0')}));
 let calls=[];
 const fetcher=async(url,options)=>{
  const range=options.headers.Range.match(/^(\d+)-(\d+)$/);
  assert.ok(range);
  assert.equal(options.headers.Prefer,'count=exact');
  assert.match(url,/order=state_code.asc/);
  const a=Number(range[1]),b=Number(range[2]);
  const part=rows.slice(a,b+1);
  calls.push(a);
  return response(part,a+'-'+(a+part.length-1)+'/415');
 };
 const got=await data.read('flock_analytics_states','https://example.gov','public-key',fetcher);
 assert.equal(got.length,415);
 assert.deepEqual(calls,[0,200,400]);
 assert.equal(new Set(got.map(r=>r.state_code)).size,415);
 assert.equal((await data.read('flock_analytics_states','https://example.gov','public-key',
  async()=>response([],'*/0'))).length,0);
 for(const bad of [
  async()=>response([{state_code:'CA'}],null),
  async()=>response([{state_code:'CA'}],'0-0/*'),
  async()=>response([{state_code:'CA'}],'0-0/999999'),
  async()=>response([{state_code:'CA'}],'1-1/1'),
  async()=>response([{state_code:'CA'}],'0-1/2'),
  async()=>response([],'*/2')
 ]){
  await assert.rejects(()=>data.read('flock_analytics_states','https://example.gov','public-key',bad),
    /count|incomplete|Missing|overlap|exceeds|source/i);
 }
 await assert.rejects(()=>data.read('flock_analytics_states','https://example.gov','public-key',
  async()=>response([],null,500)),/HTTP 500/);
 const dup=async(url,opt)=>{
  const start=Number(opt.headers.Range.split('-')[0]);
  return start===0?response([{state_code:'CA'}],'0-0/2'):
   response([{state_code:'CA'}],'1-1/2');
 };
 await assert.rejects(()=>data.read('flock_analytics_states','https://example.gov','public-key',dup,{limit:1}),
  /Duplicate/);
 const changed=async(url,opt)=>{
  const start=Number(opt.headers.Range.split('-')[0]);
  return start===0?response([{state_code:'CA'}],'0-0/2'):
   response([{state_code:'NY'}],'1-1/3');
 };
 await assert.rejects(()=>data.read('flock_analytics_states','https://example.gov','public-key',changed,{limit:1}),
  /count changed/);
 const overview={exact_government_points:316,source_flock_labeled_points:293,
  generic_lpr_points:23,unknown_manufacturer_points:0,states_with_any_documented_evidence:2};
 const stateRows=[
  {state_code:'CA',source_flock_labeled_points:293,generic_lpr_points:0,
   unknown_manufacturer_points:0,verified_exact_gis_points:293},
  {state_code:'TX',source_flock_labeled_points:0,generic_lpr_points:23,
   unknown_manufacturer_points:0,verified_exact_gis_points:23}];
 assert.equal(data.reconcile(overview,stateRows),true);
 assert.throws(()=>data.reconcile({...overview,source_flock_labeled_points:294},stateRows),
  /classification inconsistent/);
 assert.throws(()=>data.reconcile(overview,[{...stateRows[0],source_flock_labeled_points:292},stateRows[1]]),
  /do not reconcile/);
 assert.throws(()=>data.reconcile({...overview,unknown_manufacturer_points:2},stateRows),
  /classification inconsistent/);
 await assert.rejects(()=>data.read('private_reporter_addresses','https://example.gov','key',
  async()=>response([],'*/0')),/unavailable/);
 console.log('M7 ANALYTICS DATA PASS: bounded complete pagination, no silent truncation, no duplicate/count race and exact manufacturer split');
}
run().catch(e=>{console.error(e);process.exitCode=1});
