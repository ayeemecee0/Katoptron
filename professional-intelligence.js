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

/* Original-government national starters are historically source-attributed.
 * They are NOT newly observed Watch events, independent page-diffs or evidence
 * of operational devices. The issuer is preserved as the scope of each lead. */
function leadFromNational(sets){
 if(!Array.isArray(sets)||sets.length!==2)throw Error('Two reviewed national source registries required');
 const ids=new Set(),out=[];
 for(const batch of sets){
  if(!batch||batch.schema_version!==1||!Array.isArray(batch.leads)||batch.leads.length<1||batch.leads.length>50)
   throw Error('Reviewed national source registry unavailable');
  for(const r of batch.leads){
   const host=String(r.source_url||'').match(/^https:\/\/([^/]+)/)?.[1]||'';
   if(!r.id||ids.has(r.id)||!validUrl(r.source_url)||
    !(host.endsWith('.gov')||host==='www.naperville.il.us')||
    !/^[A-Z]{2}$/.test(r.state||'')||!String(r.source_issuer_review_status||'').startsWith('source_attributed_')||
    r.camera_coordinates_republished!==false||r.policy_enactment_inferred!==false||
    !Array.isArray(r.what_is_unknown)||r.what_is_unknown.length<2||
    !r.title||!r.published_finding||!r.verified_boundary||!r.source_date||
    r.independent_original_document_version_diff_verified===true||r.changed_source_hash_proven===true){
    throw Error('National source lead not sufficiently qualified');
   }
   ids.add(r.id);
   const issuer=String(r.agency||r.publisher||'Agency not independently verified');
   const key=issuer.toLowerCase().replace(/[^a-z0-9 -]/g,'').replace(/\s+/g,' ').trim().slice(0,115)+'|'+r.state;
   if(!/^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$/.test(key))throw Error('Invalid agency-scoped national research key');
   const topicList=topics({kind:r.document_type,title:r.title,summary:r.published_finding,status:r.source_issuer_review_status});
   out.push(Object.freeze({id:'national:'+r.id,locality_key:key,agency:issuer,title:r.title,
    summary:r.published_finding+' Evidence limit: '+r.verified_boundary,
    source_date:r.source_date,observed_at:null,status:r.source_issuer_review_status,kind:'source_attributed_historical',
    original_url:r.source_url,source_ids:[r.id],originals:[{title:r.title,url:r.source_url,
      date:r.source_date,status:r.source_issuer_review_status,proof:r.verified_boundary}],
    topics:topicList,why:why(topicList[0]),unknown:r.what_is_unknown.slice(0,6),
    steps:['Check the original government publication and its precise action/status.',
      'Resolve: '+r.further_verification,'Do not infer device operation or adopted policy from publication alone.'],
    label:'Source-attributed national research starter',fresh:false,
    verified_scope:'original_government_publisher_claim_not_independent_page_diff',amount:null,amount_basis:null}));
  }
 }
 return out;
}
/* Personalization is editorial topical relevance, never a probability of
 * misconduct, newsworthiness, verified truth or source completeness. */
