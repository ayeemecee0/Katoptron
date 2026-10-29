/* Exact-government-authority investigation from individually cited, historical original records.
   Multiple municipal agencies within one city must NEVER be silently merged. */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronGovernmentAgencyBrief=api;})(typeof window!=='undefined'?window:null,function(){
'use strict';
function profile(docket,id){
 if(!docket||!Array.isArray(docket.rows))throw Error('Original government docket absent');
 if(typeof id!=='string'||id.length>120)throw Error('Invalid government record identifier');
 const first=docket.get(id);
 if(!first)throw Error('No government original with this identifier');
 const rows=docket.rows.filter(r=>r.agency===first.agency&&r.state===first.state);
 const issues=[...new Set(rows.flatMap(r=>r.open_questions))].slice(0,16);
 return Object.freeze({
  id:first.id,agency:first.agency,locality_key:first.locality_key,state:first.state,
  rows,issues,source_count:new Set(rows.map(r=>r.source_url)).size,
  dated_records:rows.length,
  documented_amounts:rows.filter(r=>Number.isFinite(r.amount_usd)&&r.amount_usd>0),
  has_executed_contract:rows.some(r=>r.status==='government_publisher_reports_signed_contract_amendment'),
  caveat:'Agency-authored original records are source-dated and not proof of current cameras, payment, compliance, or live data access.'
 });
}
function request(profile){
 if(!profile||!profile.rows?.length)throw Error('Source-backed agency profile required');
 const questions=profile.issues;
 const urls=[...new Set(profile.rows.map(r=>r.source_url))];
 return [
  'To: Public Records Officer, '+profile.agency+' ('+profile.state+')',
  'Subject: Public records request concerning Flock Safety / ALPR governance',
  '',
  'I request copies of existing publicly releasable records sufficient to answer:',
  ...questions.map((q,i)=>(i+1)+'. '+q),
  '',
  'Where applicable, please include existing signed vendor agreements and amendments, payments or invoices, publicly approved technology policies, retention and external-access terms, and council actions concerning the documented program.',
  '',
  'I am not requesting individual license plate observations, vehicle-location histories, search logs containing personal information, hotlist entries, or user account credentials.',
  '',
  'Original government records motivating this request:',
  ...urls,
  '',
  'Please provide records electronically and advise of any estimated fees in advance.'
 ].join('\n');
}
return Object.freeze({profile,request});
});
