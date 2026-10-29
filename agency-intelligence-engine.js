/* Deterministic original-government intelligence. No invented device status,
   dates, expenditures, contract execution, policy adoption or cross-agency links.
   Each item retains the original source and limitations. */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronAgencyIntelligenceEngine=api;})(typeof window!=='undefined'?window:null,function(){
'use strict';
const TOPICS=Object.freeze({
 environmental_notice:'Project filing',
 government_decision:'Government decisions',
 contract_proposal:'Contract or procurement proposal',
 policy_proposal:'Proposed policies',
 historic_policy:'Historical policies',
 published_policy:'Published policies'
});
function safeDate(value){
 if(typeof value!=='string'||!/^20[012]\d-(0[1-9]|1[0-2])(?:-([0-2]\d|3[01]))?$/.test(value))throw Error('Unqualified original source date');
 if(value.length===10&&Number.isNaN(Date.parse(value)))throw Error('Invalid original source date');
 return value;
}
function score(rows){
 // This is a research-gap priority, NOT a claim that agency poses greater risk.
 return rows.reduce((n,x)=>n+x.open_questions.length,0);
}
function build(docket){
 if(!docket||!Array.isArray(docket.rows)||docket.rows.length<15)throw Error('Government source docket missing');
 const byAgency=new Map();
 for(const row of docket.rows){
  if(!row||row.watch_category!=='historical_research_only'||!row.source_url?.startsWith('https://')
   ||!row.agency||!row.state||!Array.isArray(row.open_questions))throw Error('Unreviewed source cannot become verified intelligence');
  const id=row.agency+'|'+row.state;
  const list=byAgency.get(id)||[];list.push(row);byAgency.set(id,list);
 }
 const agencies=[];
 for(const [id,records] of byAgency){
  const rows=records.slice().sort((a,b)=>safeDate(b.source_date).localeCompare(safeDate(a.source_date))||a.id.localeCompare(b.id));
  const questions=[...new Set(rows.flatMap(r=>r.open_questions))].sort();
  const amounts=rows.filter(r=>r.amount_usd!==null&&Number.isFinite(r.amount_usd)&&r.amount_usd>0)
   .map(r=>({value_usd:r.amount_usd,basis:r.amount_basis,source_url:r.source_url,record_id:r.id,
     limitation:'Source-stated amount, not verified payment or aggregate spending.'}));
  const topics={};for(const k of Object.keys(TOPICS))topics[k]=rows.filter(r=>r.kind===k);
  const trace=rows.map(r=>({
   record_id:r.id,source_date:r.source_date,date_precision:r.source_date.length===7?'month':'day',
   label:r.title,source_url:r.source_url,proof:r.proof,issuer:r.agency,status:r.status,kind:r.kind,
   summary:r.summary,source_type:r.source_type,amount_usd:r.amount_usd,amount_basis:r.amount_basis,
   caveat:'The dated government publication does not establish current camera operation or final implementation.'
  }));
  agencies.push(Object.freeze({
   id,agency:rows[0].agency,state:rows[0].state,locality_key:rows[0].locality_key,
   latest_source_date:rows[0].source_date,documents:rows.length,
   unique_original_urls:new Set(rows.map(r=>r.source_url)).size,
   topics,questions,amounts,trace,
   research_gap_count:score(rows),
   historical_only:true,
   has_signed_document_announcement:rows.some(r=>r.status==='government_publisher_reports_signed_contract_amendment'),
   spending_status:amounts.length?'source_amounts_without_payment_verification':'actual_spending_unknown',
   lifecycle_note:rows.length>1?
      'Multiple source dates do not independently prove a change in deployed technology or written policy.':
      'One dated official publication is not a longitudinal change history.'
  }));
 }
 agencies.sort((a,b)=>b.research_gap_count-a.research_gap_count||a.id.localeCompare(b.id));
 return Object.freeze({
  agencies,total_original_documents:docket.rows.length,
  states:[...new Set(agencies.map(a=>a.state))].sort(),
  localities:[...new Set(agencies.map(a=>a.locality_key))].sort(),
  agency_count:agencies.length,
  byRecord:recordId=>agencies.find(a=>a.trace.some(r=>r.record_id===recordId))||null,
  byExactAgency:id=>agencies.find(a=>a.id===id)||null
 });
}
function researchActions(agency){
 if(!agency||!agency.trace?.length)throw Error('Exact source-backed agency required');
 return agency.questions.slice(0,12).map(q=>({
  title:q,
  reason:'Unanswered by the currently cited original-government documents; not evidence of absence.',
  source_url:agency.trace[0].source_url,source_date:agency.latest_source_date
 }));
}
return Object.freeze({build,researchActions,TOPICS,safeDate});
});
