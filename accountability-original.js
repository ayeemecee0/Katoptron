/* M6 original government chronology: strictly separate documented original
 * civic statements from direct agreements, individual votes and camera hardware.
 * A council authorization is not an executed agreement or actual expenditure.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronOriginalAccountability=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const TYPES=Object.freeze({
  recorded_governing_body_decision:'recorded_legislative_decision',
  agency_reported_operational_change:'original_operational_change',
  government_disclosure_publication:'original_government_disclosure',
  government_reported_estimate:'original_government_estimate'
 });
 function safeGovernment(url){
  try{
   const p=new URL(url);
   return p.protocol==='https:'&&!p.username&&!p.password&&
    (p.hostname.endsWith('.gov')||p.hostname==='gov')?p.href:null;
  }catch{return null}
 }
 function validDay(value){
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;
  const d=new Date(value+'T00:00:00Z');
  return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===value;
 }
 function normalizeCivic(rows){
  if(!Array.isArray(rows))throw Error('Original government chronology unavailable');
  const result=[];
  for(const row of rows){
   if(!row||row.evidence_tier!=='original_government_reviewed'||
      typeof row.milestone_key!=='string'||!/^[-a-z0-9_]{8,120}$/.test(row.milestone_key)||
      !TYPES[row.event_type]||!safeGovernment(row.source_url)||
      typeof row.jurisdiction_label!=='string'||
      !/,[ ]*[A-Z]{2}$/.test(row.jurisdiction_label)||
      typeof row.summary!=='string'||row.summary.length<20||
      typeof row.title!=='string'||row.title.length<6)continue;
   const documentedDate=row.event_date;
   if(documentedDate===null){
    if(row.date_basis!=='date_not_reported')continue;
   }else if(!validDay(documentedDate)||row.date_basis==='date_not_reported'){
    continue;
   }
   const isEstimate=row.event_type==='government_reported_estimate';
   if(row.amount_usd!=null&&
      (!isEstimate||row.amount_basis!=='government_estimate_not_executed_contract'||
       !Number.isFinite(Number(row.amount_usd))||Number(row.amount_usd)<0))continue;
   if(isEstimate&&row.amount_usd!=null&&row.amount_basis!=='government_estimate_not_executed_contract')continue;
   result.push(Object.freeze({
    event_key:'original_civic:'+row.milestone_key,
    event_type:TYPES[row.event_type],
    evidence_level:'original_government_reviewed',
    jurisdiction_label:row.jurisdiction_label,
    state_code:row.jurisdiction_label.match(/,\s*([A-Z]{2})$/)[1],
    agency_label:null,person_label:null,person_role:null,
    event_date:documentedDate,date_basis:row.date_basis,
    title:row.title,summary:row.summary,source_url:row.source_url,
    source_label:'Original government-reviewed public record',
    amount_usd:isEstimate&&row.amount_usd!=null?Number(row.amount_usd):null,
    camera_count:null
   }));
  }
  return result;
 }
 return Object.freeze({normalizeCivic,safeGovernment});
});
