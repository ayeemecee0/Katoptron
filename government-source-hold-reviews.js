(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronGovSourceHolds=api;})(typeof window!=='undefined'?window:null,function(){
'use strict';
const EXPECTED=[
{id:'fl-police-operational-status-statement',state:'FL',url:'https://www.pcbfl.gov/m/NewsFlash/Home/Detail/38',status:'still_held_original_unreachable'},
{id:'nc-police-technology-disclosure',state:'NC',url:'https://raleighnc.gov/services/how-does-raleigh-use-flock-cameras',status:'still_held_original_unreachable'},
{id:'co-police-technology-disclosure',state:'CO',url:'https://www.lafayetteco.gov/4282/Flock-Safety-ALPR-Program',status:'superseded_original_government_source_lead'}];
const SHA='5a3e5f2ef5378e76c0b64bdb12ebfa7b2e29e801e6de2c8fbc9343688e320f46';
function verify(data){
 if(!data||data.schema_version!==1||data.observed_on!=='2026-10-27'||
  data.original_baseline_source_holds!==12||data.closed_as_superseded_original!==1||
  data.originals_newly_retrieved_and_sha_verified!==0||
  data.still_unresolved_original_source_items!==11||
  data.source_status_class!=='historical_source_lifecycle_not_independent_current_Flock_equipment_audit'||
  !Array.isArray(data.records)||data.records.length!==3||
  typeof data.notes!=='string'||data.notes.length<240)
  throw Error('Official source-hold lifecycle baseline or review status altered');
 for(let i=0;i<EXPECTED.length;i++){
  const r=data.records[i],x=EXPECTED[i];
  if(r?.id!==x.id||r.state!==x.state||r.original_url!==x.url||
   r.current_disposition!==x.status||r.original_publisher_statement_verified_in_ci!==false||
   r.flock_usage_live_verified!==false||r.confirmed_removal!==false||
   typeof r.review_action!=='string'||r.review_action.length<75)
   throw Error('Government original source hold qualified incorrectly');
  if(i<2){
   if(r.old_status!=='held_http_error'||r.fetch_error!=='HTTPError'||r.newer_verified_url)
    throw Error('Failed original government fetch cannot be labeled source-verified');
  }else if(r.old_status!=='held_redirect'||
   r.newer_verified_url!=='https://www.lafayetteco.gov/m/newsflash/home/detail/10277'||
   r.newer_original_html_sha256!==SHA||
   r.newer_announcement_kind!=='announced_termination_process')
   throw Error('Superseded municipal original source identity changed');
 }
 return Object.freeze({records:data.records,old_source_holds:12,closed_as_superseded:1,
   remains_unresolved:11,new_original_html_sources_hash_verified:0,
   source_status_only:true,
   note:'No current equipment uptime, physical camera removal, present sharing permissions or policy compliance is inferred from these original-source lifecycle checks.'});
}
return Object.freeze({verify,EXPECTED});
});
