/* Exact-pinned original government PDF page findings; unlike a city HTML
 * disclosure, these specific policy pages are reverified from original bytes.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronNewStatePolicyOriginals=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const ORIGINALS=Object.freeze({
 'idaho-falls-id-flock-supplemental-procedure-127':{
  sha:'9d53f9a247818cffff263cd18cf2bf0a14ae66ceca20e126578625fd62e8cf60',
  url:'https://www.idahofallsidaho.gov/DocumentCenter/View/20519/Automated-License-Plate-Readers',
  state:'ID',pages:2,
  categories:['flock_policy_system_and_hotlists','flock_alert_independent_reasonable_suspicion',
   'search_reason_and_case_fields','written_retention_and_preservation'],
  page_targets:[1,1,2,2],
  kind:'agency_published_supplemental_Flock_ALPR_procedure_text_not_signed_legal_effective_date'
 },
 'columbia-mo-surveillance-oversight-ordinance-025792':{
  sha:'37e043de9a93a84337e3d9af37b7d4be377476084742832b63aca29353959f48',
  url:'https://www.como.gov/archive/2024/10/ordinance-025792.pdf',
  state:'MO',pages:9,
  categories:['city_surveillance_oversight_enacted_code_text',
   'annual_report_finance_sharing_and_audit_requirements','alpr_explicit_technology_scope',
   'technology_policy_retention_and_location_notification',
   'public_hearing_approval_and_data_sharing',
   'existing_technology_transitional_review','annual_public_report_deadline'],
  page_targets:[1,2,4,6,7,8,9],
  kind:'city_published_surveillance_oversight_ordinance_broader_than_Flock_specific_approval'
 }});
 function validate(raw){
  if(!raw||raw.schema_version!==1||raw.reviewed_on!=='2026-10-27'||
    raw.new_verified_original_PDF_documents!==2||raw.distinct_states!==2||
    raw.exact_camera_points_added!==0||raw.active_sharing_edges_added!==0||
    raw.verified_current_system_settings!==0||
    raw.verified_signed_flock_specific_contracts!==0||
    !Array.isArray(raw.documents)||raw.documents.length!==2)
   throw Error('National first-party original policy page scope altered');
  const found=new Set(),stateSeen=new Set(),documents=[];
  for(const d of raw.documents){
   const source=ORIGINALS[d?.id];
   if(!source||found.has(d.id)||stateSeen.has(d.state)||
      d.state!==source.state||d.url!==source.url||d.sha256!==source.sha||
      d.pages!==source.pages||d.kind!==source.kind||
      d.reviewed_pages?.join(',')!==[...new Set(source.page_targets)].join(',')||
      !Array.isArray(d.findings)||d.findings.length!==source.categories.length||
      typeof d.source_limitations!=='string'||d.source_limitations.length<170||
      d.verified_current_camera_count!==0||d.verified_exact_camera_points!==0||
      d.verified_live_sharing_edges!==0)
    throw Error('Government PDF original source identity or policy claim status changed');
   found.add(d.id);stateSeen.add(d.state);
   const findings=d.findings.map((f,i)=>{
    if(f.category!==source.categories[i]||f.page!==source.page_targets[i]||
      typeof f.statement!=='string'||f.statement.length<145)
     throw Error('Original policy document individual source-page evidence mismatch');
    return {...f,original_page:d.url+'#page='+f.page};
   });
   documents.push({...d,findings});
  }
  if(found.size!==2||stateSeen.size!==2)throw Error('Two distinct state originals not verified');
  return Object.freeze({
   documents,individually_reviewed_original_government_PDFs_added:2,
   distinct_new_state_PDF_governance_records:2,exact_camera_points_added:0,
   verified_current_Flock_sharing_access_edges_added:0,
   source_scope:'Idaho Falls publishes an Flock-specific police procedure; Columbia publishes a general enacted surveillance oversight ordinance listing ALPR, NOT a specific signed Flock vendor contract or live device proof.'
  });
 }
 return Object.freeze({validate,ORIGINALS});
});
