/* Original-source comparison for Katoptron Agency X-Ray.
 * Compare already individually page-reviewed facts, never infer deployment,
 * actual compliance, policy adoption, installed camera locations or sharing.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronOriginalEvidenceComparison=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const TOPICS=Object.freeze({
  all:'All page-reviewed findings',
  retention:'Written retention and deletion provisions',
  sharing:'Written access and sharing restrictions',
  oversight:'Written audits, oversight and reporting',
  contracts:'Original contract and agreement provisions'
 });
 const MATCH={
  retention:/retention|purge|delet|storag/i,
  sharing:/shar|access|release|federal|immigration|request_approval/i,
  oversight:/audit|oversight|transparency|reporting/i,
  contracts:/contract|amendment|renewal|funds|billing|signed_order|pause_terms|execution_date/i
 };
 function sourcePageUrl(sourceUrl,page){
  try{
   const u=new URL(sourceUrl);
   if(u.protocol!=='https:'||u.username||u.password||u.hash||!Number.isInteger(page)||
      page<1||page>120)return null;
   u.hash='page='+page;
   return u.href;
  }catch{return null;}
 }
 function compare(index,keys,topic='all'){
  if(!Object.prototype.hasOwnProperty.call(TOPICS,topic)||
   !index||index.no_live_camera_or_sharing_claims!==true||
   !Array.isArray(index.dossiers)||!Array.isArray(keys)||
   keys.length<2||keys.length>3||new Set(keys).size!==keys.length)
   throw Error('Comparison requires two or three distinct source-verified agencies');
  const byKey=new Map();
  for(const row of index.dossiers){
   if(typeof row.key!=='string'||!row.key||byKey.has(row.key))
    throw Error('Invalid source agency identity');
   byKey.set(row.key,row);
  }
  const columns=keys.map(key=>{
   const row=byKey.get(key);
   if(!row||!Array.isArray(row.documents)||!row.documents.length)
    throw Error('Unknown or unverified agency');
   const matching=[];
   for(const doc of row.documents){
    if(!doc||typeof doc.id!=='string'||typeof doc.title!=='string'||
       !((/^20\d\d-\d\d-\d\d$/.test(doc.date||'')&&doc.date_basis!=='undated_original_not_verified_effective')||
         (doc.date===null&&doc.date_basis==='undated_original_not_verified_effective'&&
          typeof doc.date_note==='string'&&doc.date_note.length>=40))||
       typeof doc.date_basis!=='string'||typeof doc.limits!=='string'||
       doc.limits.length<40||!Array.isArray(doc.pages)||!doc.pages.length||
       !/^[0-9a-f]{64}$/.test(doc.sha||'')||!Array.isArray(doc.findings)||
       !doc.findings.length)
     throw Error('Unverified document metadata cannot be compared');
    const findings=[];
    for(const f of doc.findings){
     if(!f||!Number.isInteger(f.page)||!doc.pages.includes(f.page)||
        typeof f.category!=='string'||typeof f.statement!=='string'||
        f.statement.length<50||!sourcePageUrl(doc.source_url,f.page))
      throw Error('Unverified original page citation cannot be compared');
     if(topic==='all'||MATCH[topic].test(f.category)){
      findings.push({page:f.page,category:f.category,
       statement:f.statement,source_page_url:sourcePageUrl(doc.source_url,f.page)});
     }
    }
    if(findings.length)matching.push({id:doc.id,title:doc.title,
     kind:doc.kind,date:doc.date,date_basis:doc.date_basis,date_note:doc.date_note||null,sha:doc.sha,
     source_url:doc.source_url,limits:doc.limits,findings});
   }
   return {key:row.key,label:row.label,state:row.state,tier:row.tier,
    total_verified_documents:row.documents.length,documents:matching,
    notes:Array.isArray(row.notes)?row.notes.slice():[]};
  });
  return {topic,topic_label:TOPICS[topic],columns,
   total_matches:columns.reduce((n,c)=>n+c.documents.reduce((m,d)=>m+d.findings.length,0),0),
   evidence_limit:'A topic match is only a source-page-reviewed statement from a specific historical document. No match means no reviewed finding in this catalog, not no policy or cameras. Written requirements do not establish actual practice, live Flock deployment, camera positions or access relationships.'};
 }
 return {TOPICS,compare,sourcePageUrl};
});
