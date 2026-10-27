/* Katoptron Automated Accountability Engine v1.
 * Public, read-only, deterministic. No rating of legality or agency misconduct.
 * Every positive observation is attributed; absence is never proof of nonexistence.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronAudit=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const VERSION='1.0';
 const DATE=/^\d{4}-\d{2}-\d{2}$/;
 function safe(url){
  try{const u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password?u.href:null;}
  catch{return null;}
 }
 function day(value){
  const valueDay=String(value||'').slice(0,10);
  if(!DATE.test(valueDay))return null;
  const d=new Date(valueDay+'T00:00:00Z');
  return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===valueDay?valueDay:null;
 }
 function uniqueLinks(rows){
  return [...new Set(rows.map(safe).filter(Boolean))];
 }
 function validNumber(n){
  return n!==null&&n!==undefined&&n!==''&&Number.isFinite(Number(n))&&Number(n)>=0;
 }
 function assess(group,contracts=[],options={}){
  const required=['events','programs','portals','cameras','originalOutgoing',
   'originalIncoming','secondary','secondaryRetention','identityMatches'];
  if(!group||!required.every(k=>Array.isArray(group[k]))||!Array.isArray(contracts))
   throw Error('Incomplete published evidence, audit unavailable');
  if(typeof group.label!=='string'||typeof group.key!=='string')
   throw Error('Invalid locality identity');
  const contractStatus=options.contractStatus==='ok'?'ok':'unavailable';
  const auditArchiveStatus=options.auditArchiveStatus==='ok'?'ok':'unavailable';
  const archiveRows=Array.isArray(options.independentAudits)?options.independentAudits:[];
  // Independent auditor reports are curated original-source observations,
  // NOT assertions by Katoptron that an agency is legally compliant.
  // Never match an audit to a city by fuzzy name or an agency centroid.
  const independentAudits=archiveRows.filter(r=>{
   if(r.jurisdiction_key!==group.key||r.source_tier!=='original_government_archive_independent_audit_report'||
      !/^[0-9a-f]{64}$/.test(r.content_sha256||'')||
      !safe(r.source_url)||!day(r.report_date)||!day(r.reviewed_on)||
      !Array.isArray(r.findings)||!r.findings.length||
      !Array.isArray(r.pages_reviewed)||!r.pages_reviewed.length)return false;
   let host;
   try{host=new URL(r.source_url).hostname.toLowerCase();}catch{return false;}
   return host.endsWith('.gov')&&r.pages_reviewed.every(p=>Number.isInteger(p)&&p>=1&&p<=300)&&
    r.findings.every(f=>Number.isInteger(f.page)&&r.pages_reviewed.includes(f.page)&&
     typeof f.statement==='string'&&f.statement.length>=40&&f.statement.length<=700);
  });
  const asOf=day(options.asOf)||new Date().toISOString().slice(0,10);
  const findings=[],inventory=[],seen=new Set();
  function item(kind,title,detail,urls=[],meta={}){
   const sources=uniqueLinks(urls);
   if(!sources.length)return; // documented claims must have a citation
   inventory.push({kind,title,detail,sources,date:day(meta.date),tier:meta.tier||'original_publisher'});
  }
  function finding(code,type,priority,title,detail,question,urls=[]){
   if(seen.has(code))return;
   seen.add(code);
   findings.push({code,type,priority,title,detail,question,sources:uniqueLinks(urls)});
  }
  const gov=group.events.filter(e=>safe(e.source_url));
  const programs=group.programs.filter(p=>safe(p.official_evidence_url));
  const cameras=group.cameras.filter(c=>c.verification_status==='verified'&&
    c.location_accuracy==='exact'&&safe(c.source_url));
  const portals=group.portals.filter(p=>p.disclosure_status==='verified_source_snapshot'&&safe(p.portal_url));
  const sharing=group.originalOutgoing.filter(r=>
    ['original_government','original_flock_vendor_portal'].includes(r.source_kind)&&safe(r.source_url));
  const signed=contracts.filter(c=>safe(c.source_url));
  const citedContracts=signed.filter(c=>day(c.signed_on));
  const signedEvent=gov.filter(e=>e.event_type==='executed_contract');
  const citedSecond=group.secondaryRetention.filter(e=>
    e.evidence_tier==='secondary_aggregated_portal_snapshot'&&safe(e.source_url));
  const sourceCounts=new Map();
  for(const c of cameras)sourceCounts.set(c.source_url,(sourceCounts.get(c.source_url)||0)+1);
  for(const [url,n] of sourceCounts)item('government_gis',
    String(n)+' source-mapped exact location(s)',
    'Original government GIS coordinates; not proof of operating hardware or manufacturer.',
    [url],{tier:'government_geographic_source'});
  for(const e of gov)item('government_record',e.title||'Government record',
    'Source-dated original government event, not automatically a signed contract or installed camera.',
    [e.source_url],{date:e.event_date,tier:'original_government'});
  for(const p of programs)item('government_program','Government program: '+String(p.program_status||'reported'),
    'A government statement about a program, not device uptime.',
    [p.official_evidence_url],{date:p.source_date,tier:'original_government'});
  for(const p of portals)item('vendor_snapshot',String(p.agency_label||'Flock portal')+' disclosed metrics',
    'Original Flock portal snapshot. Count and retention are publisher-reported, not independently verified hardware.',
    [p.portal_url],{date:p.source_date,tier:'first_party_vendor_disclosure'});
  const sharingSources=new Map();
  for(const r of sharing){
   const key=String(r.source_key||r.source_url);
   if(!sharingSources.has(key))sharingSources.set(key,{row:r,count:0});
   sharingSources.get(key).count++;
  }
  for(const {row,count} of sharingSources.values()){
   item('original_sharing',String(row.publisher_name||'Original publisher')+' published '+count+' captured recipient name(s)',
    'Historical directional list, possibly excerpted; NOT live access, reciprocity or actual searches.',
    [row.source_url],{date:row.source_observed_on,tier:row.source_kind});
  }
  for(const c of citedContracts)item('signed_contract','Reviewed signed Flock agreement',
    'Signed-document date and recorded amount/end date, if present. Scheduled end is not a confirmed renewal or termination.',
    [c.source_url],{date:c.signed_on,tier:'original_government_signed_agreement'});
  for(const report of independentAudits){
   item('independent_auditor_report',report.report_title,
    'Third-party auditor report dated '+report.report_date+
    ', covering '+report.period_start+' through '+report.period_end+
    '. Original page claims and auditor conclusions are attributed; not a Katoptron certification.',
    [report.source_url],{date:report.report_date,tier:report.source_tier});
   for(const observation of report.findings){
    item('auditor_reported_observation',report.report_title+' · p.'+observation.page,
     observation.statement,[report.source_url+'#page='+observation.page],
     {date:report.report_date,tier:'independent_auditor_statement'});
   }
  }
  if(auditArchiveStatus==='unavailable'){
   finding('independent_audit_archive_unavailable','evidence_unavailable','P2',
    'Independent-audit source catalog unavailable',
    'The dated third-party audit catalog could not be retrieved. Do not infer that no audits exist.',
    'Please supply the most recent independent ALPR audit and its public official publication location.');
  }
  if(!gov.length&&!programs.length){
   finding('government_record_gap','evidence_gap','P1','Government decision/program evidence not indexed',
    'No qualifying original government decision or program record is currently published for this locality. This is not proof that no such records exist.',
    'Please provide the current authorizing decisions, agenda packets, meeting minutes and ALPR program policies.');
  }
  if(!cameras.length){
   finding('gis_gap','evidence_gap','P2','No authenticated individual-position GIS inventory',
    'No exact government-source-backed camera locations are indexed for this locality. An empty map does not mean cameras are absent.',
    'Please provide the current ALPR equipment inventory or public GIS map, with publication and revision dates.');
  }
  if(!portals.length){
   finding('vendor_gap','evidence_gap','P1','Original Flock transparency snapshot unavailable in this index',
    'No dated first-party Flock portal snapshot has been captured for this locality. It may exist outside Katoptron.',
    'Please identify the official Flock transparency portal and the effective dates for any posted retention policy.');
  }
  if(contractStatus==='unavailable'){
   finding('contract_endpoint_error','evidence_unavailable','P1','Signed-contract lookup unavailable',
    'The independently reviewed signed-agreement endpoint could not be checked. No absence-of-contract conclusion is possible.',
    'Please supply executed Flock agreements, amendments and signed contract dates to establish the public record.');
  }else if(!citedContracts.length&&!signedEvent.length){
   finding('contract_gap','evidence_gap','P1','No verified executed contract indexed',
    'No reviewed signed Flock agreement is published for this locality in Katoptron. This is not proof that no contract exists or no money was spent.',
    'Please provide executed Flock Safety agreements, amendments, invoices, purchase orders and termination/renewal notices.');
  }
  if(!sharing.length){
   finding('sharing_gap','evidence_gap','P1','No original outward access list indexed',
    'No source-qualified original publisher outward recipient list is indexed for this locality. Inbound references or secondary network entries do not establish its own outward sharing.',
    'Please provide the dated ALPR/Flock interagency sharing-permission list and any amendments, omitting personal plate-query data.');
  }else if([...sharingSources.values()].some(s=>s.row.captured_scope!=='complete')){
   finding('sharing_excerpt','scope_limitation','P1','At least one original sharing source is an excerpt',
    'Captured recipient names may not constitute the publisher’s full list. Never infer a complete list or zero unlisted recipients.',
    'Please supply a complete dated public agency-sharing list, with direction, publication date and completeness statement.',
    sharing.map(r=>r.source_url));
  }
  const datedVendor=portals.filter(p=>day(p.source_date)&&validNumber(p.retention_days));
  const vendorByAgency=new Map();
  for(const row of datedVendor){
   const id=String(row.agency_key||row.portal_url);
   if(!vendorByAgency.has(id))vendorByAgency.set(id,[]);
   vendorByAgency.get(id).push(row);
  }
  let vendorComparisons=0;
  for(const [id,rows] of vendorByAgency){
   rows.sort((a,b)=>a.source_date.localeCompare(b.source_date));
   const dates=new Map();
   for(const r of rows){
    const prev=dates.get(r.source_date);
    if(prev&&Number(prev.retention_days)!==Number(r.retention_days)){
     finding('same_day_vendor:'+id+':'+r.source_date,'source_difference','P1',
      'Different vendor retention values recorded for the same source date',
      'The same original publisher identity has two indexed readings dated '+r.source_date+
      ': '+prev.retention_days+' versus '+r.retention_days+
      ' days. A source correction, collection difference or indexing error must be checked; no policy violation is inferred.',
      'Please provide the authoritative retained historical snapshot and the effective retention-policy date.',
      [prev.portal_url,r.portal_url]);
    }
    dates.set(r.source_date,r);
   }
   const distinct=[...dates.values()].sort((a,b)=>a.source_date.localeCompare(b.source_date));
   for(let i=1;i<distinct.length;i++){
    vendorComparisons++;
    const old=distinct[i-1],cur=distinct[i];
    if(Number(old.retention_days)===Number(cur.retention_days))continue;
    finding('vendor_retention_change:'+id+':'+cur.source_date,'observed_change','P1',
     'Original Flock retention disclosure changed',
     String(old.retention_days)+' days on '+old.source_date+' versus '+
     String(cur.retention_days)+' days on '+cur.source_date+
     '. This is a difference between source snapshots, not necessarily the effective policy date.',
     'Please provide the governing retention policies, effective dates and approval records for the period between these snapshots.',
     [old.portal_url,cur.portal_url]);
   }
  }
  if(vendorComparisons===0){
   finding('history_gap','evidence_gap','P2','No comparable first-party retention history',
    'Fewer than two distinct dated retention readings from the same original Flock publisher were available. One snapshot cannot prove a policy changed or remained stable.',
    'Please provide dated historical Flock retention settings and the applicable approved retention policies.');
  }
  const linked=new Map();
  for(const m of group.identityMatches){
   if(m.match_basis==='original_flock_portal_slug_exact'&&safe(m.first_party_portal_url)){
    linked.set(m.source_agency_id,m.first_party_agency_key);
   }
  }
  if(group.secondary.length&&!linked.size){
   finding('identity_gap','identity_limitation','P2','Secondary agency identity not independently matched',
    'Similar city names do not establish that secondary-source records and government records describe the same operator.',
    'Please identify the agency-controlled official portal URL and canonical operating agency name.');
  }
  // Compare only explicit same-portal-ID matches on the exact observation date.
  // Different collection dates cannot be called a contradiction.
  const observedSecondary=citedSecond.filter(x=>linked.has(x.source_agency_id)&&
    day(x.observed_on)&&validNumber(x.retention_days));
  for(const sec of observedSecondary){
   const id=linked.get(sec.source_agency_id);
   for(const primary of vendorByAgency.get(id)||[]){
    if(primary.source_date!==sec.observed_on||Number(primary.retention_days)===Number(sec.retention_days))continue;
    finding('same_date_cross_tier:'+id+':'+sec.observed_on,
      'source_difference','P1','First-party and secondary retention readings differ',
      'A portal-identity-matched original vendor snapshot reports '+primary.retention_days+
      ' days, while a licensed secondary reading reports '+sec.retention_days+
      ' days on '+sec.observed_on+
      '. Collection times and reporting basis may differ; this is a review flag, NOT proof of misconduct.',
      'Please provide the original versioned retention setting and effective date for this observation.',
      [primary.portal_url,sec.source_url]);
   }
  }
  for(const c of citedContracts){
   if(day(c.ends_on)&&c.ends_on<asOf){
    finding('contract_end:'+String(c.contract_key||c.source_url),'followup','P1',
     'Source-documented scheduled contract end date has passed',
     'A reviewed contract names '+c.ends_on+' as its scheduled end date. Without a subsequent original agreement, renewal and termination remain unknown.',
     'Please provide any executed extensions, replacements, cancellation notices or closeout records after '+c.ends_on+'.',
     [c.source_url]);
   }
  }
  const rank={P1:0,P2:1,P3:2};
  findings.sort((a,b)=>(rank[a.priority]??9)-(rank[b.priority]??9)||a.code.localeCompare(b.code));
  const allSources=uniqueLinks(inventory.flatMap(i=>i.sources));
  return Object.freeze({
   version:VERSION,asOf,key:group.key,label:group.label,
   counts:{governmentRecords:gov.length,governmentPrograms:programs.length,
    exactGovernmentPositions:cameras.length,vendorSnapshots:portals.length,
    originalSharingSources:sharingSources.size,originalSharingNames:sharing.length,
    reviewedSignedContracts:citedContracts.length,independentAuditorReports:independentAudits.length,uniqueCitedSources:allSources.length},
   inventory,findings,sourceUrls:allSources,contractStatus,auditArchiveStatus,
   disclaimer:'Locality grouping does not verify common agency ownership. These findings are source-coverage gaps, date-limited changes and leads for review, NOT a legality, compliance, security or wrongdoing score. Missing records are unknown, not evidence of absence.'
  });
 }
 function requestDraft(audit){
  if(!audit||!Array.isArray(audit.findings))throw Error('No verified audit available');
  const queries=[...new Set(audit.findings.map(f=>f.question).filter(Boolean))];
  return [
   'DRAFT ONLY — NOT SENT',
   'Subject: Public records request — Flock Safety / ALPR documentation in '+audit.label,
   '',
   'To the appropriate public-records officer:',
   '',
   'I request existing public records relating to the use, contracting and governance of Flock Safety / automated license plate reader technology in '+audit.label+'.',
   'Please search the relevant public agency or advise if a different custodian holds these records. This locality name alone does not establish which agency operates any system.',
   '',
   ...queries.map((s,i)=>String(i+1)+'. '+s),
   '',
   'Please provide electronic copies, applicable record dates and public links where available. Redaction of protected personal information is appropriate; I am not requesting individual plate reads, personally identifiable travel records, or confidential investigative data.',
   'If a record is withheld, please identify the applicable legal basis. If you have no responsive record, please distinguish that from a claim that the activity did not occur.',
   '',
   'Thank you.',
   '',
   'Prepared from Katoptron public evidence as of '+audit.asOf+'.',
   'Review local law, custodian and wording before sending; this is a research draft, not legal advice.'
  ].join('\n');
 }
 return Object.freeze({VERSION,day,safe,assess,requestDraft});
});