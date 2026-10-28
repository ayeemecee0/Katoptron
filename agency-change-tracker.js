/* Source-qualified policy/contract/decision change events, never generic document counts.
 * Cites exact original government pages and preserves draft vs adopted status.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronChangeTracker=api;
})(typeof window!=='undefined'?window:null,function(){
'use strict';
const RESOLUTION='8173fcdc45105478522251a8a5d745ca4145767d438d4de91d4811e50907fc5a';
const URL='https://www.apachejunctionaz.gov/DocumentCenter/View/33562/RES-26-43';
function events(model,source){
 if(!model||!Array.isArray(model.transitions)||model.transitions.length!==3)
  throw Error('Verified before/after source intelligence absent');
 const originals=model.transitions.map(t=>({
  ...t,source_type:'individually_source_page_reviewed',
  verified_policy_effectiveness:false,
  actual_device_or_platform_configuration_verified:false
 }));
 const r=source?.apacheResolution;
 const gov=source?.adoption;
 if(!r||r.id!=='apache-junction-resolution-26-43-signed-chapter-17'||
  r.source_url!==URL||r.original_sha256!==RESOLUTION||r.original_pdf_pages!==5||
  r.signed_resolution_adoption_date!=='2026-10-06'||
  r.notices_table_resolution_date!=='2026-10-08'||
  r.legal_effective_date_verified!==false||
  r.original_council_agenda_appendix_exact_match_verified!==false||
  r.exact_camera_points_added!==0||
  !Array.isArray(r.findings)||r.findings.length!==5||
  !r.findings.some(x=>x.page===4&&x.statement.includes('30-consecutive-calendar-day')))
  throw Error('Signed resolution text or date boundaries not verified');
 const action=gov?.records?.find(x=>x.id==='apache-junction-az-ordinance-1579-adopted-2026-10-06');
 if(gov?.schema_version!==1||!action||
    action.status!=='adopted_government_original_notice'||
    action.event_date!=='2026-10-06'||action.effective_date!==null||
    action.jurisdiction!=='Apache Junction, AZ')
  throw Error('Ordinance adoption status not grounded');
 originals.push({
  id:'apache-junction-adopted-resolution-with-chapter',
  agency_key:'apache-junction-city-az',state:'AZ',agency_name:'Apache Junction City Council',
  kind:'authenticated_signed_resolution_attachment',status:'adopted_reference_document_with_date_conflict',
  title:'Adopted resolution attachment adds official Chapter 17 source to earlier agenda proposal',
  event_date:'2026-10-06',date_basis:'signed_resolution_page_date_with_conflicting_city_index',
  before:'Before the signed original was acquired, only the earlier Council agenda Chapter 17 attachment was verified; an agenda attachment does not alone prove adopted text.',
  after:'The City Clerk original signed Resolution 26-43 includes a three-page Chapter 17 attachment. Its signature reads October 6; the Clerk notices listing reads October 8. A full text-level match to the earlier agenda draft and the independent legal effective date remain unresolved.',
  substantive:true,source_type:'signed_city_clerk_original_SHA_verified',
  verified_policy_effectiveness:false,actual_device_or_platform_configuration_verified:false,
  sources:[{label:'City Clerk signed resolution, page 2',url:URL+'#page=2',sha:RESOLUTION},
   {label:'Attached original Chapter 17, page 4',url:URL+'#page=4',sha:RESOLUTION},
   {label:'Original Chapter 17, page 5',url:URL+'#page=5',sha:RESOLUTION}],
  alert_category:'government_decision'
 });
 const ids=new Set(),valid=new Set(['executed_contract_status_change','unadopted_policy_proposal','signed_contract_amendment','authenticated_signed_resolution_attachment']);
 for(const t of originals){
  if(ids.has(t.id)||!valid.has(t.kind)||t.verified_policy_effectiveness!==false||
    t.actual_device_or_platform_configuration_verified!==false||
    !Array.isArray(t.sources)||!t.sources.length||
    !t.sources.every(s=>typeof s.url==='string'&&/^https:\/\//.test(s.url)&&/^[a-f0-9]{64}$/.test(s.sha)))
   throw Error('Original-source change status cannot be promoted');
  ids.add(t.id);
 }
 return Object.freeze(originals.sort((a,b)=>(b.event_date||'').localeCompare(a.event_date||'')));
}
return Object.freeze({events});
});
