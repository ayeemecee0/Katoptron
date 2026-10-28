/* Nationwide policy original-source coverage and agency research workload.
 * State-level research enrollment and government URL reachability are NOT
 * agency census or Flock verification. Only individually reviewed dossiers
 * qualify as original PDF facts. Never derive GPS/sharing/operational counts.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronNationwidePolicyCoverage=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const STATES='AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split(' ');
 const SOURCE_RANK=Object.freeze({verified_original:0,adopted_official_notice:1,
   state_registered_unverified:2,government_source_reachable_unreviewed:3,
   government_source_held:4,official_legacy_source_unreviewed:5});
 function build(input,apis){
  const required=['registry','legacy','receipts','wa','dossiers','adoption'];
  if(!input||!required.every(k=>input[k])||
     !apis?.jurisdictions||!apis?.wa||!apis?.adoption)
   throw Error('Nationwide original-government evidence sources incomplete');
  const baseline=apis.jurisdictions.catalog(input.registry,input.legacy);
  const checked=apis.jurisdictions.sourceReceipts(input.receipts,input.registry);
  const wa=apis.wa.catalog(input.wa);
  const decisions=apis.adoption.validate(input.adoption);
  const dossier=input.dossiers;
  if(baseline.total!==51||baseline.seeded!==51||baseline.seedUrls!==43||
     baseline.legacyUrls!==14||baseline.reviewedInstallationsClaimed!==0||
     checked.receipts.size!==43||wa.length!==97||
     dossier.agencies!==18||dossier.original_documents!==25||
     dossier.no_live_camera_or_sharing_claims!==true||
     decisions.government_actions_adopted!==1||
     decisions.published_unadopted_drafts!==1)
   throw Error('Government national evidence ledger counts changed; review source changes');
  const byState=new Map(baseline.states.map(s=>[s.state,{
   state:s.state,name:s.name,sources:[],registered:[],reviewed:[],
   decisions:[],source_held:0,source_reachable:0,
   original_source_urls:0,source_monitoring_enrolled:true,
   verified_agency_count:0,complete_agency_census:false,
   complete_policy_inventory:false,
   flock_cameras_individually_verified_from_sources:0
  }]));
  for(const s of baseline.states){
   const dest=byState.get(s.state);
   for(const src of s.seeds){
    const rec=checked.receipts.get(src.id);
    if(!rec||rec.state!==s.state||rec.source_url!==src.source_url)
     throw Error('State source original receipt mismatch');
    const reachable=rec.status.startsWith('original_government_');
    dest.sources.push({
     id:src.id,publisher:src.publisher,role:src.publisher_role,
     url:src.source_url,evidence:reachable?
      'government_source_reachable_unreviewed':'government_source_held',
     detail:reachable?'Government original link retrieved; individual statements NOT verified':
       'Government original retrieval held: '+rec.status,
     observed_status:rec.status,document_hash:reachable?rec.sha256_at_observation:null,
     policy_adopted:false,flock_installed_verified:false,
     source_page_reviewed:false
    });
    dest[reachable?'source_reachable':'source_held']++;
   }
   for(const old of s.existing){
    dest.sources.push({
     id:old.id,publisher:old.agency,role:old.publisher_role,
     url:old.url,evidence:'official_legacy_source_unreviewed',
     detail:'Curated public government index; no individual policy verified by this entry',
     observed_status:'not_independently_rechecked_in_this_snapshot',
     document_hash:null,policy_adopted:false,flock_installed_verified:false,
     source_page_reviewed:false
    });
   }
   dest.original_source_urls=dest.sources.length;
  }
  const regNames=new Set();
  for(const x of wa){
   const key=x.agency_name.toLowerCase();
   if(regNames.has(key))throw Error('Duplicated registered state agency');
   regNames.add(key);
   byState.get('WA').registered.push({
    id:x.id,agency:x.agency_name,
    registered_on:x.submitted_on,
    policy_urls:x.policy_links_from_official_ago_page,
    evidence:'state_registered_unverified',
    detail:'Washington Attorney General self-certification listing; Flock vendor and installation NOT established',
    policy_adopted:false,flock_installed_verified:false,
    source_page_reviewed:false
   });
  }
  const seenDossier=new Set(),seenDocuments=new Set();
  for(const agency of dossier.dossiers){
   if(!byState.has(agency.state)||seenDossier.has(agency.key)||
      !Array.isArray(agency.documents)||!agency.documents.length||
      typeof agency.label!=='string'||agency.label.length<5)
    throw Error('Missing agency-level original source identity');
   seenDossier.add(agency.key);
   const docs=[];
   for(const d of agency.documents){
    if(seenDocuments.has(d.id)||!/^[a-f0-9]{64}$/.test(d.sha||'')||
       !Array.isArray(d.pages)||!d.pages.length||
       !Array.isArray(d.findings)||!d.findings.length||
       !d.findings.every(f=>d.pages.includes(f.page))||
       typeof d.source_url!=='string'||!d.source_url.startsWith('https://'))
     throw Error('Dossier source-page verification lost');
    seenDocuments.add(d.id);
    docs.push({
     id:d.id,title:d.title,kind:d.kind,date:d.date,
     original_sha256:d.sha,
     url:d.source_url,
     pages:d.pages.slice(),source_page_reviewed:true,
     adoption_verified:false,
     note:'Historical reviewed source text; no automatically inferred adoption or live operation'
    });
   }
   const dest=byState.get(agency.state);
   dest.reviewed.push({id:agency.key,agency:agency.label,
    evidence:'verified_original',documents:docs});
   dest.verified_agency_count++;
  }
  for(const action of decisions.records){
   if(!byState.has(action.state)||
      action.effective_date!==null||
      !['adopted_government_original_notice',
        'draft_published_no_adoption_verified'].includes(action.status))
    throw Error('Government adoption/draft status ungrounded');
   byState.get(action.state).decisions.push({
    id:action.id,title:action.title,jurisdiction:action.jurisdiction,
    status:action.status,
    date:action.event_date,
    effective_date:null,
    source_url:action.source_url,
    corroboration_url:action.corroboration_url,
    evidence:'adopted_official_notice',
    original_city_clerk_ordinance_visually_reviewed:
      action.state==='AZ',
    note:action.limits,
    camera_coordinates_claimed:0
   });
  }
  const rows=[...byState.values()].sort((a,b)=>a.name.localeCompare(b.name));
  const counts={
   states_enrolled:rows.length,
   state_original_source_seeded:rows.filter(s=>s.original_source_urls>0).length,
   original_source_links:rows.reduce((n,s)=>n+s.original_source_urls,0),
   new_seed_accessible:checked.counts.accessible,
   new_seed_held:checked.counts.held,
   state_ago_registered_agencies:wa.length,
   individually_source_reviewed_dossier_agencies:dossier.agencies,
   individually_source_reviewed_original_documents:dossier.original_documents,
   adopted_ordinance_government_status_records:decisions.government_actions_adopted,
   published_unadopted_draft_status_records:decisions.published_unadopted_drafts,
   states_with_complete_agency_policy_census:0,
   verified_current_camera_locations_added:0,
   verified_current_data_sharing_edges_added:0
  };
  if(counts.states_enrolled!==51||counts.state_original_source_seeded!==51||
     counts.original_source_links!==57||
     counts.new_seed_accessible+counts.new_seed_held!==43||
     rows.some(s=>s.complete_agency_census||s.complete_policy_inventory||
       s.flock_cameras_individually_verified_from_sources!==0))
    throw Error('Nationwide source coverage incorrectly implied complete factual census');
  const priorities=rows.map(s=>({
   state:s.state,name:s.name,
   reviewed_agency_count:s.reviewed.length,
   registered_only_count:s.registered.length,
   source_links:s.original_source_urls,
   reachable_unreviewed:s.source_reachable,
   held_government_origins:s.source_held,
   evidence_gap:s.reviewed.length===0?
    'no_individually_page_reviewed_agency_dossier':
    'agency_dossiers_present_but_statewide_coverage_not_established',
   recommended_next:s.source_held>0?
    'resolve_original_government_link_hold_and_source_attribution':
    s.reviewed.length===0?
    'inspect_original_government_source_for_flock_specific_agency_policy':
    'expand_to_additional_source_identified_agencies_without_conflating_deployments',
   next_review_status:'research_queue_not_an_enacted_policy_fact',
   complete_agency_census:false
  })).sort((a,b)=>Number(a.reviewed_agency_count>0)-Number(b.reviewed_agency_count)||
    b.held_government_origins-a.held_government_origins||
    a.state.localeCompare(b.state));
  return Object.freeze({
   states:rows,priorities,counts,
   scope:'Every US state and DC has a source research entry, but this is NOT every municipality, county or law-enforcement agency, and source retrieval is not policy verification.',
   source_reviewed_states:rows.filter(x=>x.reviewed.length>0).map(x=>x.state).sort(),
   zero_complete_census_claim:true
  });
 }
 function filter(index,state,query,tier){
  if(!index||!Array.isArray(index.states))return [];
  const needle=String(query||'').trim().toLowerCase().slice(0,120);
  return index.states.filter(s=>!state||state==='ALL'||s.state===state).map(s=>{
   const includes=(text)=>!needle||text.toLowerCase().includes(needle)||
      s.name.toLowerCase().includes(needle)||s.state.toLowerCase()===needle;
   const sources=s.sources.filter(x=>(!tier||tier==='ALL'||tier==='sources')&&
    includes(x.publisher+' '+x.role+' '+x.id));
   const registered=s.registered.filter(x=>(!tier||tier==='ALL'||tier==='registered')&&
    includes(x.agency));
   const reviewed=s.reviewed.filter(x=>(!tier||tier==='ALL'||tier==='verified')&&
    includes(x.agency+' '+x.documents.map(d=>d.title).join(' ')));
   const decisions=s.decisions.filter(x=>(!tier||tier==='ALL'||tier==='actions')&&
    includes(x.jurisdiction+' '+x.title));
   return {...s,sources,registered,reviewed,decisions};
  }).filter(s=>s.sources.length+s.registered.length+s.reviewed.length+s.decisions.length>0);
 }
 return Object.freeze({build,filter,STATES,SOURCE_RANK});
});
