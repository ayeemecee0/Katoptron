/* Katoptron: source-dated agency accountability chronology.
 * Separate a dated original-source observation from actual deployment,
 * adopted policy, contract execution, or demonstrated network use.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronTimeline=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const DATE=/^\d{4}-\d{2}-\d{2}$/;
 function date(v){
  const s=String(v||'').slice(0,10);
  if(!DATE.test(s))return null;
  const d=new Date(s+'T00:00:00Z');
  return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s?s:null;
 }
 function safe(url){
  try{const u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password?u.href:null}
  catch{return null}
 }
 function build(group,contracts=[]){
  if(!group||!Array.isArray(group.events)||!Array.isArray(group.portals)||!Array.isArray(group.programs)||!Array.isArray(contracts))
    throw Error('Published agency sources incomplete');
  const dated=[],undated=[],seen=new Set();
  function add(kind,when,title,detail,source,tier,basis,key,scheduled=false){
   const url=safe(source);if(!url)return;
   const id=key||kind+'|'+url+'|'+String(when);
   if(seen.has(id))return;seen.add(id);
   const entry={id,kind,date:date(when),title,detail,source_url:url,tier,date_basis:basis,scheduled};
   (entry.date?dated:undated).push(entry);
  }
  for(const e of group.events){
   const when=e.event_date;
   // A source-dated government PROGRAM is not an adoption date; a signed
   // contract requires an independently reviewed executed agreement.
   let kind='government_record',title=e.title;
   if(e.event_type==='recorded_legislative_decision')kind='recorded_decision';
   if(e.event_type==='executed_contract')kind='contract_execution';
   if(e.event_type==='government_program')kind='program_disclosure';
   add(kind,when,title,e.summary,e.source_url,'original_government',
      e.date_basis||'date_not_established','government:'+e.event_key);
  }
  for(const p of group.programs){
   const detail='Government-reported programme status: '+p.program_status+
    '. This is an observation as of the source date, not necessarily the start or end of operation.';
   add('program_disclosure',p.source_date,'Government program status disclosed',
     detail,p.official_evidence_url,'original_government','source_observation_date','program:'+p.program_key);
  }
  for(const p of group.portals){
   add('vendor_snapshot',p.source_date,'Flock vendor transparency snapshot: '+p.agency_label,
     'Reported retention: '+(p.retention_days==null?'unknown':p.retention_days+' days')+
     '; reported mixed-scope cameras: '+(p.reported_total_cameras??'unknown')+
     '. Vendor statements do not authenticate the present camera inventory.',
     p.portal_url,'original_flock_vendor','source_snapshot_date','vendor:'+p.agency_key+':'+p.source_date);
  }
  const sourceLists=new Map();
  for(const edge of group.originalOutgoing||[]){
   if(!sourceLists.has(edge.source_key))sourceLists.set(edge.source_key,[]);
   sourceLists.get(edge.source_key).push(edge);
  }
  for(const rows of sourceLists.values()){
   const r=rows[0];
   add('sharing_observation',r.source_observed_on,
     'Original publisher listed outward sharing recipients',
     rows.length+' names observed in '+r.publisher_name+' source ('+r.captured_scope+
     '). Historical observation, NOT confirmation of currently active permission, reciprocal access or actual searches.',
     r.source_url,r.source_kind,'source_observation_date','sharing:'+r.source_key);
  }
  const byAgency=new Map();
  for(const r of group.secondaryRetention||[]){
   if(!byAgency.has(r.source_agency_id))byAgency.set(r.source_agency_id,[]);
   byAgency.get(r.source_agency_id).push(r);
  }
  for(const rows of byAgency.values()){
   rows.sort((a,b)=>String(a.observed_on).localeCompare(String(b.observed_on)));
   for(let i=1;i<rows.length;i++){
    const prev=rows[i-1],cur=rows[i];
    if(prev.retention_days==null||cur.retention_days==null||
       prev.retention_days===cur.retention_days)continue;
    add('retention_difference',cur.observed_on,
      'Secondary retention disclosure changed between observations',
      'Licensed secondary source reports '+prev.retention_days+' days on '+prev.observed_on+
       ' and '+cur.retention_days+' days on '+cur.observed_on+
       '. This is NOT independently authenticated current policy or effective date.',
      cur.source_url,'secondary_aggregated_portal_snapshot','secondary_comparison_observation_date',
      'retention:'+cur.source_agency_id+':'+cur.observed_on);
   }
  }
  for(const c of contracts){
   const price=c.amount_usd==null?'amount not reported':'source-documented $'+Number(c.amount_usd).toLocaleString('en-US');
   add('contract_execution',c.signed_on,'Reviewed signed Flock agreement',
     price+'; source-documented contract number: '+(c.contract_number||'unknown'),
     c.source_url,'original_government','signed_date_on_reviewed_agreement','signed:'+c.contract_key);
   if(c.ends_on)
    add('scheduled_contract_end',c.ends_on,'Scheduled contract end date',
     'Source-documented scheduled end only. It does NOT establish renewal, actual termination, or continued operation.',
     c.source_url,'original_government','contract_end_date_in_signed_agreement',
     'end:'+c.contract_key,true);
  }
  dated.sort((a,b)=>b.date.localeCompare(a.date)||a.title.localeCompare(b.title));
  undated.sort((a,b)=>a.title.localeCompare(b.title));
  return {dated,undated};
 }
 function filter(items,kind='all'){
  return kind==='all'?items:items.filter(x=>x.kind===kind);
 }
 async function contractsFor(label){
  const cfg=window.KATOPTRON_CONFIG;
  if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey)throw Error('Original contract evidence unavailable');
  // Only the vetted, signed and published contract view; no discovery leads.
  const q=new URLSearchParams({select:'contract_key,jurisdiction_label,contract_number,signed_on,ends_on,amount_usd,source_url',
    jurisdiction_label:'eq.'+label,limit:'500'});
  const r=await fetch(cfg.supabaseUrl+'/rest/v1/flock_public_signed_contract_end_dates?'+q,
    {headers:{apikey:cfg.supabasePublishableKey},cache:'no-store'});
  if(!r.ok)throw Error('Original signed agreement evidence unavailable: HTTP '+r.status);
  const rows=await r.json();if(!Array.isArray(rows))throw Error('Invalid signed-agreement source');
  return rows;
 }
 return Object.freeze({date,safe,build,filter,contractsFor});
});
