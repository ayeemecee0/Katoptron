/* Original-page-reviewed Washington AGO-linked source documents in exact agency dossiers.
 * Flock phrase, policy imprint and historical bulletin are NOT live equipment.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronWAOriginalAgencyDossiers=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const NAMES={
  'arlington-wa-fleet-policy-2026':['arlington-police-wa','Arlington Police Department'],
  'des-moines-wa-flock-search-policy-2026':['des-moines-police-wa','Des Moines Police Department'],
  'federal-way-wa-bulletin-2026':['federal-way-police-wa','Federal Way Police Department'],
  'mukilteo-wa-flock-retention-policy-2026':['mukilteo-police-wa','Mukilteo Police Department'],
  'prosser-wa-flock-transparency-policy-2026':['prosser-police-wa','Prosser Police Department'],
  'sedro-woolley-wa-flock-policy-2026':['sedro-woolley-police-wa','Sedro-Woolley Police Department'],
  'walla-walla-wa-flock-policy-2026':['walla-walla-police-wa','Walla Walla Police Department'],
  'whitman-wa-flock-system-policy-2026':['whitman-sheriff-wa',"Whitman County Sheriff's Office"],
  'auburn-wa-policy-july-2026':['auburn-police-wa','Auburn Police Department'],
  'black-diamond-wa-policy-june-2026':['black-diamond-police-wa','Black Diamond Police Department'],
  'normandy-park-wa-policy-june-2026':['normandy-park-police-wa','Normandy Park Police Department']
 };
 function catalog(raw,api){
  if(!raw||!raw.flock||!raw.other||!raw.registry||!raw.receipts||
   !api?.flock?.catalog||!api?.other?.catalog)
   throw Error('Washington source original reviewer registries unavailable');
  const verified=api.flock.catalog(raw.flock,raw.registry.registrations,raw.receipts.receipts);
  const other=api.other.catalog(raw.other);
  if(verified.documents.length!==8||other.length!==3||
   verified.held?.registry_agency!=='Sultan Police Department'||
   verified.held.publish_document_page_links!==false)
   throw Error('Washington publisher mismatch hold or original document count invalid');
  const originals=[...verified.documents,...other];
  if(originals.length!==Object.keys(NAMES).length)throw Error('WA original source list incomplete');
  const results=[],keys=new Set(),ids=new Set();
  for(const r of originals){
   const id=r.id,expected=Object.prototype.hasOwnProperty.call(NAMES,id)?NAMES[id]:null;
   const name=r.agency_name,date=r.document_imprint_date??r.policy_manual_imprint??r.ago_registration_date;
   const basis=r.document_imprint_date||r.policy_manual_imprint?'document_imprint_not_verified_adoption':'attorney_general_registration_date_not_policy_date';
   const kind=r.policy_kind||'state_linked_department_alpr_policy';
   const pages=r.pages_reviewed;
   const findings=r.findings.map(f=>({
    page:f.page,category:f.category||f.kind||'policy_original_source_observation',
    statement:f.statement
   }));
   const limits=r.evidence_limits||raw.other.scope_limits;
   if(!expected||name!==expected[1]||r.state!=='WA'||keys.has(expected[0])||ids.has(id)||
    !/^20\d\d-\d\d-\d\d$/.test(date||'')||
    !/^[a-f0-9]{64}$/.test(r.content_sha256||'')||
    !Array.isArray(pages)||!pages.length||
    !Array.isArray(findings)||!findings.length||
    !findings.every(f=>pages.includes(f.page)&&typeof f.category==='string'&&
     f.category.length>=8&&typeof f.statement==='string'&&f.statement.length>=80)||
    !/^https:\/\//.test(r.source_url||'')||
    typeof limits!=='string'||limits.length<60||
    ['verified_camera_coordinates','operational_status','flock_device_installed','actual_data_access'].some(k=>Object.hasOwn(r,k)))
    throw Error('Washington identity, original document or Flock fact mismatch');
   keys.add(expected[0]);ids.add(id);
   results.push({
    key:expected[0],label:name,agency:name,state:'WA',
    tier:kind==='agency_training_bulletin'?'historical_agency_training_bulletin_not_current_camera_inventory':
      'state_linked_agency_published_policy_original_not_live_camera_facts',
    documents:[{
      id,title:kind==='agency_training_bulletin'?
        '2026 agency training bulletin, historical and proposed equipment statements':
        'Original state-linked ALPR department policy document',
      kind,date,date_basis:basis,source_url:r.source_url,sha:r.content_sha256,
      pages,findings,limits,agency:name,state:'WA'
    }],
    notes:kind==='agency_training_bulletin'?
     ['Federal Way publication dates an earlier reported location and separate proposed equipment. The bulletin is not proof any individual camera is active today.']:
     ['A policy or Attorney General source listing records published language, not independently verified installation, live sharing, adopted effective date or legal compliance.']
   });
  }
  if(results.length!==11||keys.size!==11)throw Error('Incomplete 11 Washington exact agency source dossiers');
  return results.sort((a,b)=>a.label.localeCompare(b.label));
 }
 function combine(base,wa){
  if(!base||base.agencies!==6||base.original_documents!==10||base.no_live_camera_or_sharing_claims!==true||
   !Array.isArray(wa)||wa.length!==11)throw Error('Cannot join unverified or incomplete original agency datasets');
  const all=[...base.dossiers,...wa],keys=new Set(),ids=new Set(),urls=new Set();
  for(const row of all){
   if(keys.has(row.key)||!row.documents.length)throw Error('Cross-state agency identity collision');
   keys.add(row.key);
   for(const d of row.documents){
    if(ids.has(d.id)||urls.has(d.source_url))throw Error('Cross-agency original source attribution collision');
    ids.add(d.id);urls.add(d.source_url);
   }
  }
  const total=all.reduce((n,x)=>n+x.documents.length,0);
  if(all.length!==17||total!==21)throw Error('Original agency source coverage changed without verification');
  return {dossiers:all.sort((a,b)=>a.label.localeCompare(b.label)||a.state.localeCompare(b.state)),
    agencies:all.length,original_documents:total,
    findings:all.reduce((n,r)=>n+r.documents.reduce((m,d)=>m+d.findings.length,0),0),
    no_live_camera_or_sharing_claims:true};
 }
 return {catalog,combine};
});