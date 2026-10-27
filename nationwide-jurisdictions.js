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
   if(u.protocol!=='https:'||!(u.hostname.endsWith('.gov')||u.hostname==='www.state.wv.us')||u.host!==u.hostname||
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
 return {catalog,safe};
});