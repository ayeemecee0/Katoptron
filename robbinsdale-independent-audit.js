/* Explicit two-source Robbinsdale Flock evidence comparison.
 * 2025 original external audit and separately dated 2026 city FAQ.
 * Never equate vehicle reads, hits, or plate photograph retention periods.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronRobbinsdaleAudit=api;
})(typeof window!=='undefined'?window:null,function(){
'use strict';
const ORIGINAL='https://www.lrl.mn.gov/docs/2025/mandated/251675.pdf';
const SHA='5374d507c1853a37df377cfab5068a24f36df04935b0fd5d66c79a9e3740c010';
const CITY='https://www.robbinsdalemn.gov/389/4240/Automated-License-Plate-Readers-ALPR';
const CITY_HASH='540fe81b203688493e8c5dc467350a2d5fa7aa1f58ded205ff6d17f75a9223a8';
const categories=[
 ['historical_independent_external_equipment_audit',2],
 ['historical_audited_retention_controls',2],
 ['documented_interagency_request_process_not_live_grants',3],
 ['audit_of_alpr_logs_and_policy_procedures',4],
 ['external_auditor_conclusion_scope',5]
];
function verify(audit,agency){
 if(!audit||audit.schema_version!==1||audit.source_url!==ORIGINAL||
   audit.sha256!==SHA||audit.page_count!==5||audit.source_date!=='2025-10-23'||
   audit.audit_period_start!=='2023-11-01'||audit.audit_period_end!=='2025-09-30'||
   audit.auditor!=='Minnesota Security Consortium (MNSec)'||
   audit.agency!=='Robbinsdale Police Department'||audit.state!=='MN'||
   audit.pages_reviewed?.join(',')!=='2,3,4,5'||
   !Array.isArray(audit.findings)||audit.findings.length!==5||
   audit.legal_policy_current_effectiveness_verified!==false||
   audit.current_operating_equipment_verified!==false||
   audit.live_directed_sharing_edges_verified!==0||
   audit.exact_camera_coordinates_added!==0||
   audit.city_2026_source_url!==CITY||
   typeof audit.comparison_note!=='string'||
   !/differing record types and observation dates/.test(audit.comparison_note))
   throw Error('Historical state-archived independent audit source identity or uncertainty changed');
 for(let i=0;i<categories.length;i++){
  const f=audit.findings[i], [category,page]=categories[i];
  if(f?.category!==category||f.page!==page||typeof f.statement!=='string'||
    f.statement.length<145||/2026 current operations are verified/i.test(f.statement))
   throw Error('Independent original PDF page finding cannot be published');
 }
 if(!agency||agency.id!=='robbinsdale-mn'||agency.agency!==audit.agency||
   agency.state!=='MN'||agency.source_url!==CITY||
   agency.original_html_sha256!==CITY_HASH||
   agency.publisher_statement_category!=='agency_reports_flock_use'||
   agency.source_claim_anchors_verified!==true||
   !agency.claim_anchors?.some(s=>/two Flock cameras in Robbinsdale/i.test(s))||
   !agency.claim_anchors?.some(s=>/License plate photos are retained for two years/i.test(s))||
   !agency.claim_anchors?.some(s=>/Total Flock Hits and Hotlist Hits are retained for 30 days/i.test(s))||
   agency.policy_enactment_verified!==false||
   agency.current_camera_operation_independently_verified!==false||
   agency.device_coordinates_individually_verified!==0||
   agency.live_sharing_edges_verified!==0)
   throw Error('2026 Robbinsdale government publication or its retention source anchors changed');
 const findings=audit.findings.map(f=>({...f,original_page:ORIGINAL+'#page='+f.page}));
 return Object.freeze({
  independent_audit:{...audit,findings},
  agency_publisher:agency,
  evidence_period:'2023-11-01 to 2025-09-30',
  historical_equipment:'Auditor-reported two stationary Flock units at time of audit; no mobile units',
  historical_retention:'2025 external auditor checked Flock Vehicle Reads and described a default 30-day retention setting',
  agency_2026_photos:'City FAQ describes license-plate photographs retained two years',
  agency_2026_hits:'City FAQ describes total Flock and hotlist hits retained 30 days',
  identity_resolution:'Both sources name Robbinsdale Police Department, but concern different observation periods and potentially different record classes.',
  comparison_status:'Not established as a contradiction or proof of currently configured record lifecycle',
  confirmed_live_sharing_edges:0,
  confirmed_current_geolocated_camera_points:0,
  new_independently_page_reviewed_historical_audit_documents:1,
  new_individually_reviewed_final_policy_427_versions:0
 });
}
return Object.freeze({verify,ORIGINAL,CITY,SHA});
});