function rankForResearch(leads,topic='all',question='',jurisdiction=''){
 if(!Array.isArray(leads)||typeof question!=='string'||question.length>160||
    !(['all',...TOPICS].includes(topic)))throw Error('Invalid research ranking inputs');
 const terms=[...new Set((question.toLowerCase().match(/[a-z0-9]{3,}/g)||[]).slice(0,12))];
 return leads.filter(l=>l&&validUrl(l.original_url)&&(!jurisdiction||l.locality_key===jurisdiction)&&
   (topic==='all'||l.topics.includes(topic))).map(l=>{
  const text=[l.title,l.summary,l.status,l.agency,...l.unknown].join(' ').toLowerCase();
  const overlap=terms.filter(t=>text.includes(t)).length;
  const match=topic==='all'?0:l.topics.includes(topic)?25:0;
  const score=match+overlap*8+(l.observed_at?2:0)+Math.min(l.unknown.length,4);
  return {lead:l,score,matched_terms:overlap,why_ranked:overlap+' research question term(s) match original-source wording; '+(topic==='all'?'any topic':topic+' topic')};
 }).sort((a,b)=>b.score-a.score||String(b.lead.observed_at||b.lead.source_date).localeCompare(String(a.lead.observed_at||a.lead.source_date))||a.lead.id.localeCompare(b.lead.id));
}
function digest(leads,prefs,now=new Date().toISOString()){
 if(!Number.isFinite(Date.parse(now)))throw Error('Valid digest review time required');
 const feed=personalize(leads,prefs),cutoff=Date.parse(now)-7*86400000;
 const recent=feed.newItems.filter(x=>x.observed_at&&Date.parse(x.observed_at)>=cutoff&&Date.parse(x.observed_at)<=Date.parse(now));
 return Object.freeze({newReviewed:recent,historical:feed.historical.slice(0,8),previouslyReviewed:feed.reviewed.slice(0,8),
   summary:recent.length?'New independently published, source-qualified Watch events since follow baseline':'No qualifying new Watch events in the last seven days',
   last_seven_days:true,automatic_email_enabled:false});
}
const ACTIONS=Object.freeze({
 contract:{role:'Procurement and finance records custodian (confirm actual public agency)',
   record:'Signed agreements, amendments, itemized invoices, payment registers and procurement award documents, if held'},
 policy:{role:'Department policy records custodian (confirm actual public agency)',
   record:'Effective and prior policy versions, dated approval orders and implementation notices, if held'},
 oversight:{role:'Clerk or oversight records custodian (confirm actual public agency)',
   record:'Final minutes, official vote results, audit responses and oversight correspondence, if held'},
 sharing:{role:'Agency data-governance records custodian (confirm actual public agency)',
   record:'Published interagency sharing agreements, access policy versions and aggregate audit procedures, if held'},
 procurement:{role:'Purchasing or finance records custodian (confirm actual public agency)',
   record:'Solicitations, bids, scoring memoranda, award notices and signed purchase orders, if held'}
});
function acquisitionBacklog(leads,existing,limit=20){
 if(!Number.isInteger(limit)||limit<1||limit>100)throw Error('Bounded evidence gap review required');
 const tasks=[],seen=new Set();
 for(const l of leads){
  if(!l||!validUrl(l.original_url)||!Array.isArray(l.unknown))continue;
  for(let i=0;i<l.unknown.length;i++){
   const q=l.unknown[i];
   if(!q||q.length<15||seen.has(l.id+':'+i))continue;
   seen.add(l.id+':'+i);
   tasks.push({task_id:l.id+':'+i,locality_key:l.locality_key,agency:l.agency,
    question:q,source_url:l.original_url,source_date:l.source_date,
    draft:acquisition({...l,unknown:[q]},existing),
    status:'missing_evidence_not_claim_of_wrongdoing'});
   if(tasks.length>=limit)return tasks;
  }
 }
 return tasks;
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
 if(!lead||!validUrl(lead.original_url)||!Array.isArray(lead.unknown)||!lead.locality_key)
  throw Error('No sourced lead to request records for');
 const related=(existing||[]).filter(r=>r.locality_key===lead.locality_key&&
  validUrl(r.source_url)&&r.source_url!==lead.original_url).slice(0,8);
 const questions=lead.unknown.slice(0,4);
 const selected=[...new Set((lead.topics||[]).filter(t=>ACTIONS[t]))];
 if(!selected.length)selected.push('oversight');
 const records=selected.map(t=>ACTIONS[t].record);
 const custodian=lead.agency||lead.locality_key;
 const content=[
  'UNSENT DRAFT — verify government custodian and responsive date range before submission',
  'To: Public Records Officer for '+custodian+' (recipient and authority unverified)',
  'Subject: Existing government records relating to '+lead.title,'',
  'I request existing, non-exempt and reasonably identifiable public records, IF HELD, for the source-dated matter below:',
  'Source: '+lead.original_url,'Government source date: '+lead.source_date,
  'Documentary status: '+lead.status,
  '','Specific unanswered questions (for record identification only, not requests for new analysis):',
  ...questions.map((q,i)=>(i+1)+'. '+q),
  '','Please search for the following categories of existing records to the extent responsive:',
  ...records.map((q,i)=>(i+1)+'. '+q+'.'),
  '','This request does not seek individual license-plate observations, personal location histories, hotlists, credentials, or confidential law-enforcement query logs.',
  'Please advise of fees and available narrowing options. Provide reasonably segregable public portions and identify the legal basis of any withholding.',
  'This is not a request for the government to create new records. No statutory deadline is assumed or submission made by Katoptron.'
 ].join('\n');
 return {custodian_role:selected.map(x=>ACTIONS[x].role).join('; '),
  agency:custodian,questions,requested_record_types:records,existing:related,body:content,
  subject:'Public government records follow-up: '+lead.title,submitted:false};
}
function assemblePackage(lead,docket){
 if(!lead||!validUrl(lead.original_url)||!docket||!Array.isArray(docket.rows))throw Error('Verified original-government source index required');
 const relevant=docket.rows.filter(r=>r.locality_key===lead.locality_key&&r.watch_category==='historical_research_only'&&validUrl(r.source_url));
 const originals=new Map();
 for(const row of lead.originals||[])if(validUrl(row.url))originals.set(row.url+'|'+row.date,{...row});
 for(const r of relevant){
  const key=r.source_url+'|'+r.source_date;
  if(!originals.has(key))originals.set(key,{title:r.title,url:r.source_url,date:r.source_date,status:r.status,proof:r.proof,summary:r.summary});
 }
 const timeline=[...originals.values()].sort((a,b)=>String(b.date).localeCompare(String(a.date)));
 return {...lead,originals:timeline,
  unknown:[...new Set([...lead.unknown,...relevant.flatMap(r=>r.open_questions)])].slice(0,22),
  steps:[...new Set([...lead.steps,
   'Reconcile contract, policy, council and department sources by agency identity and publication date before inferring a change.'])]};
}
function packageHtml(lead,comparison,request){
 if(!lead||!validUrl(lead.original_url)||!Array.isArray(lead.originals)||!lead.originals.length)throw Error('Verified lead required');
 const refs=lead.originals.map((x,i)=>'<li><strong>['+(i+1)+'] '+esc(x.title)+'</strong> ('+esc(x.date)+
  ', '+esc(x.status)+') <a rel="noopener noreferrer" href="'+esc(x.url)+'">'+esc(x.url)+'</a>'+
  '<p>Verification basis: '+esc(x.proof)+'</p>'+ (x.summary?'<p>Source-attributed government finding: '+esc(x.summary)+'</p>':'')+'</li>').join('');
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
return Object.freeze({TOPICS,validUrl,topics,leadFromDocket,leadFromWatch,leadFromNational,rankForResearch,digest,personalize,compare,crossAgency,acquisition,acquisitionBacklog,assemblePackage,packageHtml});
});
