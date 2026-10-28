/* Original policy-version intelligence. All input must be the previously
 * source-verified Agency X-Ray index. No live surveillance, policy adoption,
 * compliance rating, or automatic change finding is inferred from text.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronPolicyHistory=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const STORAGE='katoptron-policy-history-watch-v1';
 const KINDS=new Set([
  'published_department_policy','draft_policy_unadopted','draft_not_proven_adopted',
  'department_published_effective_general_order',
  'department_published_chief_signed_policy_revision',
  'agency_alpr_policy','state_linked_department_alpr_policy'
 ]);
 const PAIRS=Object.freeze([{
  agency_key:'green-bay-police-wi',
  older:'green-bay-wi-policy-may-2026',
  newer:'green-bay-wi-policy-draft-sept-2026',
  relationship:'published_version_compared_with_unadopted_proposal',
  topic:'ordinary ALPR data retention',
  older_category:'published_policy_retention',
  newer_category:'draft_retention_proposal_not_effective',
  status:'proposed_not_adopted',
  interpretation:'The May published policy describes 30-day ordinary retention. The separately published September draft proposes seven days. The draft is not proof of adoption, of a currently effective policy amendment, or of an implemented database setting.'
 }]);
 function sourcePage(url,page){
  try{const x=new URL(url);
   if(x.protocol!=='https:'||x.username||x.password||x.hash||
      !Number.isInteger(page)||page<1||page>120)return null;
   x.hash='page='+page;return x.href;
  }catch{return null;}
 }
 function catalog(index){
  if(index?.no_live_camera_or_sharing_claims!==true||
     !Array.isArray(index.dossiers)||!index.dossiers.length)
   throw Error('Verified original-government agency index unavailable');
  const agencyKeys=new Set(),ids=new Set(),rows=[];
  for(const agency of index.dossiers){
   if(!/^[a-z0-9-]{8,90}$/.test(agency.key||'')||agencyKeys.has(agency.key)||
      !Array.isArray(agency.documents))throw Error('Unverified original agency identity');
   agencyKeys.add(agency.key);
   const docs=[];
   for(const doc of agency.documents){
    if(!KINDS.has(doc.kind))continue;
    if(ids.has(doc.id)||!/^[0-9a-f]{64}$/.test(doc.sha||'')||
       typeof doc.title!=='string'||!doc.title||
       !['manual_imprint_not_adoption','original_source_date',
         'undated_original_not_verified_effective','policy_effective_date',
         'attorney_general_registration_date_not_policy_date',
         'document_imprint_not_verified_adoption'].includes(doc.date_basis)||
       !(doc.date===null&&doc.date_basis==='undated_original_not_verified_effective'&&
         typeof doc.date_note==='string'&&doc.date_note.length>=40) &&
       !(/^20\d{2}-\d{2}-\d{2}$/.test(doc.date||'')&&
         doc.date_basis!=='undated_original_not_verified_effective')||
       !Array.isArray(doc.pages)||!doc.pages.length||
       !Array.isArray(doc.findings)||!doc.findings.length||
       !doc.findings.every(f=>doc.pages.includes(f.page)&&
         typeof f.category==='string'&&f.category.length>=8&&
         typeof f.statement==='string'&&f.statement.length>=50&&
         sourcePage(doc.source_url,f.page)))
     throw Error('Original policy document not page-source verified');
    ids.add(doc.id);
    docs.push({
     id:doc.id,title:doc.title,kind:doc.kind,date:doc.date,
     date_basis:doc.date_basis,date_note:doc.date_note||null,
     sha:doc.sha,limits:doc.limits,source_url:doc.source_url,
     status:(doc.kind==='draft_policy_unadopted'||doc.kind==='draft_not_proven_adopted')?'draft_unadopted':
      doc.date_basis==='policy_effective_date'?'document_effective_date':
      'published_text_effective_status_unverified',
     findings:doc.findings.map(f=>({page:f.page,category:f.category,
      statement:f.statement,original_page:sourcePage(doc.source_url,f.page)}))
    });
   }
   if(docs.length)rows.push({
    key:agency.key,name:agency.label,state:agency.state,documents:docs.sort((a,b)=>
     (b.date||'').localeCompare(a.date||'')||a.id.localeCompare(b.id))
   });
  }
  const byKey=new Map(rows.map(r=>[r.key,r]));
  const comparisons=[];
  for(const pair of PAIRS){
   const agency=byKey.get(pair.agency_key);
   if(!agency)throw Error('Source-reviewed comparison agency unavailable');
   const old=agency.documents.find(d=>d.id===pair.older);
   const next=agency.documents.find(d=>d.id===pair.newer);
   if(!old||!next||old.kind!=='published_department_policy'||
      next.kind!=='draft_policy_unadopted'||next.date!==null||
      old.date!=='2026-05-04'||
      !/DRAFT/i.test(next.date_note||''))
    throw Error('Proposed policy compared as enacted or original versions changed');
   const oldFinding=old.findings.find(f=>f.category===pair.older_category);
   const newFinding=next.findings.find(f=>f.category===pair.newer_category);
   if(!oldFinding||!newFinding||
      !/30.day maximum/i.test(oldFinding.statement)||
      !/seven days/i.test(newFinding.statement)||
      !/not a verified adopted policy change/i.test(newFinding.statement))
    throw Error('Policy version original-page statements have changed');
   comparisons.push({...pair,agency_name:agency.name,old:{
      id:old.id,date:old.date,date_basis:old.date_basis,statement:oldFinding.statement,
      source_page:oldFinding.original_page,sha:old.sha
    },proposed:{
      id:next.id,date:null,date_note:next.date_note,statement:newFinding.statement,
      source_page:newFinding.original_page,sha:next.sha
    }});
  }
  return {agencies:rows,agency_count:rows.length,
   original_policy_documents:rows.reduce((n,r)=>n+r.documents.length,0),
   comparisons,interpretation:'Only published source text and individually reviewed original PDF pages are shown. This is not an adopted-policy-change census, legal compliance determination, live camera inventory or system configuration.'};
 }
 function sourceTokens(agency){
  return agency.documents.map(d=>d.id+'@'+d.sha).sort();
 }
 function validateStore(raw){
  if(!raw||raw.schema!==1||!Array.isArray(raw.follows)||
     raw.follows.length>15||!raw.seen||typeof raw.seen!=='object'||Array.isArray(raw.seen))
   return {schema:1,follows:[],seen:{}};
  const follows=raw.follows.filter(k=>typeof k==='string'&&/^[a-z0-9-]{8,90}$/.test(k)).slice(0,15);
  const seen={};
  for(const k of follows){
   const v=raw.seen[k];
   seen[k]=Array.isArray(v)?v.filter(t=>typeof t==='string'&&
      /^[a-z0-9-]+@[a-f0-9]{64}$/.test(t)).slice(0,100):[];
  }
  return {schema:1,follows:[...new Set(follows)],seen};
 }
 function follow(state,agency){
  const s=validateStore(state);
  if(!agency||!agency.key||!Array.isArray(agency.documents)||
      (s.follows.length>=15&&!s.follows.includes(agency.key)))
   throw Error('Policy watch limit or agency validation failed');
  if(!s.follows.includes(agency.key)){
   s.follows.push(agency.key);
   s.seen[agency.key]=sourceTokens(agency);
  }
  return s;
 }
 function unwatch(state,key){
  const s=validateStore(state);
  s.follows=s.follows.filter(k=>k!==key);delete s.seen[key];return s;
 }
 function updates(state,agency){
  const s=validateStore(state);
  if(!s.follows.includes(agency?.key))return [];
  const old=new Set(s.seen[agency.key]||[]);
  return agency.documents.filter(d=>!old.has(d.id+'@'+d.sha));
 }
 function markReviewed(state,agency){
  const s=validateStore(state);
  if(!s.follows.includes(agency?.key))return s;
  s.seen[agency.key]=sourceTokens(agency);return s;
 }
 return Object.freeze({catalog,PAIRS,STORAGE,validateStore,follow,
  unwatch,updates,markReviewed,sourcePage});
});
