/* Curated reporting-beat starting dossiers. Inputs must first pass the
 * existing original-government docket verification gate; no prospect names,
 * private outreach metadata, coordinates or new claims are published here.
 */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronPilotDossiers=api;})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const CATALOG=Object.freeze([
  {id:'woodland',key:'woodland|CA',title:'Woodland, California',focus:'Contract, retention policy and oversight',audience:'Local government accountability reporting'},
  {id:'san-diego',key:'san diego|CA',title:'San Diego, California',focus:'Department-reported ALPR audit exceptions',audience:'Police oversight and procurement reporting'},
  {id:'houston',key:'houston|TX',title:'Houston, Texas',focus:'Council authorization versus actual spending',audience:'City contract and expenditure research'},
  {id:'louisville',key:'louisville|KY',title:'Louisville, Kentucky',focus:'Rejected camera-disclosure proposal and unresolved contracts',audience:'Public records and police oversight reporting'},
  {id:'new-hanover',key:'new hanover county|NC',title:'New Hanover County, North Carolina',focus:'Vendor-neutral reader procurement and award questions',audience:'County procurement investigation'},
  {id:'los-angeles',key:'los angeles|CA',title:'Los Angeles, California',focus:'Proposed Flock restrictions versus enacted policy',audience:'City surveillance and legislative reporting'},
  {id:'sacramento',key:'sacramento county|CA',title:'Sacramento County, California',focus:'Historical policy versus current Flock project filings',audience:'Source reconciliation and records research'},
  {id:'pasadena',key:'pasadena|CA',title:'Pasadena, California',focus:'Council oversight request and outstanding contract disclosures',audience:'Municipal committee oversight research'}
 ]);
 const esc=x=>String(x==null?'':x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function build(docket){
  if(!docket||typeof docket.byLocality!=='function')throw Error('Original-government verification gate unavailable');
  return CATALOG.map(p=>{
   const records=docket.byLocality(p.key);
   if(!records.length||records.length>8)throw Error('Curated dossier lacks bounded original evidence: '+p.id);
   for(const s of records)if(s.locality_key!==p.key||s.watch_category!=='historical_research_only'||
    !/^https:\/\//.test(s.source_url)||!s.source_date||!s.status||!Array.isArray(s.open_questions))
    throw Error('Unreviewed dossier source rejected: '+p.id);
   return Object.freeze({...p,records:Object.freeze(records.slice()),questions:Object.freeze([...new Set(records.flatMap(s=>s.open_questions))].slice(0,12))});
  });
 }
 function recordNote(record){
  return ('ORIGINAL-GOVERNMENT SOURCE / REVIEWED HISTORICAL EVIDENCE\n'+
   'Record ID: '+record.id+'\nSource date: '+record.source_date+'\nPublished by: '+record.provider+
   '\nSource status: '+record.status+'\nKind: '+record.kind+'\nTitle: '+record.title+
   '\nDocumented finding (source-attributed, not independently audited operations): '+record.summary+
   '\nVerification basis: '+record.proof+
   (record.amount_usd!==null?'\nPublished amount: $'+record.amount_usd+'; limitation: '+record.amount_basis:'')+
   '\nUnresolved questions:\n'+record.open_questions.map((x,i)=>(i+1)+'. '+x).join('\n')+
   '\nOriginal link: '+record.source_url+
   '\nDo not infer current deployment, payments, data access, signed contract, or enacted policy beyond the stated source.').slice(0,5000);
 }
 function exportHtml(dossier,compiledOn){
  if(!dossier||!Array.isArray(dossier.records)||!dossier.records.length)throw Error('No original-source evidence to export');
  const items=dossier.records.map((s,i)=>'<section><h2>['+(i+1)+'] '+esc(s.title)+'</h2>'+
   '<p><strong>Agency:</strong> '+esc(s.agency)+' · <strong>Source date:</strong> '+esc(s.source_date)+
   ' · <strong>Publisher:</strong> '+esc(s.provider)+'</p>'+
   '<p><strong>Evidence classification:</strong> '+esc(s.kind)+' / '+esc(s.status)+'</p>'+
   '<p><strong>Original-government finding:</strong> '+esc(s.summary)+'</p>'+
   '<p><strong>Verification basis:</strong> '+esc(s.proof)+'</p>'+
   (s.amount_usd!==null?'<p><strong>Document amount:</strong> $'+esc(s.amount_usd)+'; '+esc(s.amount_basis)+'</p>':'')+
   '<p><strong>Inspect original:</strong> <a rel="noopener noreferrer" href="'+esc(s.source_url)+'">'+esc(s.source_url)+'</a></p>'+
   '<h3>Unresolved questions</h3><ol>'+s.open_questions.map(q=>'<li>'+esc(q)+'</li>').join('')+'</ol></section>').join('');
  return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="referrer" content="no-referrer"><title>'+esc(dossier.title)+' | Katoptron original-source brief</title>'+
   '<style>body{font:16px/1.6 system-ui,Arial,sans-serif;max-width:850px;margin:2rem auto;padding:0 1.2rem;color:#16222d}a{overflow-wrap:anywhere}section{border-top:1px solid #aaa;padding:1rem 0}h2{font-size:1.22rem}li{margin:.4rem 0}@media print{body{margin:0;padding:.3in}section{break-inside:avoid}}</style></head><body>'+
   '<h1>'+esc(dossier.title)+'</h1><p><strong>Research focus:</strong> '+esc(dossier.focus)+'</p>'+
   '<p><strong>Original-government records:</strong> '+dossier.records.length+' · <strong>Research index compiled:</strong> '+esc(compiledOn)+'</p>'+
   '<p><strong>Evidence limits:</strong> These are dated publisher records, not a live camera census, independent equipment audit, verified paid invoices or assurance that draft language was enacted. Original links must be rechecked before publication. This document includes no private case data or tracking.</p>'+
   items+'<p>Prepared from Katoptron’s previously reviewed original-government source index. No unverified vendor identity, camera location, current contract or legal conclusion has been added.</p></body></html>';
 }
 return Object.freeze({catalog:CATALOG,build,recordNote,exportHtml});
});
