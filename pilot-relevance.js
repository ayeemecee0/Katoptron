/* Public, privacy-preserving editorial research-fit recommendations.
 * Only original-government docket records validated by KatoptronGovernmentDocket
 * are inputs. Score = workflow relevance, NOT evidence strength or wrongdoing.
 * No person names, outreach recipients, browsing identifiers or user profiles saved.
 */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronPilotResearch=api;})(typeof window!=='undefined'?window:null,function(){
'use strict';
const PRESETS=Object.freeze([
 {id:'local_accountability',label:'Local government accountability',description:'City/county approvals, council decisions and oversight',topics:['oversight','contract','procurement'],keywords:['council','ordinance','adopt','decision','audit','approval','meeting']},
 {id:'technology',label:'Technology and investigative reporting',description:'Vendor agreements, procurement and changes to technology use',topics:['contract','procurement','sharing'],keywords:['flock','vendor','amendment','contract','sharing','technology']},
 {id:'civil_liberties',label:'Privacy and civil-liberties research',description:'Published retention, sharing and access policies',topics:['policy','sharing','oversight'],keywords:['retention','privacy','access','sharing','policy','restrictions']},
 {id:'legal',label:'Legal and public-records research',description:'Signed versus proposed actions and missing original documents',topics:['policy','oversight','contract'],keywords:['adopted','signed','draft','resolution','law','ordinance','rights']},
 {id:'public_spending',label:'Procurement and public spending',description:'Authorized spending versus actual payments and signed contracts',topics:['contract','procurement','oversight'],keywords:['spending','amount','invoice','fund','amendment','contract','renewal','lease']}
]);
const COLORS={};
const byId=id=>PRESETS.find(x=>x.id===id)||null;
const esc=v=>String(v===null||v===undefined?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const isOriginal=s=>!!s&&s.watch_category==='historical_research_only'&&typeof s.status==='string'&&
  Array.isArray(s.open_questions)&&s.open_questions.length>0&&/^https:\/\//.test(s.source_url||'')&&/^\d{4}-\d{2}/.test(s.source_date||'');
function group(docket){
 if(!docket||!Array.isArray(docket.rows))throw Error('Validated original-government docket required');
 const groups=new Map();
 for(const r of docket.rows){
  if(!isOriginal(r))throw Error('Unreviewed record cannot enter pilot recommendation engine');
  const array=groups.get(r.locality_key)||[];array.push(r);groups.set(r.locality_key,array);
 }
 return [...groups].map(([locality_key,records])=>Object.freeze({locality_key,records:records.slice().sort((a,b)=>b.source_date.localeCompare(a.source_date)||a.id.localeCompare(b.id))}));
}
function rank(docket,presetId,localityKey='',question=''){
 const preset=byId(presetId);if(!preset)throw Error('Unknown reporter research focus');
 if(typeof question!=='string'||question.length>160)throw Error('Research question exceeds public preview limits');
 if(typeof localityKey!=='string'||localityKey.length>125)throw Error('Invalid agency selection');
 const tokens=(question.toLowerCase().match(/[a-z0-9]{3,}/g)||[]).slice(0,12);
 const results=[];
 for(const g of group(docket)){
  if(localityKey&&g.locality_key!==localityKey)continue;
  const scored=g.records.map(s=>{
   const corpus=[s.title,s.summary,s.kind,s.status,...s.open_questions].join(' ').toLowerCase();
   const matches=preset.keywords.filter(k=>corpus.includes(k));
   const questionMatches=tokens.filter(k=>corpus.includes(k));
   const topicMatches=preset.topics.filter(x=>{
    const v=x==='contract'?/(contract|agreement|renew|lease|amendment)/:x==='procurement'?/(bid|rfp|purchase|fund|award|procure)/:
      x==='policy'?/(policy|retention|ordinance|draft|safeguard)/:x==='sharing'?/(access|sharing|disclosure|federal)/:
      /(council|oversight|audit|resolution|decision|committee)/;
    return v.test(corpus);
   });
   // No use of urgency, scandal, accuracy probability, or unpublished source changes.
   const score=topicMatches.length*12+Math.min(matches.length,5)*3+questionMatches.length*5+
     (s.flock_specific?2:0)+Math.min(s.open_questions.length,4);
   const reasons=[
    topicMatches.length?topicMatches.join(', ')+' topic match':'general government accountability evidence',
    questionMatches.length?questionMatches.length+' matching research-question term(s)':'no specialized question provided',
    s.flock_specific?'publisher explicitly refers to Flock':'vendor identity may be unresolved'
   ];
   return {source:s,score,reasons};
  }).sort((a,b)=>b.score-a.score||b.source.source_date.localeCompare(a.source.source_date)||a.source.id.localeCompare(b.source.id));
  const top=scored.slice(0,3),questions=[...new Set(top.flatMap(x=>x.source.open_questions))].slice(0,8);
  results.push(Object.freeze({locality_key:g.locality_key,preset_id:presetId,score:top.reduce((n,x)=>n+x.score,0),
   documents:g.records.length,selected:top,records:g.records,questions,
   why:'Prioritized by research-topic and question matches, not claim truth, legal culpability or current camera operations.',
   limitation:top.length<3?'Only '+top.length+' original-government record(s) are available for this focus; missing sources are not fabricated.':'Three relevant original-government records are listed. Additional records may exist outside this index.'}));
 }
 return results.sort((a,b)=>b.score-a.score||b.documents-a.documents||a.locality_key.localeCompare(b.locality_key));
}
/* Every proposed next step is attached to reviewed original sources and explicitly
 * requests records IF HELD. This never transmits a request or names a custodian. */
function actionPlan(dossier){
 if(!dossier||!groupKey(dossier.locality_key)||!Array.isArray(dossier.selected)||!dossier.selected.length||
    !Array.isArray(dossier.records)||!dossier.records.length)throw Error('Verified jurisdiction bundle required');
 const chosen=dossier.selected.map(x=>x.source);
 if(chosen.length>3||chosen.some(x=>!isOriginal(x)||x.locality_key!==dossier.locality_key||
    !dossier.records.some(r=>r.id===x.id)))throw Error('Unverified or cross-jurisdiction action rejected');
 const requests=new Set(),roles=new Set(['Public records officer (confirm which agency actually holds each record)']);
 for(const s of chosen){
  const descriptor=[s.kind,s.title,s.status].join(' ').toLowerCase();
  if(/contract|agreement|lease|fund|procure|rfp|spend|payment|amendment/.test(descriptor)){
   roles.add('Procurement or finance records custodian, if applicable');
   requests.add('Final signed agreements and amendments, procurement approvals, and invoices or payment registers related to the cited matter, if any');
  }
  if(/policy|ordinance|retention|access|sharing|safeguard/.test(descriptor)){
   roles.add('Agency policy records custodian, if applicable');
   requests.add('Dated adopted policy versions, prior versions, and documented adoption or approval records for the cited matter, if any');
  }
  if(/council|resolution|meeting|decision|motion|agenda|vote|approval/.test(descriptor)){
   roles.add('City or county clerk / legislative records custodian, if applicable');
   requests.add('Final meeting minutes, official vote or action results, and final resolution or decision records for the cited agenda item, if any');
  }
  if(/environmental|notice/.test(descriptor)){
   requests.add('Final decisions, supporting agency determinations and implementation-status notices corresponding to the cited filing, if any');
  }
 }
 if(!requests.size)requests.add('Final agency records showing disposition or outcome of the cited historical government publication, if any');
 const originalSources=chosen.map(s=>({title:s.title,date:s.source_date,url:s.source_url,agency:s.agency,status:s.status}));
 const lines=[
  'UNSENT PUBLIC-RECORDS REQUEST DRAFT — CONFIRM CUSTODIAN AND SCOPE BEFORE SUBMITTING',
  'To: Public records officer of the responsible government agency (recipient not verified)',
  'Subject: Existing records relating to '+dossier.locality_key+' source-dated government publications',
  '',
  'I request copies of existing, non-exempt public records, if held, associated with the specific dated government publications listed below:',
  ...originalSources.map((s,i)=>String(i+1)+'. '+s.agency+' — '+s.title+' ('+s.date+'; recorded status: '+s.status+')\n   Original: '+s.url),
  '',
  'Please search, as applicable, for:',
  ...[...requests].map((q,i)=>String(i+1)+'. '+q+'.'),
  '',
  'Please advise of any fees before incurring them, provide reasonably segregable portions of responsive records and identify any legal basis for withholding. If a different public office maintains these records, please identify that office if known.',
  'I do not request license plate reads, individual vehicle movements, or private personal information.',
  '',
  'This is a draft only. It has not been submitted. The cited historical publications do not prove an executed contract, current equipment operation, payments, misconduct or a policy taking effect.'
 ];
 return Object.freeze({locality_key:dossier.locality_key,requestDraft:lines.join('\n'),sources:originalSources,
  recordTypes:[...requests],custodianRoles:[...roles],verificationQuestions:dossier.questions.slice()});
}

function pack(dossier){
 if(!dossier||!dossier.selected?.length||!dossier.records?.length)throw Error('No source-verified research bundle');
 const plan=actionPlan(dossier);
 const items=dossier.records.map((r,i)=>{
  if(!isOriginal(r))throw Error('Unreviewed record in bundle');
  return '<section><h2>['+(i+1)+'] '+esc(r.title)+'</h2><p>'+esc(r.agency)+' | '+esc(r.source_date)+
   ' | '+esc(r.status)+' | '+esc(r.kind)+'</p>'+
   '<p><strong>Publisher-attributed finding:</strong> '+esc(r.summary)+'</p>'+
   '<p><strong>Source basis:</strong> '+esc(r.proof)+'</p>'+
   (r.amount_usd!==null?'<p><strong>Stated document amount:</strong> $'+esc(r.amount_usd)+'; '+esc(r.amount_basis)+'</p>':'')+
   '<p><strong>Inspect original:</strong> <a href="'+esc(r.source_url)+'" rel="noopener noreferrer">'+esc(r.source_url)+'</a></p>'+
   '<h3>Unanswered questions</h3><ol>'+r.open_questions.map(q=>'<li>'+esc(q)+'</li>').join('')+'</ol></section>';
 }).join('');
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="referrer" content="no-referrer"><title>Katoptron research starting package</title>'+
  '<style>body{font:16px/1.6 system-ui,Arial,sans-serif;max-width:880px;margin:auto;padding:1.2rem;color:#17212b}section{border-top:1px solid #aebbc2;padding:.9rem 0}a{overflow-wrap:anywhere}@media print{section{break-inside:avoid}}</style></head><body>'+
  '<h1>Original-government research starting package</h1><p><strong>Jurisdiction:</strong> '+esc(dossier.locality_key)+
  ' | <strong>Research focus:</strong> '+esc(byId(dossier.preset_id)?.label||'unspecified')+'</p>'+
  '<p><strong>Evidence boundary:</strong> Historical, source-attributed government documents. Neither the selection score nor missing records demonstrate misconduct, operational equipment, a paid contract, or adopted policy. Original documents and effective dates must be independently checked before publication.</p>'+
  '<p><strong>Indexed original documents:</strong> '+dossier.records.length+
  ' | Selected for first review: '+dossier.selected.length+'. '+esc(dossier.limitation)+'</p>'+
  '<h2>Suggested investigation order</h2><ol>'+dossier.selected.map(x=>'<li>'+esc(x.source.title)+
  ' — '+esc(x.reasons.join('; '))+'</li>').join('')+'</ol>'+
  '<h2>Verification checklist</h2><ol>'+dossier.questions.map(q=>'<li>'+esc(q)+'</li>').join('')+'</ol>'+
  '<h2>Original-source chronology and appendix</h2>'+items+
  '<h2>Source-specific next action</h2><p>Candidate custodian roles (not verified contacts): '+esc(plan.custodianRoles.join('; '))+'</p>'+ 
  '<h3>Unsent records-request draft</h3><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+esc(plan.requestDraft)+'</pre>'+ 
  '<p>Verify the responsible records custodian, date range, available records and applicable local records law before submitting. No request was submitted.</p>'+
  '<p>This is a research starting point, not a completed investigation, legal opinion or finding of wrongdoing. No personal data, plate observations or private case contents included.</p></body></html>';
}
function sharePath(presetId,localityKey){
 if(!byId(presetId)||!groupKey(localityKey))throw Error('Invalid public dossier selection');
 return './pilot-research.html?focus='+encodeURIComponent(presetId)+'&agency='+encodeURIComponent(localityKey);
}
function groupKey(v){return typeof v==='string'&&/^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$/.test(v)}
return Object.freeze({PRESETS,byId,group,rank,actionPlan,pack,sharePath});
});
