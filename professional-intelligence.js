/* Five evidence-constrained professional research capabilities.
 * This is not an AI finding generator. It transforms already publisher-reviewed
 * original government records and optionally the separately published Watch feed.
 * "New" is relative to user's opt-in time, never a recycled historical record.
 */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronResearchIntelligence=api;})(typeof window!=='undefined'?window:null,function(){
'use strict';
const TOPICS=Object.freeze(['contract','policy','oversight','sharing','procurement']);
const VERIFIED_KINDS=new Set(['government_decision','contract_document','contract_renewal','policy_original_reviewed','policy_draft_reviewed','retention_changed','sharing_list_changed']);
const validUrl=value=>{try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&u.hostname.length>=5;}catch{return false;}};
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function topics(value){
 const t=(value.kind+' '+value.title+' '+value.summary+' '+value.status).toLowerCase(),out=[];
 if(/contract|agreement|renew|payment|license|spending|amendment/.test(t))out.push('contract');
 if(/retention|policy|ordinance|draft|general order/.test(t))out.push('policy');
 if(/council|oversight|audit|termination|approval|resolution|vote/.test(t))out.push('oversight');
 if(/sharing|access|disclosure|outside agency|federal/.test(t))out.push('sharing');
 if(/procure|bid|rfp|sole.source|purchase|award/.test(t))out.push('procurement');
 return out.length?out:['oversight'];
}
function why(t){
 return ({contract:'Original contract/authorization evidence may reveal obligations or spending questions.',
 policy:'Dated policy evidence may establish a proposed, published or adopted rule, subject to its stated status.',
 oversight:'Government actions and audits may warrant follow-up on oversight and documented decisions.',
 sharing:'Published access/sharing statements may warrant comparison against governing agreements.',
 procurement:'Original procurement documents may clarify vendor selection and authorizations.'})[t]||'Source-dated public record merits verification.';
}
function leadFromDocket(docket){
 if(!docket||!Array.isArray(docket.rows))throw Error('Original-government docket verification required');
 return docket.rows.map(r=>{
  if(r.watch_category!=='historical_research_only'||!validUrl(r.source_url)||!r.source_date||!r.status||
    !Array.isArray(r.open_questions)||!r.open_questions.length)throw Error('Unverified historical source rejected');
  const tag=topics(r)[0];
  return Object.freeze({id:'historic:'+r.id,locality_key:r.locality_key,agency:r.agency,title:r.title,
   summary:r.summary,source_date:r.source_date,observed_at:null,status:r.status,kind:r.kind,
   original_url:r.source_url,source_ids:[r.id],originals:[{title:r.title,url:r.source_url,date:r.source_date,status:r.status,proof:r.proof}],
   topics:topics(r),why:why(tag),unknown:r.open_questions.slice(),
   steps:['Inspect the complete dated government record and its stated action status.',
     ...r.open_questions.slice(0,3).map(q=>'Locate original records establishing: '+q)],
   label:'Historical research lead',fresh:false,verified_scope:'dated_publisher_claim_not_live_system',
   amount:r.amount_usd,amount_basis:r.amount_basis});
 });
}
function leadFromWatch(events){
 if(!Array.isArray(events))throw Error('Published event feed unavailable');
 const seen=new Set(),out=[];
 for(const e of events){
  if(!e||!VERIFIED_KINDS.has(e.kind)||e.evidence_tier!=='original_government'||!validUrl(e.source_url)||
    !/^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$/.test(e.locality_key||'')||
    !/^[a-z0-9_-]{8,160}$/.test(e.event_key||'')||typeof e.title!=='string'||
    typeof e.summary!=='string'||!Number.isFinite(Date.parse(e.observed_at||'')))continue;
  if(seen.has(e.event_key))continue;seen.add(e.event_key);
  const tag=topics({kind:e.kind,title:e.title,summary:e.summary,status:e.kind})[0];
  out.push(Object.freeze({id:'reviewed:'+e.event_key,locality_key:e.locality_key,agency:e.source_agency_id||e.locality_key,
   title:e.title,summary:e.summary,source_date:e.source_date||'source date not established',
   observed_at:e.observed_at,status:e.kind,kind:e.kind,
   original_url:e.source_url,source_ids:[e.event_key],
   originals:[{title:e.title,url:e.source_url,date:e.source_date||'not established',status:e.kind,proof:'Public Watch event labeled original_government'}],
   topics:topics({kind:e.kind,title:e.title,summary:e.summary,status:e.kind}),
   why:why(tag),unknown:[
    'Does the original full document support the published summary and claimed action status?',
    'What subsequent amendments, actions or replies change the interpretation?'
   ],
   steps:['Open and check the original government document, including its effective versus publication date.',
    'Locate the final signed records or governing-body minutes if the published item is only a proposal.',
    'Request redacted public records resolving outstanding contracting, access or spending questions.'],
   label:'Reviewed public Watch record',fresh:false,verified_scope:'published_government_event_not_live_status',
   amount:null,amount_basis:null}));
 }
 return out.sort((a,b)=>Date.parse(b.observed_at)-Date.parse(a.observed_at));
}
function personalize(leads,prefs){
 if(!Array.isArray(leads))throw Error('Source leads required');
 if(!Array.isArray(prefs)||!prefs.length)return {newItems:[],historical:leads.filter(x=>!x.observed_at).slice(0,15),reviewed:leads.filter(x=>x.observed_at).slice(0,15)};
 const valid=prefs.filter(p=>/^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$/.test(p.locality_key||'')&&
   Number.isFinite(Date.parse(p.opted_in_at||'')));
 const matched=leads.filter(l=>valid.some(p=>p.locality_key===l.locality_key &&
   (!Array.isArray(p.topics)||!p.topics.length||l.topics.some(t=>p.topics.includes(t)))&&
   (!p.research_question||p.research_question.length<3||
    (l.title+' '+l.summary+' '+l.topics.join(' ')).toLowerCase().includes(p.research_question.toLowerCase())||
    l.unknown.some(q=>q.toLowerCase().includes(p.research_question.toLowerCase())))));
 const since=l=>valid.some(p=>p.locality_key===l.locality_key&&
   l.observed_at&&Date.parse(l.observed_at)>Date.parse(p.opted_in_at));
 return {newItems:matched.filter(since).slice(0,20),
  historical:matched.filter(l=>!l.observed_at).slice(0,20),
  reviewed:matched.filter(l=>l.observed_at&&!since(l)).slice(0,20)};
}
function compare(docket,reviewedDiffs=[]){
 if(!docket||!Array.isArray(docket.rows))throw Error('Original records unavailable');
 const out=[],byKey=new Map();
 for(const r of docket.rows){const a=byKey.get(r.locality_key)||[];a.push(r);byKey.set(r.locality_key,a);}
 for(const [key,records] of byKey){
  // A missing original document is a research gap, NOT proof of no contract/policy.
  for(const r of records){
   for(const question of r.open_questions.slice(0,2)){
    out.push({id:'gap:'+r.id+':'+question.slice(0,28),type:'missing_evidence',locality_key:key,
     title:'Unresolved source gap: '+r.agency,interpretation:question,
     original_refs:[{url:r.source_url,title:r.title,date:r.source_date,page:null}],
     caveat:'No absence of activity or wrongdoing inferred from missing published evidence.'});
   }
  }
  const sorted=records.filter(r=>/policy|retention|access|sharing/.test((r.title+' '+r.summary+' '+r.kind).toLowerCase()))
   .sort((a,b)=>a.source_date.localeCompare(b.source_date));
  for(let i=1;i<sorted.length;i++){
   const a=sorted[i-1],b=sorted[i];
   if(a.agency!==b.agency||a.source_url===b.source_url)continue;
   out.push({id:'review:'+a.id+':'+b.id,type:'apparent_inconsistency_needs_review',locality_key:key,
    title:'Two dated disclosures warrant reconciliation: '+a.agency,
    interpretation:'Different government records discuss overlapping policy/access subjects. Their dates, scope, adopted status or underlying technology may differ. This is NOT a confirmed contradiction.',
    original_refs:[{url:a.source_url,title:a.title,date:a.source_date,page:null},{url:b.source_url,title:b.title,date:b.source_date,page:null}],
    caveat:'Review full text and exact pages before claiming changed policy, inconsistency or wrongdoing.'});
  }
 }
 for(const d of reviewedDiffs){
  if(!d||!d.delta||!Array.isArray(d.evidence)||d.evidence.length<1||
    d.evidence.some(s=>!validUrl(s.url)||!/#page=\d{1,3}$/.test(s.url)||!/^[a-f0-9]{64}$/.test(s.sha||'')))continue;
  if(d.category==='policy_proposal'||d.delta.same)continue;
  out.unshift({id:'diff:'+d.id,type:'confirmed_documentary_difference',locality_key:d.agency||'',
   title:d.title,interpretation:'Reviewed source-pinned claim wording changed: earlier-only "'+d.delta.removed+
    '", later-only "'+d.delta.added+'". This is NOT proof of effective policy or equipment change.',
   original_refs:d.evidence.map(s=>({url:s.url,title:s.label,date:'refer to original page',page:s.url.match(/#page=(\d+)/)[1],sha:s.sha})),
   caveat:d.interpretation});
 }
 return out;
}
function crossAgency(docket,topic){
 if(!TOPICS.includes(topic))throw Error('Unknown comparison topic');
 const candidates=docket.rows.filter(r=>topics(r).includes(topic)),seen=new Map();
 for(const r of candidates){if(!seen.has(r.locality_key))seen.set(r.locality_key,r);}
 const rows=[...seen.values()].slice(0,15);
 return rows.map(r=>({agency:r.agency,locality_key:r.locality_key,title:r.title,
  status:r.status,date:r.source_date,url:r.source_url,
  caveat:'Different jurisdictions or technologies are not directly comparable; no contradiction inferred.'}));
}
function acquisition(lead,existing){
 if(!lead||!validUrl(lead.original_url)||!Array.isArray(lead.unknown))throw Error('No sourced lead to request records for');
 const related=(existing||[]).filter(r=>r.locality_key===lead.locality_key&&validUrl(r.source_url)).slice(0,8);
 const questions=lead.unknown.slice(0,4);
 const custodian=lead.agency||lead.locality_key;
 const content=['To: Public Records Officer, '+custodian,'Subject: Existing government records about '+lead.title,'',
  'Please provide reasonably identifiable, publicly releasable existing government records relating to:',
  ...questions.map((q,i)=>(i+1)+'. '+q),
  '','Relevant government publication: '+lead.original_url,
  'Reference date: '+lead.source_date,
  '','Please include signed agreements, publicly releasable amendments, adoption records, agendas, invoices, or official written policies where responsive.',
  'This request does not seek individual license-plate observations, personal location histories, hotlists, credentials, or confidential law-enforcement query logs.',
  'Please advise of fees and available narrowing options. No statutory deadline is assumed or submission made by Katoptron.'].join('\n');
 return {custodian_role:'Agency records custodian / city clerk / procurement officer (confirm jurisdiction)',
  agency:custodian,questions,existing:related,body:content,subject:'Public government records follow-up: '+lead.title,submitted:false};
}
function packageHtml(lead,comparison,request){
 if(!lead||!validUrl(lead.original_url)||!Array.isArray(lead.originals)||!lead.originals.length)throw Error('Verified lead required');
 const refs=lead.originals.map((x,i)=>'<li><strong>['+(i+1)+'] '+esc(x.title)+'</strong> ('+esc(x.date)+
  ', '+esc(x.status)+') <a rel="noopener noreferrer" href="'+esc(x.url)+'">'+esc(x.url)+'</a>'+
  '<p>Verification basis: '+esc(x.proof)+'</p></li>').join('');
 const related=(comparison||[]).filter(x=>x.locality_key===lead.locality_key).slice(0,7);
 const differences=related.map(x=>'<li><strong>'+esc(x.type)+'</strong>: '+esc(x.interpretation)+
  '<p>Source(s): '+x.original_refs.map(r=>'<a rel="noopener noreferrer" href="'+esc(r.url)+'">'+esc(r.title)+'</a>').join(' · ')+'</p></li>').join('');
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="referrer" content="no-referrer"><title>Katoptron sourced investigation package</title>'+
  '<style>body{font:16px/1.6 system-ui,sans-serif;color:#192632;max-width:900px;margin:2rem auto;padding:1rem}a{overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f3f5;padding:1rem}h2{border-bottom:1px solid #bbb}@media print{body{margin:.2in}section{break-inside:avoid}}</style></head><body>'+
  '<h1>Investigative research package</h1><p>'+esc(lead.title)+' | '+esc(lead.locality_key)+'</p>'+
  '<p><strong>Source status:</strong> '+esc(lead.label)+' · '+esc(lead.status)+' · <strong>Source date:</strong> '+esc(lead.source_date)+'</p>'+
  '<p><strong>Published finding:</strong> '+esc(lead.summary)+'</p><p><strong>Why it may matter:</strong> '+esc(lead.why)+'</p>'+
  '<p><strong>Evidence boundary:</strong> Publisher-attributed evidence. No misconduct, live camera inventory, actual spending, enacted policy, or contract execution inferred beyond the explicit original. Recheck all original URLs and exact pages before publication.</p>'+
  '<h2>Verified-source timeline and appendix</h2><ol>'+refs+'</ol>'+
  '<h2>Differences and missing evidence</h2><ul>'+(differences||'<li>No independently comparable source pair established.</li>')+'</ul>'+
  '<h2>Unresolved research questions</h2><ol>'+lead.unknown.map(q=>'<li>'+esc(q)+'</li>').join('')+'</ol>'+
  '<h2>Next verification actions</h2><ol>'+lead.steps.map(q=>'<li>'+esc(q)+'</li>').join('')+'</ol>'+
  '<h2>Official roles to contact</h2><p>Agency records custodian; city/county clerk; procurement or finance officer; agency policy officer. These are roles, not verified individual contacts.</p>'+
  '<h2>Unsent editable records request</h2><p>Suggested custodian: '+esc(request?.custodian_role||'Confirm appropriate records custodian')+'</p><pre>'+esc(request?.body||'')+'</pre>'+
  '<p>Katoptron does not file this request, provide legal advice, or guarantee that an unpublished document exists. This package contains only public-source material, no private case notes.</p></body></html>';
}
return Object.freeze({TOPICS,validUrl,topics,leadFromDocket,leadFromWatch,personalize,compare,crossAgency,acquisition,packageHtml});
});
