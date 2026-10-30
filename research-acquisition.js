(async()=>{
'use strict';
const $=id=>document.getElementById(id);
const el=(parent,tag,value)=>{
 const node=document.createElement(tag);
 if(value!=null)node.textContent=String(value);
 parent.append(node);return node;
};
const src=(parent,url,label,page)=>{
 try{const u=new URL(url);if(u.protocol!=='https:'||u.username||u.password)throw Error('Unsafe URL');
  const a=el(parent,'a',label);a.href=u.href+(Number.isInteger(page)&&page>0?'#page='+page:'');
  a.target='_blank';a.rel='noopener noreferrer';return a;
 }catch{return el(parent,'span','Original source link held')}
};
const get=async name=>{
 const r=await fetch('./data/'+name,{cache:'no-store',referrerPolicy:'no-referrer'});
 if(!r.ok)throw Error('Source evidence HTTP '+r.status);
 return r.json();
};
try{
 const [sources,held,diffs]=await Promise.all([
  get('editorial-originals-intelligence-batch-2026-10-29.json'),
  get('nationwide-19-held-original-government-source-recovery-2026-10-29.json'),
  get('current-source-version-hash-review-workplan-2026-10-29.json')]);
 if(sources.schema_version!==1||sources.sources.length!==14||
  held.resolutions.length!==19||diffs.sources.length!==38||
  diffs.approved_substantive_document_version_differences!==0)
  throw Error('Evidence inventory incomplete or changed without review');
 $('summary').textContent='14 source-backed research opportunities · 13 new monitored government URLs · 19 retrieval holds dispositioned · 38 authenticated source-byte pairs · 0 approved prior/new source-version wording differences';
 function showLeads(){
  const q=$('searchLeads').value.trim().toLowerCase();
  $('leadCards').replaceChildren();
  let shown=0;
  for(const s of sources.sources){
   if(![s.title,s.agency,s.topic,s.claim,s.unresolved_question].join(' ').toLowerCase().includes(q))continue;
   shown++;
   const card=el($('leadCards'),'article');
   el(card,'h3',s.title);
   el(card,'small',s.state+' · '+s.agency+' · original date '+s.source_date+' ('+s.source_date_type+')');
   el(card,'p',s.claim);
   el(card,'strong','Not established');
   el(card,'p',s.unresolved_question);
   el(card,'strong','Next independent verification');
   el(card,'p',s.next_verification_action);
   el(card,'strong','Records request to prepare (unsent)');
   el(card,'p',s.next_records_request);
   const p=el(card,'p');src(p,s.source_url,'Open original government publication',s.source_page);
   el(card,'small','Evidence class: '+s.evidence_tier+' · historical research starter; no verified version change');
  }
  if(!shown)el($('leadCards'),'p','No matching original-government research leads.');
 }
 $('searchLeads').addEventListener('input',showLeads);showLeads();
 for(const item of held.resolutions){
  const d=el($('heldCards'),'details');el(d,'summary',item.state+' · '+item.source_id+' · '+item.monitor_status);
  el(d,'p',item.next_action);el(d,'p','Evidence limit: '+item.evidence_limit);
  el(d,'small','Automatic monitor still held; original source retained.');
  if(item.alternate_url){const p=el(d,'p');src(p,item.alternate_url,'Official alternative/source link')}
 }
 for(const c of diffs.sources){
  const d=el($('diffCards'),'details');el(d,'summary',c.source_id+' · NO approved page-cited difference');
  el(d,'p',c.status);
  const list=el(d,'ol');for(const step of c.review_actions)el(list,'li',step);
 }
}catch(error){$('summary').textContent='Source verification unavailable: '+error.message;}
})();