/* Strict read-only analytics transport: exact PostgREST counts, stable pages,
 * duplicate detection, upper bounds and snapshot source-count changes fail closed.
 * No route, plate or individual contributor statistics or data stored. */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronAnalyticsData=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const PAGE_SIZE=200,MAX_PAGES=25;
 const orders=Object.freeze({
  flock_analytics_overview:'exact_government_points.asc',
  flock_analytics_states:'state_code.asc',
  flock_analytics_monthly_evidence:'evidence_month.asc,event_type.asc'
 });
 async function read(table,base,key,fetcher=fetch,options={}){
  if(!orders[table]||typeof base!=='string'||!base.startsWith('https://')||
     typeof key!=='string'||!key||typeof fetcher!=='function')
   throw Error('Public analytics source unavailable');
  const limit=options.limit||PAGE_SIZE,budget=options.budget||MAX_PAGES;
  if(!Number.isInteger(limit)||limit<1||limit>PAGE_SIZE||
     !Number.isInteger(budget)||budget<1||budget>MAX_PAGES)
   throw Error('Invalid bounded analytics pagination');
  const all=[],seen=new Set();let total=null;
  for(let i=0;i<budget;i++){
   const start=i*limit,end=start+limit-1;
   const url=new URL(base+'/rest/v1/'+table);
   url.searchParams.set('select','*');
   url.searchParams.set('order',orders[table]);
   const response=await fetcher(url.href,{
    headers:{apikey:key,Prefer:'count=exact',Range:start+'-'+end},
    cache:'no-store',referrerPolicy:'no-referrer'
   });
   if(!response.ok)throw Error('Public analytics HTTP '+response.status);
   const rows=await response.json(),range=response.headers.get('content-range');
   if(!Array.isArray(rows)||rows.length>limit||typeof range!=='string')
    throw Error('Public analytics source response incomplete');
   const match=/^(?:(\d+)-(\d+)|\*)\/(\d+)$/.exec(range.trim());
   if(!match)throw Error('Exact public analytics source count unavailable');
   const count=Number(match[3]);
   if(!Number.isSafeInteger(count)||count<0||count>limit*budget||
      total!==null&&count!==total)
    throw Error('Public analytics source count changed or exceeds budget');
   total=count;
   if(rows.length){
    if(Number(match[1])!==start||Number(match[2])!==start+rows.length-1||
       rows.length>count-start)throw Error('Incomplete or overlapping analytics page');
   }else if(count>start)throw Error('Missing analytics rows');
   for(const row of rows){
    const id=table==='flock_analytics_monthly_evidence'?
     row.evidence_month+'|'+row.event_type:
     table==='flock_analytics_states'?row.state_code:'national-overview';
    if(seen.has(id))throw Error('Duplicate source analytics rows');
    seen.add(id);all.push(row);
   }
   if(all.length===count)return all;
   if(!rows.length)throw Error('Incomplete public analytics source');
  }
  throw Error('Public analytics exceeds complete-source query budget');
 }
 function reconcile(o,states){
  if(!o||!Array.isArray(states))throw Error('Missing national analytics');
  const keys=['source_flock_labeled_points','generic_lpr_points','unknown_manufacturer_points'];
  const nums=keys.map(k=>Number(o[k])),total=Number(o.exact_government_points);
  if(![...nums,total].every(Number.isSafeInteger)||
      nums.some(n=>n<0)||total<0||nums.reduce((a,b)=>a+b,0)!==total)
   throw Error('Original-government manufacturer classification inconsistent');
  const sum=k=>states.reduce((acc,r)=>acc+Number(r[k]),0);
  if(sum('verified_exact_gis_points')!==total||
    keys.some((k,i)=>sum(k)!==nums[i])||
    states.length!==Number(o.states_with_any_documented_evidence))
   throw Error('State and national analytics do not reconcile');
  return true;
 }
 return Object.freeze({read,reconcile,PAGE_SIZE,MAX_PAGES});
});
