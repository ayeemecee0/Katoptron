/* Reviewed government oversight + official original-document source portals.
 * These are NEVER treated as current camera locations or private ALPR records.
 */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronNationalGovernmentSources=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const reportURLs={
  'san-mateo-ca-2026-grand-jury':'https://sanmateo.courts.ca.gov/system/files/grand-jury/auto-license-plate-readers-report.pdf',
  'austin-tx-2025-city-auditor':'https://services.austintexas.gov/edims/document.cfm?id=452710',
  'woodburn-or-2026-impact-assessment':'https://www.woodburn-or.gov/DocumentCenter/View/3298/Flock-Impact-Assessment-FINAL-2-3-26'
 };
 const roles={
  'san-mateo-ca-2026-grand-jury':'independent_government_oversight',
  'austin-tx-2025-city-auditor':'independent_government_oversight',
  'woodburn-or-2026-impact-assessment':'agency_authored_impact_assessment'
 };
 const officialHosts=new Set(['www.sanbruno.ca.gov','sanmateo.courts.ca.gov','www.paloalto.gov','www.greenbaywi.gov',
  'rva.gov','www.rva.gov','www.austintexas.gov','services.austintexas.gov',
  'attorneygeneral.delaware.gov','www.woodburn-or.gov',
  'www.moline.il.us','www.naperville.il.us','www.darien.il.us','www.atg.wa.gov']);
 function safe(url){
  try{
   if(typeof url!=='string'||url.length>900)return null;
   const u=new URL(url);
   if(u.protocol!=='https:'||!officialHosts.has(u.hostname)||u.host!==u.hostname||u.username||u.password||u.hash)return null;
   if(u.search&&!(u.hostname==='services.austintexas.gov'&&u.pathname==='/edims/document.cfm'&&/^\?id=\d{4,9}$/.test(u.search)))return null;
   if(u.pathname.includes('/../')||u.pathname.includes('\\')||!u.pathname.startsWith('/'))return null;
   return u.href;
  }catch(_){return null;}
 }
 function overview(report){
  if(!report||typeof report!=='object'||reportURLs[report.id]!==report.source_url||
   roles[report.id]!==report.publisher_type||!safe(report.source_url))return false;
  if(!/^[a-f0-9]{64}$/.test(report.content_sha256||'')||
   !['CA','TX','OR'].includes(report.state)||typeof report.agency_name!=='string'||
   report.agency_name.length<10||typeof report.report_title!=='string'||report.report_title.length<15||
   typeof report.report_scope!=='string'||report.report_scope.length<30||
   !Array.isArray(report.pages_reviewed)||!report.pages_reviewed.length||
   !report.pages_reviewed.every(p=>Number.isInteger(p)&&p>=1&&p<=100)||
   !Array.isArray(report.findings)||!report.findings.length||report.findings.length>8)return false;
  if(report.source_date!==null&&
   !(typeof report.source_date==='string'&&/^20\d{2}-\d{2}-\d{2}$/.test(report.source_date)&&
    new Date(report.source_date+'T00:00:00Z').toISOString().slice(0,10)===report.source_date))return false;
  if(report.source_date===null&&
   (typeof report.source_date_note!=='string'||report.source_date_note.length<20))return false;
  return report.findings.every(f=>Number.isInteger(f.page)&&report.pages_reviewed.includes(f.page)&&
   typeof f.statement==='string'&&f.statement.length>=55&&f.statement.length<951);
 }
 function oversightCatalog(obj){
  if(!obj||obj.schema_version!==1||!Array.isArray(obj.reports)||obj.reports.length!==3||
   !obj.reports.every(overview)||new Set(obj.reports.map(x=>x.id)).size!==3)
   throw Error('Incomplete original government oversight verification');
  return obj.reports.slice().sort((a,b)=>a.state.localeCompare(b.state)||a.agency_name.localeCompare(b.agency_name));
 }
 function publisher(p){
  if(!p||typeof p!=='object'||!/^([a-z]{2}-){1}[a-z0-9-]{8,85}$/.test(p.id||'')||
   !['CA','TX','WI','VA','DE','OR','IL','WA'].includes(p.state)||
   !['police_department','government_independent_oversight','government_legal_authority'].includes(p.publisher_role)||
   !['html_index','pdf_original'].includes(p.kind)||typeof p.agency!=='string'||p.agency.length<8||
   !Array.isArray(p.allowed_document_hosts)||!p.allowed_document_hosts.length||
   p.allowed_document_hosts.length>3||!p.allowed_document_hosts.every(x=>officialHosts.has(x)))return false;
  const u=safe(p.url);
  return !!(u&&new URL(u).href===p.url&&p.allowed_document_hosts.includes(new URL(u).hostname));
 }
 function portals(obj){
  if(!obj||obj.schema_version!==1||!Array.isArray(obj.sources)||obj.sources.length<1||
   obj.sources.length>25||!obj.sources.every(publisher)||new Set(obj.sources.map(x=>x.id)).size!==obj.sources.length)
   throw Error('Unverified original government publisher registry');
  return obj.sources.slice().sort((a,b)=>a.state.localeCompare(b.state)||a.agency.localeCompare(b.agency));
 }
 function counts(rows){return {documents:rows.length,agencies:new Set(rows.map(x=>x.jurisdiction_key)).size,
  states:new Set(rows.map(x=>x.state)).size};}
 return {oversightCatalog,portals,overview,publisher,safe,counts};
});
