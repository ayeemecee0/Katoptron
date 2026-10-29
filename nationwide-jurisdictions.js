/* All-51 US state/D.C. original-government publisher index. A monitored link
 * is not Flock camera evidence, installed equipment, or statewide completeness.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronNationwideJurisdictions=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const STATES='AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split(' ');
 const existingRoles=new Set(['police_department','government_independent_oversight','government_legal_authority']);
 function safe(url){
  if(typeof url!=='string'||url.length>950||/%2e|\\|\/\.\.?\//i.test(url.split('?')[0]))return null;
  try{
   const u=new URL(url);
   if(u.protocol!=='https:'||!(u.hostname.endsWith('.gov')||u.hostname==='www.state.wv.us'||['www.moline.il.us','www.naperville.il.us','www.darien.il.us'].includes(u.hostname))||u.host!==u.hostname||
      !!u.username||!!u.password||!!u.hash||u.pathname.length<2||u.search.length>192)return null;
   return url;
  }catch{return null;}
 }
 function catalog(reg,old){
  if(!reg||reg.schema_version!==1||reg.universe!=='50_us_states_plus_district_of_columbia'||
    typeof reg.policy!=='string'||!reg.policy.includes('NOT verified Flock cameras')||
    !Array.isArray(reg.jurisdictions)||reg.jurisdictions.length!==51||
    !Array.isArray(reg.official_seed_sources)||reg.official_seed_sources.length<40||
    !old||old.schema_version!==1||!Array.isArray(old.sources)||
    old.sources.length<8||old.sources.length>25)
   throw Error('National source coverage registry not authentic');
  const byState=new Map(STATES.map(s=>[s,{state:s,name:null,seeds:[],existing:[]}]));
  const seen=new Set(),ids=new Set();
  for(const row of reg.jurisdictions){
   if(!byState.has(row.state)||seen.has(row.state)||
      typeof row.name!=='string'||row.name.length<3||row.name.length>24||
      row.discovery_status!=='enrolled_state_research_queue'||
      row.original_sources_expected!=='not_complete_state_agency_census'||
      !Array.isArray(row.search_terms)||row.search_terms.length!==2)
    throw Error('Missing or false 50-state plus DC research enrollment');
   seen.add(row.state);byState.get(row.state).name=row.name;
  }
  if(seen.size!==51)throw Error('Nationwide jurisdiction census incomplete');
  for(const src of reg.official_seed_sources){
   if(!byState.has(src.state)||typeof src.id!=='string'||ids.has(src.id)||
     !/^[a-z]{2}-[a-z0-9-]{9,95}$/.test(src.id)||
     !['html','pdf'].includes(src.kind)||typeof src.publisher!=='string'||src.publisher.length<10||
     !safe(src.source_url)||
     src.origin_role!=='government_authored_publication_not_independently_page_reviewed'||
     typeof src.evidence_limit!=='string'||!src.evidence_limit.includes('no unverified')||
     ['verified_camera_count','camera_coordinates','flock_installed','live_data_sharing'].some(k=>Object.hasOwn(src,k)))
    throw Error('Unverified or misattributed government original');
   ids.add(src.id);byState.get(src.state).seeds.push(src);
  }
  for(const src of old.sources){
   if(!byState.has(src.state)||!existingRoles.has(src.publisher_role)||
      typeof src.agency!=='string'||src.agency.length<8||!safe(src.url)||
      !Array.isArray(src.allowed_document_hosts)||
      !src.allowed_document_hosts.includes(new URL(src.url).hostname))
    throw Error('Unverified legacy official source index');
   byState.get(src.state).existing.push(src);
  }
  const states=Array.from(byState.values()).sort((a,b)=>a.name.localeCompare(b.name));
  const seeded=states.filter(x=>x.seeds.length+x.existing.length).length;
  return {states,total:51,seeded,without:51-seeded,seedUrls:reg.official_seed_sources.length,
   legacyUrls:old.sources.length,reviewedInstallationsClaimed:0};
 }
 function sourceReceipts(data,registry){
  if(!data||data.schema_version!==1||data.inspected_on!=='2026-10-27'||
   data.scope!=='read_only_original_government_source_metadata_not_individual_flock_evidence'||
   !Array.isArray(data.receipts)||data.receipts.length>registry.official_seed_sources.length||
   typeof data.limitations!=='string'||!data.limitations.includes('not policy adoption'))
   throw Error('Nationwide source receipt metadata invalid');
  const known=new Map(registry.official_seed_sources.map(x=>[x.id,x]));
  const seen=new Set(),receipts=new Map(),counts={accessible:0,held:0};
  const available=new Set(['original_government_pdf_accessible','original_government_html_accessible']);
  const held=new Set(['held_redirect','held_http_error','held_oversized','held_wrong_format',
   'held_unreadable_original','held_timeout_or_network']);
  for(const r of data.receipts){
   const orig=known.get(r?.source_id);
   if(!orig||seen.has(r.source_id)||r.state!==orig.state||r.source_url!==orig.source_url||
    r.kind!==orig.kind||r.authoritatively_verified_document_claims!==false||
    r.flock_equipment_verified!==false||r.camera_coordinates_verified!==false||
    !available.has(r.status)&&!held.has(r.status))
    throw Error('Nationwide original source receipt attribution invalid');
   seen.add(r.source_id);
   if(available.has(r.status)){
    if(!/^[a-f0-9]{64}$/.test(r.sha256_at_observation||'')||
      (r.kind==='pdf'&&(!Number.isInteger(r.page_count_at_observation)||
       r.page_count_at_observation<1||r.page_count_at_observation>120))||
      (r.kind==='html'&&r.page_count_at_observation!==null))
     throw Error('Source original hash or page receipt invalid');
    counts.accessible++;
   }else{
    if(r.sha256_at_observation!==null||r.page_count_at_observation!==null)
     throw Error('Held source cannot claim verified content');
    counts.held++;
   }
   receipts.set(r.source_id,r);
  }
  // Two newly admitted government publisher URLs have not yet produced
  // authenticated retrieval receipts in the pinned 2026-10-27 baseline.
  // Expose them as *pending/unobserved*, never as accessed or verified sources.
  const expectedNew=new Set([
   'ma-groton-municipal-contract-termination-2026',
   'oh-shaker-heights-data-contract-policy-2026'
  ]);
  for(const src of registry.official_seed_sources){
   if(seen.has(src.id))continue;
   if(!expectedNew.has(src.id))
    throw Error('Nationwide official seed source receipts incomplete');
   receipts.set(src.id,{
    source_id:src.id,state:src.state,source_url:src.source_url,kind:src.kind,
    status:'held_new_source_pending_receipt',
    sha256_at_observation:null,page_count_at_observation:null,
    authoritatively_verified_document_claims:false,
    flock_equipment_verified:false,camera_coordinates_verified:false,
    pending_unobserved:true
   });
   counts.held++;
  }
  return {receipts,counts};
 }
 return {catalog,safe,sourceReceipts};
});