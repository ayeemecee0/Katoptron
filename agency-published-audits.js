/* Original agency-authored ALPR reports. Explicitly separate from external audits. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronAgencyPublishedAudits=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const PUB_TYPES=new Set(['agency_authored_audit','agency_internal_audit']);
 function safeUrl(str){
  try{
   if(typeof str!=='string'||str.length>650)return null;
   const u=new URL(str);
   if(u.protocol!=='https:'||u.username||u.password||u.search||u.hash)return null;
   if(u.host==='www.lrl.mn.gov'&&u.pathname==='/docs/2019/mandated/191260.pdf')return u.href;
   if(['www.sanbruno.ca.gov','www.greenbaywi.gov'].includes(u.host)&&
     /^\/DocumentCenter\/View\/[0-9]{3,6}\/[A-Za-z0-9-]{10,160}$/.test(u.pathname))return u.href;
  }catch(_){}
  return null;
 }
 function validDate(s){
  if(s===null)return true;
  if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
  const d=new Date(s+'T00:00:00Z');
  return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===s;
 }
 function valid(report){
  if(!report||typeof report!=='object')return false;
  const r=report;
  return PUB_TYPES.has(r.publisher_type)&&
   typeof r.id==='string'&&/^[a-z0-9-]{8,100}$/.test(r.id)&&
   safeUrl(r.source_url)&&
   ['CA','WI','MN'].includes(r.state)&&
   typeof r.jurisdiction_key==='string'&&r.jurisdiction_key.endsWith('|'+r.state)&&
   typeof r.agency_name==='string'&&r.agency_name.length>=8&&r.agency_name.length<140&&
   typeof r.report_title==='string'&&r.report_title.length>=18&&r.report_title.length<250&&
   /^[a-f0-9]{64}$/.test(r.content_sha256||'')&&validDate(r.source_date)&&
   typeof r.source_date_note==='string'&&r.source_date_note.length>=12&&r.source_date_note.length<500&&
   typeof r.report_scope==='string'&&r.report_scope.length>=14&&r.report_scope.length<600&&
   Array.isArray(r.pages_reviewed)&&r.pages_reviewed.length>0&&r.pages_reviewed.length<=25&&
   r.pages_reviewed.every(p=>Number.isInteger(p)&&p>=1&&p<=25)&&
   Array.isArray(r.findings)&&r.findings.length>0&&r.findings.length<=12&&
   r.findings.every(f=>typeof f.key==='string'&&
     Number.isInteger(f.page)&&r.pages_reviewed.includes(f.page)&&
     typeof f.statement==='string'&&f.statement.length>=40&&f.statement.length<800);
 }
 function catalog(j){
  if(!j||j.schema_version!==1||!Array.isArray(j.reports)||!j.reports.length||j.reports.length>80||
     !j.reports.every(valid))throw Error('Unverified or unbounded government-publisher catalog');
  const seen=new Set(),urls=new Set();
  for(const r of j.reports){
   if(seen.has(r.id)||urls.has(r.source_url))throw Error('Duplicate publisher source');
   seen.add(r.id);urls.add(r.source_url);
  }
  return j.reports.slice().sort((a,b)=>a.state.localeCompare(b.state)||
    a.agency_name.localeCompare(b.agency_name)||
    String(a.source_date||'').localeCompare(String(b.source_date||'')));
 }
 function count(rows){return {reports:rows.length,agencies:new Set(rows.map(r=>r.jurisdiction_key)).size,states:new Set(rows.map(r=>r.state)).size};}
 return {catalog,valid,safeUrl,count};
});
