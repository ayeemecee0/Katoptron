/* Source-attributed, review-status-safe government research dossier.
   Never upgrades a historic agenda, contract proposal or policy PDF to
   a live camera deployment or a newly adopted agreement. */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronGovernmentDocket=api;})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const HOSTS=new Set(['www.lakewoodca.gov','www.sheboyganwi.gov','www.grandrapidsmi.gov','henrico.gov','www.fridleymn.gov','www.richlandwa.gov','www.libertyhilltx.gov','www.elgintexas.gov','www.redmond.gov','www.tukwilawa.gov','ceqanet.lci.ca.gov','www.sacsheriff.com','www.sacda.org','cityofcleveland.legistar.com','elpasotexas.legistar.com','stpaul.legistar.com','allentownpa.legistar.com','carrolltontx.legistar.com','rockfordil.legistar.com','monterey.legistar.com','manteca-ca.legistar.com','ci-ssf-ca.legistar.com','toledo.legistar.com','commerce.legistar.com','www.grotonma.gov','shakerheightsoh.gov','www.cityoflacrosse.org','rec.cityofsunprairie.com','cityofmethuen.net']);
 const STATUSES=new Set(['filed_notice_not_operational_verification','historical_policy_not_verified_current','ordinance_passed_not_executed_contract','council_action_reported_pass_header_discrepancy','council_resolution_adopted_call_for_termination_only','research_contract_authorized_not_flock_vendor_contract','council_item_passed_not_signed_contract','council_approved_sole_source_award','proposed_approval_not_verified_signed','agenda_ready_final_action_unverified','vendor_rfp_recommendation_not_adopted','city_staff_proposed_response_not_final_adoption_verified','proposed_grand_jury_response_resolution_not_legistar_finalized','published_da_data_access_policy_not_flock_equipment','police_department_published_flock_program_statement_not_independent_audit','resolution_held_in_council_not_adopted','ordinance_first_reading_passed_not_final_adoption','government_publisher_announces_contract_termination','government_publisher_reports_signed_contract_amendment','government_publisher_reports_contract_ending_steps','government_publisher_announces_future_nonrenewal','government_publisher_announces_ending_program_removal_pending','government_reported_proposed_agreement_rejected','agency_requests_termination_not_council_adoption','government_publisher_announces_proposed_policy_order_not_verified_issued','agency_reports_alpr_suspension_intent','government_publisher_reports_contract_terminated_and_cameras_removed','agency_reports_alpr_program_paused','council_approved_termination_not_confirmed_cameras_removed','government_reports_amended_contract_approval_not_independent_executed_doc']);
 const KINDS=new Set(['environmental_notice','historic_policy','published_policy','government_decision','contract_proposal','policy_proposal']);
 function validUrl(value){try{const x=new URL(value);return x.protocol==='https:'&&!x.username&&!x.password&&!x.hash&&HOSTS.has(x.hostname)&&!x.port;}catch{return false;}}
 function build(input){
  if(!input||input.schema_version!==1||!Array.isArray(input.sources)||input.sources.length<8||input.sources.length>70)throw Error('Original government docket unavailable');
  const ids=new Set(),rows=[],agencies=new Map();
  for(const s of input.sources){
   if(!s||typeof s.id!=='string'||!/^([a-z0-9]+-){2,}[a-z0-9-]+$/.test(s.id)||ids.has(s.id)||!validUrl(s.source_url)||!STATUSES.has(s.status)||!KINDS.has(s.kind)||!/^20[012][0-9]-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[12][0-9]|3[01]))?$/.test(s.source_date)||!/^[-a-z ]+\|[A-Z]{2}$/.test(s.locality_key)||!s.locality_key.endsWith('|'+s.state)||typeof s.agency!=='string'||s.agency.length<9||typeof s.summary!=='string'||s.summary.length<90||typeof s.proof!=='string'||s.proof.length<25||!Array.isArray(s.open_questions)||s.open_questions.length<1||s.open_questions.length>4||s.open_questions.some(q=>typeof q!=='string'||q.length<20)||s.watch_category!=='historical_research_only'||typeof s.flock_specific!=='boolean'||(s.amount_usd!==null&&(!Number.isFinite(s.amount_usd)||s.amount_usd<=0||!s.amount_basis))){throw Error('Unverified government record held');}
   if(s.id==='sacramento-ca-sheriff-alpr-general-order-2016'&&
      (s.source_date!=='2016-04'||s.flock_specific!==false||
       s.status!=='historical_policy_not_verified_current'))
    throw Error('Historical sheriff policy date or equipment identity drift');
   if((/proposal|agenda_ready|not_executed|research_contract|unsigned|call_for_termination|historical/i.test(s.status))&&/executed agreement confirmed|camera installed and operating/i.test(s.summary))throw Error('Unverified adoption assertion');
   ids.add(s.id);rows.push(Object.freeze({...s}));
   const group=agencies.get(s.locality_key)||[];
   group.push(s);agencies.set(s.locality_key,group);
  }
  rows.sort((a,b)=>b.source_date.localeCompare(a.source_date)||a.id.localeCompare(b.id));
  const states=new Set(rows.map(r=>r.state)),issuers=new Set(rows.map(r=>r.agency));
  return Object.freeze({rows,states:[...states].sort(),agencies:[...agencies.keys()].sort(),issuers:[...issuers].sort(),byLocality:key=>rows.filter(s=>s.locality_key===key),byState:state=>rows.filter(s=>s.state===state),get:id=>rows.find(s=>s.id===id)});
 }
 return Object.freeze({build,validUrl,HOSTS});
});
