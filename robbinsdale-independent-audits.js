/* Two original independent Minnesota auditor PDFs and dated separate agency FAQ.
 * Never infer present Flock equipment, technical retention or legal violation.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronRobbinsdaleAudits=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const ORIG=[
  {id:'robbinsdale-2025-mnsec-flock-independent-audit',technology:'flock',date:'2025-10-23',
   source:'https://www.lrl.mn.gov/docs/2025/mandated/251675.pdf',
   sha:'5374d507c1853a37df377cfab5068a24f36df04935b0fd5d66c79a9e3740c010',
   kinds:['flock_historical_stationary_equipment','flock_historical_retention_review',
    'flock_access_and_requests','flock_historical_accountability_audit'],
   pages:[2,2,3,4]},
  {id:'robbinsdale-2026-mnsec-axon-independent-audit',technology:'axon',date:'2026-01-29',
   source:'https://www.lrl.mn.gov/docs/2026/mandated/260189.pdf',
   sha:'6e08a704cf379560212c57a9155e4c88c2d0160221e0811bb9e6fbe3ca99751c',
   kinds:['axon_separate_mobile_equipment','axon_separate_retention_review'],pages:[2,2]}
 ];
 const FAQ='https://www.robbinsdalemn.gov/389/4241/Automated-License-Plate-Readers-ALPR';
 function validate(raw){
  if(!raw||raw.schema_version!==1||raw.reviewed_on!=='2026-10-27'||
     raw.agency!=='Robbinsdale Police Department'||raw.state!=='MN'||
     raw.scope!=='independent_historical_Flock_and_separate_AXON_audits_archived_original_PDF_plus_later_department_self_disclosure_not_current_operational_confirmation'||
     !Array.isArray(raw.audit_originals)||raw.audit_originals.length!==2)
   throw Error('Independent audit original ledger unverified');
  const reports=raw.audit_originals.map((d,i)=>{
   const a=ORIG[i];
   if(d.id!==a.id||d.technology!==a.technology||d.audit_date!==a.date||
      d.source_url!==a.source||d.original_sha256!==a.sha||
      d.page_count!==5||d.pages_visually_reviewed?.join(',')!=='1,2,3,4,5'||
      !Array.isArray(d.findings)||d.findings.length!==a.kinds.length||
      d.findings.some((f,k)=>f.kind!==a.kinds[k]||f.page!==a.pages[k]||
       typeof f.statement!=='string'||f.statement.length<155)||
      typeof d.limitations!=='string'||d.limitations.length<150)
    throw Error('Independent audited source hash/page/technology was altered');
   return {...d,findings:d.findings.map(f=>({...f,original_page:a.source+'#page='+f.page}))};
  });
  const d=raw.later_agency_disclosure;
  if(!d||d.source_url!==FAQ||d.as_of!=='2026-08'||
     d.source_type!=='agency_authored_faq_not_independent_external_audit'||
     d.claims?.reported_flock_cameras!==2||
     d.claims?.agency_reported_photo_retention!=='two years'||
     d.claims?.agency_reported_hotlist_hit_retention_days!==30||
     typeof d.scope_note!=='string'||d.scope_note.length<200)
   throw Error('Historical agency FAQ disclosure improperly converted into current independent fact');
  const x=raw.comparison;
  if(!x||x.classification!=='historical_independent_audit_versus_later_agency_self_disclosure_requires_clarification'||
     x.automatic_compliance_finding!==false||
     x.automatic_legal_violation!==false||
     x.current_camera_coordinates_verified!==0||
     typeof x.question!=='string'||x.question.length<100||
     typeof x.limits!=='string'||x.limits.length<150)
   throw Error('Retention discrepancy cannot be classified as proven legal violation');
  return Object.freeze({reports,agency_disclosure:d,comparison:x,
   original_page_reviewed_independent_Flock_audit_count:1,
   axon_audit_technology_distinct:true,
   complete_current_flock_configuration_verified:false,
   new_exact_camera_coordinates:0});
 }
 return Object.freeze({validate,ORIG});
});
