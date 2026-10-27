/* State-index ALPR audit review candidates. Metadata only: no PDF facts asserted. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronHistoricalCandidates=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const HOST='www.lrl.mn.gov',TIER='state_legislative_registry_index_metadata_only';
 const TITLE_CLASSES=new Set(['flock_named_in_title','unspecified_alpr_title',
   'other_vendor_named_in_title','mixed_or_ambiguous_title']);
 function originalUrl(url){
  try{
   const u=new URL(url);
   const match=/^\/docs\/(20\d{2})\/mandated\/(\d{6})\.pdf$/.exec(u.pathname);
   if(u.protocol!=='https:'||u.host!==HOST||u.username||u.password||u.search||u.hash||!match)return null;
   if(match[1].slice(-2)!==match[2].slice(0,2))return null;
   return u.href;
  }catch{return null;}
 }
 function validDate(s){
  if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
  const date=new Date(s+'T00:00:00Z');
  return !Number.isNaN(date.valueOf())&&date.toISOString().slice(0,10)===s;
 }
 function normalize(value){
  return String(value||'').normalize('NFKC').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function titleHasPhrase(title,phrase){
  const t=normalize(title),p=normalize(phrase);
  return p.length>=5&&(' '+t+' ').includes(' '+p+' ');
 }
 function aliases(name){
  const n=normalize(name),out=[n];
  if(n.endsWith(' police department')&&!n.startsWith('university of ')){
   const stem=n.slice(0,-' police department'.length);
   if(stem.length>=4)out.push(stem+' pd');
  }
  if(n==='university of minnesota police department')out.push('umn police department','umn pd');
  if(n==='woodbury public safety')out.push('woodbury department of public safety');
  return out;
 }
 function verified(r){
  return !!(r&&typeof r==='object'&&originalUrl(r.source_url)&&
   r.source_tier==='original_government_archive_independent_audit_report'&&
   /^[a-f0-9]{64}$/.test(r.content_sha256||'')&&
   typeof r.jurisdiction_key==='string'&&/^[a-z][a-z\s-]*\|MN$/.test(r.jurisdiction_key)&&
   typeof r.agency_name==='string'&&r.agency_name.length>=9&&r.agency_name.length<130&&
   validDate(r.report_date)&&Array.isArray(r.findings)&&r.findings.length>0&&
   Array.isArray(r.pages_reviewed)&&r.pages_reviewed.length>0);
 }
 function official(r){
  if(!r||r.evidence_tier!==TIER||!TITLE_CLASSES.has(r.title_scope))return false;
  const url=originalUrl(r.source_url);
  if(!url||typeof r.report_id!=='string'||!/^[0-9]{2}-[0-9]{4}\.pdf$/.test(r.report_id))return false;
  const m=/\/(\d{6})\.pdf$/.exec(url);
  if(!m||r.report_id.slice(0,2)+r.report_id.slice(3,7)!==m[1])return false;
  if(typeof r.report_title!=='string'||r.report_title.length<18||r.report_title.length>400)return false;
  return r.publication_date==null||validDate(r.publication_date);
 }
 function plan(rows,manifest){
  if(!Array.isArray(rows)||rows.length<1||rows.length>500||
     !manifest||manifest.schema_version!==1||!Array.isArray(manifest.reports)||manifest.reports.length>25)
    throw Error('Incomplete or unbounded original-source inputs');
  if(!rows.every(official))throw Error('Non-official state index metadata');
  const identities=new Map(),reviewed=new Set(),seen=new Set();
  for(const r of manifest.reports){
   if(!verified(r))throw Error('Curated independent source lacks provenance');
   if(reviewed.has(r.source_url))throw Error('Duplicate independently reviewed source');
   reviewed.add(r.source_url);
   const previous=identities.get(r.jurisdiction_key);
   if(previous&&previous.agency_name!==r.agency_name)
    throw Error('Inconsistent exact agency crosswalk');
   identities.set(r.jurisdiction_key,{jurisdiction_key:r.jurisdiction_key,
     agency_name:r.agency_name,patterns:aliases(r.agency_name)});
  }
  const candidates=[];
  for(const r of rows){
   if(seen.has(r.source_url))throw Error('Duplicate original state registry URL');
   seen.add(r.source_url);
   if(reviewed.has(r.source_url))continue;
   const matching=[...identities.values()].filter(a=>a.patterns.some(p=>titleHasPhrase(r.report_title,p)));
   // Multiple agencies in an official title cannot be automatically assigned
   // to a single audited agency, regardless of title order.
   const agency=matching.length===1?matching[0]:null;
   const explicit=r.title_scope==='flock_named_in_title';
   if(!explicit&&!agency)continue;
   const priority=explicit?'P0':r.title_scope==='unspecified_alpr_title'?'P1':'P2';
   const reason=explicit?'Flock explicitly named in registry title':
    r.title_scope==='unspecified_alpr_title'?'Earlier ALPR report title for exact reviewed agency':
    'Different or ambiguous vendor named in exact-agency report title';
   candidates.push({
    report_id:r.report_id,report_title:r.report_title,source_url:r.source_url,
    publication_date:r.publication_date||null,coverage_period:r.coverage_period||'',
    title_scope:r.title_scope,evidence_tier:r.evidence_tier,priority,reason,
    jurisdiction_key:agency?.jurisdiction_key||null,
    matched_agency:agency?.agency_name||null,
    identity_basis:agency?'original_title_exact_curated_agency_phrase':'not_reconciled',
    examination_status:'official_registry_metadata_only_pending_independent_pdf_review'
   });
  }
  const rank={P0:0,P1:1,P2:2};
  candidates.sort((a,b)=>rank[a.priority]-rank[b.priority]||
    (b.publication_date||'').localeCompare(a.publication_date||'')||
    a.source_url.localeCompare(b.source_url));
  return {
   schema_version:1,scope:'state_original_registry_metadata_only',
   scanned_reports:rows.length,curated_reports:reviewed.size,
   matched_reviewed_agencies:identities.size,
   flock_titles_total:rows.filter(r=>r.title_scope==='flock_named_in_title').length,
   flock_titles_unreviewed:candidates.filter(c=>c.title_scope==='flock_named_in_title').length,
   exact_agency_historical_candidates:candidates.filter(c=>c.jurisdiction_key&&c.title_scope!=='flock_named_in_title').length,
   candidates
  };
 }
 return {plan,originalUrl,titleHasPhrase,aliases,official,verified};
});
