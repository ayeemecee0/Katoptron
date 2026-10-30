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
 const [sources,held,diffs,policy,workflows,alternates,alternateReceipts,requests,approvals,priorities,historicalSnapshot,historicalLeads]=await Promise.all([
  get('editorial-originals-intelligence-batch-2026-10-29.json'),
  get('nationwide-19-held-original-government-source-recovery-2026-10-29.json'),
  get('current-source-version-hash-review-workplan-2026-10-29.json'),
  get('naperville-paired-policy-clause-revisions-2026-10-29.json'),
  get('investigation-original-source-workflow-verification-2026-10-29.json'),
  get('nationwide-original-government-recovery-alternates-2026-10-29.json'),
  get('nationwide-alternate-source-retrieval-receipts-2026-10-29.json'),
  get('investigative-government-request-outcomes-2026-10-29.json'),
  get('naperville-independent-editorial-approval-queue-2026-10-29.json'),
  get('source-value-acquisition-priorities-2026-10-29.json'),
  get('historical-source-verified-snapshot-2026-10-30.json'),
  get('historical-government-original-issuer-investigation-leads-2026-10-30.json')]);
 if(sources.schema_version!==1||sources.sources.length!==14||
  held.resolutions.length!==19||diffs.sources.length!==38||
  diffs.approved_substantive_document_version_differences!==0||
  policy.changes.length!==10||policy.count_distinct_document_pairs!==1||
  policy.independent_human_signed_off!==0||workflows.workflows.length!==10||alternates.originals.length!==6||alternateReceipts.receipts.length!==6||alternateReceipts.original_held_recovered!==0||requests.requests.length!==6||approvals.items.length!==10||approvals.independent_editor_approved!==0||priorities.current_monitored_unique_urls!==134||
  historicalSnapshot.original_historical_count!==19||historicalSnapshot.cases.length!==19||
  historicalSnapshot.original_historical_recovered!==4||
  historicalSnapshot.original_historical_held!==15||
  historicalLeads.research_leads.length!==8||
  historicalLeads.number_of_editorially_approved_new_source_version_differences!==0)

  throw Error('Evidence inventory incomplete or changed without review');
 $('summary').textContent='14 original-issuer research opportunities from the initial docket · '+historicalSnapshot.original_historical_recovered+' of 19 original historical URLs recovered as of '+historicalSnapshot.verified_at.slice(0,10)+' · '+historicalLeads.research_leads.length+' additional source-attributed research leads · 0 new independent source-version approvals';
 $('historicalRecoverySummary').textContent='Historical verification '+historicalSnapshot.verified_at.slice(0,10)+': '+historicalSnapshot.original_historical_recovered+' recovered, '+historicalSnapshot.original_historical_held+' held. '+historicalSnapshot.accessible_urls_at_observation+'/'+historicalSnapshot.monitored_urls_at_observation+' overall original URL retrievals accessible in that snapshot.';
 const latestRun=el($('historicalRecoveryItems'),'p');
 src(latestRun,historicalSnapshot.source_run,'Inspect the exact government-source retrieval CI run and hashes');
 for(const item of historicalSnapshot.cases){
  const d=el($('historicalRecoveryItems'),'details');
  el(d,'summary',item.state+' · '+item.source_id+' · '+(item.verified_original_bytes?'Original retrieved':'Not yet retrieved'));
  el(d,'p','Initial failure: '+item.historical_failure);
  if(item.verified_original_bytes){
   el(d,'p','Source SHA-256: '+item.sha256+(item.pdf_pages?' · '+item.pdf_pages+' PDF pages':''));
  }else{
   el(d,'p','Reason not cleared: '+item.remaining_evidence_limit);
  }
  el(d,'small','Government historical original identity preserved; no equipment operation, contract performance or legal conclusion inferred.');
 }
 $('historicalLeadSummary').textContent=historicalLeads.research_leads.length+' government-issuer statements located through independent original-source review, requiring separate approval and further evidence.';
 for(const lead of historicalLeads.research_leads){
  const art=el($('historicalResearchLeads'),'article');
  el(art,'h3',lead.title);
  el(art,'small',lead.state+' · '+lead.publisher+' · '+(lead.source_date?'Publication date '+lead.source_date:'Original publication date not established'));
  el(art,'p',lead.issuer_stated_fact);
  const link=el(art,'p');src(link,lead.source_url,'Open government issuer publication');
  el(art,'strong','Not yet established');
  el(art,'p',lead.what_remains_unknown);
  el(art,'strong','Next primary evidence');
  el(art,'p',lead.next_government_original);
  el(art,'small','Research-only source attribution. Automated original-byte hash: not verified. No automated Watch event.');
 }
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
  el(c,'small','Source verification is not proof that a case was resolved. Related correspondence should be reconciled using the request tracker.');
 }
 $('workflowStatus').textContent='10 source-check workflows; '+requests.requests.length+' related government requests sent, '+requests.requests.filter(x=>x.status==='acknowledged').length+' acknowledgments at the dated record review. No substantive responses or independently closed findings verified.';
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
 $('alternateStatus').textContent=alternateReceipts.alternate_sources_accessible+' of '+alternates.originals.length+' official issuer alternate URLs in the original dated review accessible; '+historicalSnapshot.original_historical_recovered+' original historical sources were subsequently recovered in the source-monitor verification.';
 for(const item of held.resolutions){
  const d=el($('heldCards'),'details');el(d,'summary',item.state+' · '+item.source_id+' · '+item.monitor_status);
  el(d,'p',item.next_action);el(d,'p','Evidence limit: '+item.evidence_limit);
  const verified=historicalSnapshot.cases.find(c=>c.source_id===item.source_id);
  el(d,'small',verified?.verified_original_bytes?'Recovered since the initial historical hold as of '+historicalSnapshot.verified_at.slice(0,10):'Original remained unresolved at the last verified recovery snapshot.');
  if(item.alternate_url){const p=el(d,'p');src(p,item.alternate_url,'Official alternative/source link')}
 }
 for(const c of diffs.sources){
  const d=el($('diffCards'),'details');el(d,'summary',c.source_id+' · NO approved page-cited difference');
  el(d,'p',c.status);
  const list=el(d,'ol');for(const step of c.review_actions)el(list,'li',step);
 }
}catch(error){$('summary').textContent='Source verification unavailable: '+error.message;}
})();