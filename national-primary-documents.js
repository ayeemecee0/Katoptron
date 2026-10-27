/* Page-verified, typed government original ALPR policy, draft, report, vendor order
   and independent oversight document evidence. Neither a map nor a live activity feed. */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronNationalPrimaryDocuments=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const TYPES={
 'san-mateo-ca-press-advisory':['official_press_release_derivative','release_summarizes_existing_review_not_independent_new_audit'],
 'austin-tx-auditor-slides':['official_auditor_presentation_derivative','presentation_summarizes_existing_review_not_separate_audit'],
 'green-bay-wi-monthly-2026':['agency_monthly_aggregate_report','publisher_monthly_aggregate_source_not_raw_read_log'],
 'austin-tx-oversight-memo-2023':['original_government_oversight_memo','independent_oversight_concerns_about_2023_proposed_policy'],
 'green-bay-wi-policy-may-2026':['published_department_policy','may_2026_published_policy_no_current_supersession_claim'],
 'green-bay-wi-policy-draft-sept-2026':['draft_policy_unadopted','prominently_marked_draft_not_effective_or_approved'],
 'green-bay-wi-flock-order-2025':['government_published_vendor_order_form','original_published_form_execution_date_not_independently_verified'],
 'austin-tx-commission-recommendation':['advisory_recommendation_not_binding_action','approved_commission_recommendation_not_city_council_order']
 };
 const URLs={
 'san-mateo-ca-press-advisory':'https://sanmateo.courts.ca.gov/system/files/grand-jury/alpr-press-release.pdf',
 'austin-tx-auditor-slides':'https://services.austintexas.gov/edims/document.cfm?id=452702',
 'green-bay-wi-monthly-2026':'https://www.greenbaywi.gov/DocumentCenter/View/18823/Green-Bay-Police-Department-Monthly-ALPR-Report-September-2026',
 'austin-tx-oversight-memo-2023':'https://services.austintexas.gov/edims/document.cfm?id=452776',
 'green-bay-wi-policy-may-2026':'https://www.greenbaywi.gov/DocumentCenter/View/18791/Policy-424-Automated-License-Plate-Readers-ALPR-May-2026',
 'green-bay-wi-policy-draft-sept-2026':'https://www.greenbaywi.gov/DocumentCenter/View/19136/DRAFTED-REVISION---Policy-424-Automated-License-Plate-Readers-ALPR-September-2026',
 'green-bay-wi-flock-order-2025':'https://www.greenbaywi.gov/DocumentCenter/View/19138/Flock-Safety-WI---Green-Bay-PD---DFR-and-ALPR-Law-Enforcement-Agreement-2025',
 'austin-tx-commission-recommendation':'https://services.austintexas.gov/edims/document.cfm?id=452847'
 };
 const ROLES={
 'san-mateo-ca-press-advisory':'government_independent_oversight',
 'austin-tx-auditor-slides':'government_independent_oversight',
 'green-bay-wi-monthly-2026':'police_department',
 'austin-tx-oversight-memo-2023':'government_independent_oversight',
 'green-bay-wi-policy-may-2026':'police_department',
 'green-bay-wi-policy-draft-sept-2026':'police_department',
 'green-bay-wi-flock-order-2025':'police_department',
 'austin-tx-commission-recommendation':'government_advisory_commission'
 };
 const allowed=new Set(Object.values(URLs));
 const LABELS={
 'official_press_release_derivative':'Grand jury press summary, not a new audit',
 'official_auditor_presentation_derivative':'Auditor slides, derivative of existing audit',
 'agency_monthly_aggregate_report':'Agency-reported historical aggregates',
 'original_government_oversight_memo':'Government oversight memorandum',
 'published_department_policy':'Published department policy version',
 'draft_policy_unadopted':'UNADOPTED DRAFT policy proposal',
 'government_published_vendor_order_form':'Published vendor order form, execution unconfirmed',
 'advisory_recommendation_not_binding_action':'Advisory commission vote, not a city order'
 };
 function sourceLink(doc){
  if(!doc||!Object.prototype.hasOwnProperty.call(URLs,doc.id)||doc.source_url!==URLs[doc.id])return null;
  return allowed.has(doc.source_url)?doc.source_url:null;
 }
 function valid(doc){
  if(!doc||typeof doc!=='object'||!sourceLink(doc)||
   !TYPES[doc.id]||doc.kind!==TYPES[doc.id][0]||doc.status!==TYPES[doc.id][1]||doc.publisher_role!==ROLES[doc.id])return false;
  if(!['CA','TX','WI'].includes(doc.state)||typeof doc.agency!=='string'||doc.agency.length<10||
   typeof doc.title!=='string'||doc.title.length<15||
   !/^[a-f0-9]{64}$/.test(doc.content_sha256||'')||
   !Number.isInteger(doc.page_count)||doc.page_count<1||doc.page_count>120||
   !Array.isArray(doc.pages_reviewed)||!doc.pages_reviewed.length||
   !doc.pages_reviewed.every(x=>Number.isInteger(x)&&x>0&&x<=doc.page_count))return false;
  if(doc.source_date!==null &&
    !(typeof doc.source_date==='string'&&/^20\d{2}-\d{2}-\d{2}$/.test(doc.source_date)&&
       !Number.isNaN(Date.parse(doc.source_date))&&new Date(doc.source_date+'T00:00:00Z').toISOString().slice(0,10)===doc.source_date))
   return false;
  if(doc.source_date===null&&(!doc.source_date_note||doc.source_date_note.length<20))return false;
  return Array.isArray(doc.findings)&&doc.findings.length>0&&doc.findings.length<=8&&
   doc.findings.every(f=>doc.pages_reviewed.includes(f.page)&&typeof f.statement==='string'&&f.statement.length>50&&f.statement.length<950);
 }
 function catalog(raw){
  if(!raw||raw.schema_version!==1||!Array.isArray(raw.documents)||raw.documents.length!==8||
   !raw.documents.every(valid)||new Set(raw.documents.map(x=>x.id)).size!==8 ||
   !Array.isArray(raw.source_review_held)||raw.source_review_held.length!==1||
   raw.source_review_held[0].id!=='san-bruno-ca-alpr-policy')
   throw Error('Unverified original government document ledger');
  return raw.documents.slice().sort((a,b)=>a.state.localeCompare(b.state)||a.agency.localeCompare(b.agency)||a.id.localeCompare(b.id));
 }
 function label(x){return LABELS[x]||'Unclassified government source (held)';}
 return {catalog,valid,sourceLink,label};
});
