/* Katoptron M12: original-source, agency-identity-safe investigative model.
 * All sourced document arrays must come from existing individually verified
 * agency catalogs. No name-based camera/operator reconciliation or scoring.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronInvestigations=api;
})(typeof window!=='undefined'?window:null,function(){
'use strict';
const TYPES=Object.freeze({
 policy:'Published policy and procedural statements',
 contract:'Contracts, agreement amendments and funding documents',
 decision:'Government decisions, actions and status statements',
 access:'Written permissions, access and information-sharing provisions',
 oversight:'Reporting, audit and transparency provisions',
 uncertainty:'Source limitations and unresolved questions'
});
const QUERY=Object.freeze({
 policy:/policy|retention|purge|delete|storage|draft|procedure|alpr.?system/i,
 contract:/contract|agreement|amendment|renewal|billing|funds|order.form|pause/i,
 decision:/council|adopt|approval|termination|paused|pause|signed|effective/i,
 access:/access|sharing|share|recipient|federal|search|immigration/i,
 oversight:/audit|oversight|transparency|report|annual|monthly|log/i
});
const KEY_DOCS=Object.freeze({
 moline_old:['moline-il-signed-flock-order-2024','6904610d03b2c44ebaa73d90e9b10a3d4022b1520924a2d37df8fd3da3b662df'],
 moline_new:['moline-il-signed-pause-2026','13496c7ce0e83787d6010963dddedd6ca54473947b054f887488a02c23923c81'],
 green_old:['green-bay-wi-policy-may-2026','3811cad37739128bb7e711157853f588f24b9307289a5e033c7c40968d4200c0'],
 green_new:['green-bay-wi-policy-draft-sept-2026','d11b9959c69f84d7e7ab06641ee8008afdab439129c2e30e62ebc4c300762b55'],
 okc_amendment:['okc-2026-signed-flock-amendment','ed37e684252bec2c1938c3f927c777bf34ca67222c11ec86fccbd46da60f9ea0']
});
function ensure(ok,msg){if(!ok)throw Error('Verified investigation unavailable: '+msg);}
function page(url,page){
 try{
  const u=new URL(url);
  if(u.protocol!=='https:'||u.username||u.password||u.hash||
   !Number.isInteger(page)||page<1||page>120)return null;
  u.hash='page='+page;return u.href;
 }catch{return null;}
}
function build(index){
 ensure(index&&index.no_live_camera_or_sharing_claims===true&&
   Array.isArray(index.dossiers)&&index.dossiers.length>=7,'original catalog missing');
 const keys=new Set(),ids=new Set(),documents=new Map();
 for(const a of index.dossiers){
  ensure(typeof a.key==='string'&&/^[a-z0-9-]{8,90}$/.test(a.key)&&
    !keys.has(a.key)&&typeof a.label==='string'&&
    /^[A-Z]{2}$/.test(a.state)&&Array.isArray(a.documents)&&a.documents.length>0,
    'agency identity');
  keys.add(a.key);
  for(const d of a.documents){
   ensure(typeof d.id==='string'&&!ids.has(d.id)&&
    /^[0-9a-f]{64}$/.test(d.sha||'')&&
    Array.isArray(d.pages)&&d.pages.length>0&&
    Array.isArray(d.findings)&&d.findings.length>0&&
    typeof d.limits==='string'&&d.limits.length>=40&&
    d.findings.every(f=>d.pages.includes(f.page)&&
      typeof f.statement==='string'&&f.statement.length>=50&&
      page(d.source_url,f.page)), 'individual document source pages');
   ids.add(d.id);documents.set(d.id,d);
  }
 }
 function known(id,sha,key){
  const doc=documents.get(id);
  ensure(doc&&doc.sha===sha&&index.dossiers.some(a=>a.key===key&&
   a.documents.some(d=>d.id===id)),'expected original '+id);
  return doc;
 }
 const transitions=[];
 const old=known(...KEY_DOCS.moline_old,'moline-police-il');
 const next=known(...KEY_DOCS.moline_new,'moline-police-il');
 ensure(old.date==='2024-12-04'&&next.date==='2026-09-15'&&
   old.findings.some(x=>x.category==='signed_order_historical_scope')&&
   next.findings.some(x=>x.category==='signed_contract_pause_terms'&&/remove/.test(x.statement)),
   'signed Moline document sequence');
 transitions.push(Object.freeze({
  id:'moline-signed-contract-to-pause',agency_key:'moline-police-il',
  kind:'executed_contract_status_change',status:'signed_pause_terms_verified_not_completed',
  event_date:next.date,date_basis:next.date_basis,title:'Signed vendor order followed by signed pause/termination terms',
  before:'December 2024 signed Flock order describes hardware and service terms.',
  after:'September 2026 signed agreement requires removal and platform-access termination, with conditional future terms. Completion of removal is not independently established.',
  sources:[{label:'Signed original order',url:page(old.source_url,5),sha:old.sha},
   {label:'Signed pause terms',url:page(next.source_url,1),sha:next.sha}],
  alert_category:'contract_document',substantive:true
 }));
 const gb=known(...KEY_DOCS.green_old,'green-bay-police-wi');
 const proposed=known(...KEY_DOCS.green_new,'green-bay-police-wi');
 ensure(gb.date==='2026-05-04'&&proposed.date===null&&
  proposed.kind==='draft_policy_unadopted'&&
  gb.findings.some(f=>f.category==='published_policy_retention'&&/30.day maximum/i.test(f.statement))&&
  proposed.findings.some(f=>f.category==='draft_retention_proposal_not_effective'&&/seven days/i.test(f.statement)),
  'published policy vs proposed draft');
 transitions.push(Object.freeze({
  id:'green-bay-policy-retention-draft',agency_key:'green-bay-police-wi',
  kind:'unadopted_policy_proposal',status:'proposal_only_not_current_retention',
  event_date:null,date_basis:'draft_imprint_not_adoption',
  title:'Published 30-day policy compared to proposed seven-day draft',
  before:'May 2026 published Policy 424 describes a 30-day maximum for ordinary system data.',
  after:'September 2026 explicitly marked DRAFT proposes seven days. No adopted policy change or live retention setting is established.',
  sources:[{label:'Published May policy, page 2',url:page(gb.source_url,2),sha:gb.sha},
   {label:'Unadopted draft, page 4',url:page(proposed.source_url,4),sha:proposed.sha}],
  alert_category:'policy_draft_reviewed',substantive:false
 }));
 const amendment=known(...KEY_DOCS.okc_amendment,'oklahoma-city-ok');
 ensure(amendment.date==='2026-08-18'&&
  amendment.findings.some(f=>f.category==='executed_amendment_federal_access_restrictions'),
  'signed amendment evidence');
 transitions.push(Object.freeze({
  id:'okc-executed-data-access-amendment',agency_key:'oklahoma-city-ok',
  kind:'signed_contract_amendment',status:'executed_written_vendor_access_limits',
  event_date:amendment.date,date_basis:amendment.date_basis,
  title:'Executed amendment adds written federal data-access limitations',
  before:'The amendment identifies the existing June 2023 Flock master agreement; the full earlier access clause was not separately reviewed here.',
  after:'Signed August 2026 amendment adds Flock-facing voluntary federal-access restrictions with compulsory-process exceptions; this does not verify platform configuration or all City disclosures.',
  sources:[{label:'Executed amendment, page 1',url:page(amendment.source_url,1),sha:amendment.sha},
   {label:'Signed original, page 2',url:page(amendment.source_url,2),sha:amendment.sha}],
  alert_category:'contract_document',substantive:true
 }));
 function category(d){const k=String(d.kind).toLowerCase();
  if(/draft/.test(k))return 'Unadopted draft';
  if(/signed.*pause|vendor_pause/.test(k))return 'Signed pause terms';
  if(/signed|executed|approved.*renewal/.test(k))return 'Signed or approved document (source-specific)';
  if(/policy|order|procedure/.test(k))return 'Published policy or other original';
  return 'Source-reviewed record';
 }
 function profile(key){
  const row=index.dossiers.find(a=>a.key===key);
  ensure(row,'unknown agency');
  const findings=[];
  for(const d of row.documents){
   for(const f of d.findings)findings.push({
    id:d.id+'#'+f.page+'#'+f.category,
    doc_id:d.id,document:d.title,kind:d.kind,category:f.category,
    status:category(d),date:d.date,date_basis:d.date_basis,
    date_note:d.date_note||null,
    statement:f.statement,url:page(d.source_url,f.page),sha:d.sha,limits:d.limits
   });
  }
  const timeline=[...row.documents].map(d=>({
   id:d.id,title:d.title,date:d.date,date_basis:d.date_basis,
   date_note:d.date_note||null,status:category(d),
   url:page(d.source_url,d.pages[0]),sha:d.sha
  })).sort((a,b)=>(b.date||'').localeCompare(a.date||'')||a.id.localeCompare(b.id));
  const meaningful=transitions.filter(t=>t.agency_key===key);
  const gaps=[
   'No independent verification of current camera operation or individual device coordinates from these documents.',
   'Written policy and signed agreement terms do not independently establish actual system practice or statutory compliance.',
   'No audited current access grants or actual license-plate search activity is established by this dossier.'
  ];
  if(!row.documents.some(d=>/signed.*(order|amendment|pause)|approved.*renewal/i.test(d.kind)))
   gaps.unshift('No individually page-reviewed signed Flock agreement in this exact-agency source catalog; contract terms are unknown here.');
  if(!row.documents.some(d=>/policy|procedure|general_order/i.test(d.kind)))
   gaps.unshift('No page-reviewed agency procedural policy in this exact-agency dossier.');
  return {key:row.key,label:row.label,state:row.state,tier:row.tier,
   documents:row.documents.length,findings,timeline,transitions:meaningful,
   notes:[...row.notes],gaps,topics:Object.fromEntries(
    Object.entries(QUERY).map(([topic,re])=>[topic,findings.filter(f=>
      re.test(f.category)||re.test(f.kind))])),
   limitations:'Exact agency source catalog only. Not an exhaustive locality camera inventory, compliance assessment or current data-sharing network.'
  };
 }
 function compare(keys){
  ensure(Array.isArray(keys)&&keys.length>=2&&keys.length<=3&&
   new Set(keys).size===keys.length,'comparison requires distinct agencies');
  const columns=keys.map(k=>profile(k));
  const topics=Object.keys(QUERY).map(topic=>({
   topic,label:TYPES[topic],columns:columns.map(p=>({
    key:p.key,label:p.label,findings:p.topics[topic].slice(0,30),
    missing:p.topics[topic].length===0
   }))
  }));
  return {columns,topics,method:'Compare source-page-reviewed written statements, NOT agency compliance grades. A missing finding indicates an incomplete reviewed catalog, not absence of a policy, deployment or permission.'};
 }
 return Object.freeze({profile,compare,transitions:Object.freeze(transitions),types:TYPES,
  sourcePage:page,total_agencies:index.dossiers.length});
}
return Object.freeze({build,page,TYPES});
});
