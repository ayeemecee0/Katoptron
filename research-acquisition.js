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
 const [sources,held,diffs,policy,workflows,alternates,alternateReceipts,requests,approvals,priorities]=await Promise.all([
  get('editorial-originals-intelligence-batch-2026-10-29.json'),
  get('nationwide-19-held-original-government-source-recovery-2026-10-29.json'),
  get('current-source-version-hash-review-workplan-2026-10-29.json'),
  get('naperville-paired-policy-clause-revisions-2026-10-29.json'),
  get('investigation-original-source-workflow-verification-2026-10-29.json'),
  get('nationwide-original-government-recovery-alternates-2026-10-29.json'),
  get('nationwide-alternate-source-retrieval-receipts-2026-10-29.json'),
  get('investigative-government-request-outcomes-2026-10-29.json'),
  get('naperville-independent-editorial-approval-queue-2026-10-29.json'),
  get('source-value-acquisition-priorities-2026-10-29.json')]);
 if(sources.schema_version!==1||sources.sources.length!==14||
  held.resolutions.length!==19||diffs.sources.length!==38||
  diffs.approved_substantive_document_version_differences!==0||
  policy.changes.length!==10||policy.count_distinct_document_pairs!==1||
  policy.independent_human_signed_off!==0||workflows.workflows.length!==10||alternates.originals.length!==6||alternateReceipts.receipts.length!==6||alternateReceipts.original_held_recovered!==0||requests.requests.length!==6||approvals.items.length!==10||approvals.independent_editor_approved!==0||priorities.current_monitored_unique_urls!==134)
  throw Error('Evidence inventory incomplete or changed without review');
 $('summary').textContent='14 source-backed research opportunities · 13 new monitored government URLs · 19 retrieval holds dispositioned · 38 authenticated source-byte pairs · 0 approved prior/new source-version wording differences';
 $('editorialApprovalStatus').textContent=approvals.total_clauses+' original-source clauses queued for human independent review; '+approvals.independent_editor_approved+' independently approved. Naperville records request sent; official response pending.';
 for(const q of requests.requests){
  const art=el($('requestOutcomes'),'article');
  el(art,'h3',q.agency);
  el(art,'p',q.requested_records);
  el(art,'small','Submitted: '+q.sent_date+' · Status: '+q.status+' · Agency response verified: '+(q.records_received?'yes':'no')+' · Research time saved: unmeasured');
 }
 $('sourceValueSummary').textContent=priorities.highest_priority_states.length+' underrepresented jurisdictions with just one original monitored government URL. Baseline '+priorities.current_baseline.accessible_urls+'/'+priorities.current_baseline.source_urls+' accessible.';
 for(const st of priorities.highest_priority_states){
  const p=el($('sourceValuePriorities'),'details');
  el(p,'summary',st.state+': '+st.current_original_publisher_urls+' original monitored; priority to acquire two qualified new documents');
  const list=el(p,'ol');for(const check of st.qualification_steps)el(list,'li',check);
 }
 for(const entry of policy.changes){
  const c=el($('policyPairs'),'article');
  el(c,'h3',entry.title);
  el(c,'strong','2025 policy, page '+entry.before_pdf_page);
  el(c,'p',entry.before_summary);
  const b=el(c,'p');src(b,policy.before.url,'Original 2025 PDF, page '+entry.before_pdf_page,entry.before_pdf_page);
  el(c,'strong','2026 policy, page '+entry.after_pdf_page);
  el(c,'p',entry.after_summary);
  const a=el(c,'p');src(a,policy.after.url,'Original 2026 PDF, page '+entry.after_pdf_page,entry.after_pdf_page);
  el(c,'p',entry.substantive_wording_difference);
  el(c,'small','Human editorial sign-off: pending. No legal violation inferred.');
 }
 $('policyPairStatus').textContent='10 source-paired ALPR policy wording comparisons · 2 dated originals · 1 government agency · independent human approvals: 0';
 for(const entry of workflows.workflows){
  const c=el($('workflowCards'),'article');
  el(c,'h3',entry.agency);
  el(c,'p',entry.confirmed_scope);
  el(c,'small','Original research outcome: '+entry.source_verification_tier);
  const l=el(c,'p');src(l,entry.source_url,'Government publisher evidence',entry.source_pdf_page);
  el(c,'strong','Next validation');
  el(c,'p',entry.next_check);
  el(c,'small','Requests submitted: no · Compliance or wrongdoing established: no');
 }
 $('workflowStatus').textContent='10 original sources checked and research tasks advanced; no records requests filed.';
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
 for(const alt of alternates.originals){
  const d=el($('alternateCards'),'details');
  el(d,'summary',alt.state+' · Original issuer alternative for '+alt.source_id);
  el(d,'p',alt.why_relevant);
  const receipt=alternateReceipts.receipts.find(r=>r.source_id===alt.id);
  if(!receipt)throw Error('Missing issuer-alt observation receipt');
  el(d,'p','Live government-original retrieval: '+(receipt.status.startsWith('original_')?'Accessible, SHA-256 fingerprinted':'Still held: '+receipt.status));
  const box=el(d,'p');src(box,alt.source_url,'Inspect alternate original-government publisher page');
  el(d,'small','Original source remains held and preserved; alternate subject equivalence NOT independently confirmed.');
 }
 $('alternateStatus').textContent=alternateReceipts.alternate_sources_accessible+' of '+alternates.originals.length+' official issuer alternative URLs accessible; original 19 held URLs remain held.';
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