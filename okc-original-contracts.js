/* Original source-page-reviewed 2026 OKC Flock agreement. No live telemetry. */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronOKCOriginalContracts=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const BASE='https://www.okc.gov/files/assets/city/v/1/police/documents/flock/';
 const SOURCES={
 'okc-2026-signed-flock-amendment':{file:'flock-amendment-august-2026.pdf',sha:'ed37e684252bec2c1938c3f927c777bf34ca67222c11ec86fccbd46da60f9ea0',bytes:259241,pages:2,reviewed:[1,2],type:'signed_city_and_vendor_amendment_original',png:['56acb662b5a723fa42e231f882ff4dd88fe51ce5983018ad1c02d233fccab558','aa3fa98c6f4d32528700484e8a48716dd0bc15853ac70749e598e8a2a8172e30']},
 'okc-2026-approved-flock-renewal':{file:'flock-renewal-letter-august-2026.pdf',sha:'f2aa30d8b38fa8e35a88048d908f62162caaebf28bb12acc7291877ebe0d0ced',bytes:4606970,pages:21,reviewed:[1],type:'city_approved_vendor_concurred_renewal_original',png:['b7b545b579de545bcd26010c9c8fb6499a8db01f4a709f29ac34465f261ee032']},
 'okc-2026-council-staff-memo':{file:'flock-council-memo-august-2026.pdf',sha:'fa6b7b8b81c1816ff5e09668af04d7160055a9385d1a8c844c74a2b174b4501e',bytes:55040,pages:2,reviewed:[1,2],type:'original_staff_recommendation_not_vote_record',png:['d96756c761c0c0d9c5ea931d538d6b001714d02f4c2c68ef568ef42cdea4e385','d53a2598bf5cc5b5255efa43f75dd9d4b1d09e8d414019817416e6889d051e46']},
 'okc-2026-city-funds-certificate':{file:'availability-of-funds-certificate-august-2026.pdf',sha:'1362ab7c9fe7e6902ed51657a616650ce0c6c8569fa553badacfb2be24c91b3c',bytes:161357,pages:1,reviewed:[1],type:'signed_availability_of_funds_certification_not_payment',png:['46616307a268cc99a92d83861efb859000cfb3909a29525e7a463052e7cd2866']}
 };
 const KINDS=new Set(['executed_amendment_federal_access_restrictions','signed_amendment_compelled_process_exception','original_visually_verified_city_and_vendor_execution','approved_city_vendor_annual_renewal','staff_requested_renewal_not_standalone_approval','historical_contract_renewal_sequence','listed_renewal_amount_and_funding','government_sufficient_funds_signed_certification']);
 function catalog(data){
  if(!data||data.schema_version!==1||data.state!=='OK'||data.city!=='Oklahoma City'||
    data.scope!=='visually_reviewed_original_okc_flock_council_contract_documents_no_live_camera_or_sharing_verification'||
    data.city_original_program_page!=='https://www.okc.gov/Services/Public-Safety/Police/Flock-Safety-license-plate-reader-LPR-usage-in-Oklahoma-City'||
    !Array.isArray(data.documents)||data.documents.length!==4||
    typeof data.document_evidence_limits!=='string'||!data.document_evidence_limits.includes('not active platform configuration'))
   throw Error('Original Oklahoma Flock evidence ledger incomplete');
  const seen=new Set();
  for(const d of data.documents){
   const e=SOURCES[d?.id];
   if(!e||seen.has(d.id)||d.status!==e.type||
    d.source_url!==BASE+e.file||d.source_sha256!==e.sha||
    d.source_bytes!==e.bytes||d.pages!==e.pages||
    d.event_date!=='2026-08-18'||JSON.stringify(d.pages_visually_reviewed)!==JSON.stringify(e.reviewed)||
    JSON.stringify(Object.values(d.png_sha256_by_page||{}))!==JSON.stringify(e.png)||
    !Array.isArray(d.findings)||!d.findings.length||
    d.findings.some(f=>!e.reviewed.includes(f.page)||!KINDS.has(f.kind)||
      typeof f.statement!=='string'||f.statement.length<110||f.statement.length>700)||
    ['verified_camera_coordinates','actual_payment_spend_verified','live_flock_network_access_verified','independently_audited_sharing_partners'].some(k=>Object.hasOwn(d,k)))
    throw Error('Oklahoma City document source or legal status improperly promoted');
   seen.add(d.id);
  }
  if(seen.size!==4)throw Error('Missing original Oklahoma agreement evidence');
  const r=data.city_self_report;
  if(!r||r.source_kind!=='city_authored_2026_program_webpage_not_external_independent_audit'||
    r.city_2026_flock_readers_reported!==90||
    r.partner_agencies_reported_as_of_2026_08_18!==109||
    r.reported_default_data_retention_days!==7||
    r.reported_council_vote_date!=='2026-08-18'||
    r.reported_approved_annual_renewal_usd!==270000||
    r.reported_renewal_through!=='2027-06-30'||
    typeof r.interpretation!=='string'||!r.interpretation.includes('not independently measured')||
    data.unreviewed_source_note?.evidence_status!=='original_machine_inspected_presentation_not_independent_program_verification')
   throw Error('City-authored operational self-report changed or independently promoted');
  return {documents:data.documents,cityReport:r,programPage:data.city_original_program_page,
   limits:data.document_evidence_limits};
 }
 return {catalog};
});