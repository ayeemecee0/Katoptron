/* Katoptron original-source agency dossier cross-index.
 * Exact agency IDs and existing source-page-verified ledgers ONLY.
 * Never merge an agency with a locality, vendor portal, or camera count by name.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronVerifiedAgencyDossiers=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const AGENCIES=[
  ['oklahoma-city-ok','Oklahoma City','Oklahoma City','OK','contract_and_council'],
  ['dakota-county-sheriff-ne',"Dakota County Sheriff's Office","Dakota County Sheriff's Office",'NE','agency_authored_aggregate'],
  ['providence-police-ri','Providence Police Department','Providence Police Department','RI','effective_policy'],
  ['brookings-police-sd','Brookings Police Department','Brookings Police Department','SD','signed_policy_revision'],
  ['kittitas-police-wa','Kittitas Police Department','Kittitas Police Department','WA','draft_not_adopted'],
  ['moline-police-il','Moline Police Department','Moline Police Department','IL','signed_order_and_pause'],
  ['green-bay-police-wi','Green Bay Police Department','Green Bay Police Department','WI','dated_report_published_policy_and_unadopted_draft']
 ];
 function checkUrl(url){
  if(typeof url!=='string'||url.length>1100)return false;
  try{const u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password&&!u.hash;}catch{return false;}
 }
 function catalog(raw,api){
  if(!raw||!api||!raw.okc||!raw.ne||!raw.riSd||!raw.kittitas||
   !raw.waRegistry||!raw.waHeld||!raw.national||
   !api.okc?.catalog||!api.ne?.catalog||!api.riSd?.catalog||
   !api.kittitas?.review||!api.national?.catalog)
   throw Error('Original agency dossiers require all original verified source ledgers');
  const okc=api.okc.catalog(raw.okc);
  const ne=api.ne.catalog(raw.ne);
  const policies=api.riSd.catalog(raw.riSd);
  const wa=api.kittitas.review(raw.kittitas,raw.waRegistry.registrations,raw.waHeld.entries);
  const national=api.national.catalog(raw.national);
  const moline=national.filter(r=>r.id==='moline-il-signed-flock-order-2024'||
    r.id==='moline-il-signed-pause-2026');
  const greenBayIds=new Set(['green-bay-wi-monthly-2026','green-bay-wi-policy-may-2026',
    'green-bay-wi-policy-draft-sept-2026','green-bay-wi-flock-order-2025']);
  const greenBay=national.filter(r=>greenBayIds.has(r.id));
  if(policies.length!==2||moline.length!==2||greenBay.length!==4||
    !greenBay.every(r=>r.agency==='Green Bay Police Department'&&r.state==='WI')||
    okc.documents.length!==4||
    ne.document.id!=='ne-dakota-county-sheriff-2025-state-alpr-aggregate'||
    wa.id!=='kittitas-wa-original-four-page-scanned-draft-2026')
   throw Error('Reviewed original agency document set incomplete');
  const rows=new Map(AGENCIES.map(([key,label,agency,state,tier])=>
    [key,{key,label,agency,state,tier,documents:[],notes:[]}]));
  function add(key,{id,title,kind,date,date_basis,date_note=null,source_url,sha,pages,findings,limits}){
   const target=rows.get(key);
   if(!target||typeof id!=='string'||!checkUrl(source_url)||!/^[a-f0-9]{64}$/.test(sha||'')||
    !Array.isArray(pages)||!pages.length||
    !pages.every(p=>Number.isInteger(p)&&p>0&&p<=120)||
    !Array.isArray(findings)||!findings.length||
    !findings.every(f=>pages.includes(f.page)&&typeof f.statement==='string'&&f.statement.length>=50&&
      f.statement.length<=950&&typeof f.category==='string'&&f.category.length>=8)||
    !((/^20\d{2}-\d{2}-\d{2}$/.test(date||'')&&
      ['original_source_date','policy_effective_date','manual_imprint_not_adoption','report_period_end_not_publication'].includes(date_basis))||
      (date===null&&date_basis==='undated_original_not_verified_effective'&&
       typeof date_note==='string'&&date_note.length>=40))||
    typeof limits!=='string'||limits.length<40)
    throw Error('Unpinned original agency page evidence cannot appear in dossier');
   if(Array.from(rows.values()).some(r=>r.documents.some(d=>d.id===id)))
    throw Error('Original agency source linked to multiple unrelated identities');
   target.documents.push({id,title,kind,date,date_basis,date_note,source_url,sha,pages,
    findings,limits,agency:target.agency,state:target.state});
  }
  for(const r of okc.documents)add('oklahoma-city-ok',{
   id:r.id,title:({
    'okc-2026-signed-flock-amendment':'Flock master agreement: executed 2026 federal-access amendment',
    'okc-2026-approved-flock-renewal':'Flock master agreement: approved 2026–2027 renewal',
    'okc-2026-council-staff-memo':'Council staff memorandum: renewal recommendation',
    'okc-2026-city-funds-certificate':'Signed $270,000 availability-of-funds certification'
   })[r.id],kind:r.status,date:r.event_date,date_basis:'original_source_date',
   source_url:r.source_url,sha:r.source_sha256,pages:r.pages_visually_reviewed,
   findings:r.findings.map(f=>({page:f.page,category:f.kind,statement:f.statement})),
   limits:okc.limits
  });
  rows.get('oklahoma-city-ok').notes.push('City self-report: 90 Flock readers, 109 partner organizations, and seven-day default retention as reported August 18, 2026. These are not independently verified operating positions or named sharing permissions.');
  add('dakota-county-sheriff-ne',{id:ne.document.id,
   title:'Agency-submitted 2025 ALPR aggregate, not an independent audit',
   kind:'agency_authored_aggregate_not_equipment_verification',
   date:ne.document.report_end,date_basis:'report_period_end_not_publication',
   source_url:ne.document.source_url,sha:ne.document.source_sha256,
   pages:ne.document.pages_reviewed,
   findings:[{page:1,category:'agency_reported_2025_aggregate',
    statement:'For January 1 through December 31, 2025, Dakota County Sheriff\'s Office reported 43 NCIC confirmed matches, 0 NCIC non-correlated matches, 126 manually entered plate queries, 19 manual-entry confirmed matches, and 1 manual-entry non-correlated match. These are agency-authored aggregate figures, not independently audited arrests, installed Flock devices, individual plate reads or current equipment status.'}],
   limits:ne.document.source_note
  });
  rows.get('dakota-county-sheriff-ne').notes.push('A similarly titled Buffalo County 2025 form was blank and was not promoted into numeric findings.');
  for(const r of policies){
   const key=r.state==='RI'?'providence-police-ri':'brookings-police-sd';
   add(key,{id:r.id,
    title:r.state==='RI'?'General Order 350.05, effective September 2026':'Policy 13D1, chief-signed September 2026 revision',
    kind:r.kind,date:r.source_effective_date,date_basis:'policy_effective_date',
    source_url:r.source_url,sha:r.original_sha256,pages:r.pages_visually_reviewed,
    findings:r.findings.map(f=>({page:f.page,category:f.kind,statement:f.statement})),
    limits:raw.riSd.limits
   });
  }
  add('kittitas-police-wa',{id:wa.id,title:'Original scanned Policy 425, visibly DRAFT on every page',
   kind:wa.document_lifecycle,date:wa.manual_imprint_date,date_basis:'manual_imprint_not_adoption',
   source_url:wa.source_url,sha:wa.original_sha256,pages:wa.reviewed_pages,
   findings:wa.findings.map(f=>({page:f.page,category:f.category,statement:f.statement})),
   limits:wa.limits
  });
  for(const r of moline)add('moline-police-il',{id:r.id,title:r.title,kind:r.kind,
   date:r.source_date,date_basis:'original_source_date',
   source_url:r.source_url,sha:r.content_sha256,pages:r.pages_reviewed,
   findings:r.findings.map(f=>({page:f.page,category:f.category,statement:f.statement})),
   limits:r.verification_note||'Signed city-published records are historical and do not prove device installation, continuous operation or completion of deactivation.'
  });
  for(const r of greenBay){
   if(['verified_camera_coordinates','operational_status','flock_device_installed',
       'actual_data_access'].some(k=>Object.hasOwn(r,k)))
    throw Error('Green Bay original source cannot assert live device facts');
   add('green-bay-police-wi',{
    id:r.id,title:r.title,kind:r.kind,date:r.source_date,
    date_basis:r.source_date?'original_source_date':'undated_original_not_verified_effective',
    date_note:r.source_date_note||null,source_url:r.source_url,sha:r.content_sha256,
    pages:r.pages_reviewed,findings:r.findings.map(f=>({
     page:f.page,category:f.category,statement:f.statement})),
    limits:raw.national.scope_note
   });
  }
  rows.get('green-bay-police-wi').notes.push(
   'The May 2026 published policy is not verified as the currently effective policy. The September revision is expressly DRAFT and not known to be adopted; the published Flock order form is not independently confirmed executed. The October report gives dated agency-reported aggregates and access recipients, not live camera or sharing verification.');
  const dossiers=Array.from(rows.values());
  for(const r of dossiers){
   if(!r.documents.length)throw Error('Empty original agency dossier');
   r.documents.sort((a,b)=>(b.date||'').localeCompare(a.date||'')||a.id.localeCompare(b.id));
  }
  return {dossiers,agencies:dossiers.length,
    original_documents:dossiers.reduce((n,r)=>n+r.documents.length,0),
    findings:dossiers.reduce((n,r)=>n+r.documents.reduce((m,d)=>m+d.findings.length,0),0),
    no_live_camera_or_sharing_claims:true};
 }
 function byKey(index,key){return index?.dossiers?.find(r=>r.key===key)||null;}
 return {catalog,byKey,checkUrl};
});