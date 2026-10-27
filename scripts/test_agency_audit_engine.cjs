'use strict';
const assert=require('node:assert/strict');
const Audit=require('../agency-audit-engine.js');
const base=()=>({
 key:'palo alto|CA',label:'Palo Alto, CA',
 events:[],programs:[],portals:[],cameras:[],originalOutgoing:[],
 originalIncoming:[],secondary:[],secondaryRetention:[],identityMatches:[]
});
function run(g,contracts=[],status='ok'){
 return Audit.assess(g,contracts,{contractStatus:status,asOf:'2026-10-26'});
}
const empty=run(base());
assert.equal(empty.counts.uniqueCitedSources,0);
assert.ok(empty.findings.some(f=>f.code==='contract_gap'));
assert.ok(empty.findings.some(f=>f.code==='sharing_gap'));
assert.ok(empty.findings.every(f=>f.type!=='alleged_violation'));
assert.match(empty.disclaimer,/NOT a legality/);
assert.match(Audit.requestDraft(empty),/DRAFT ONLY — NOT SENT/);
assert.match(Audit.requestDraft(empty),/not requesting individual plate reads/i);
const unavailable=run(base(),[],'unavailable');
assert.ok(unavailable.findings.some(f=>f.code==='contract_endpoint_error'));
assert.ok(!unavailable.findings.some(f=>f.code==='contract_gap'),
 'Failed contract endpoint cannot become an absence claim');
const g=base();
g.events.push({event_key:'gov1',title:'Original agenda',event_type:'recorded_legislative_decision',
 source_url:'https://paloalto.gov/agenda',event_date:'2026-05-02'});
g.programs.push({program_status:'reviewed',source_date:'2026-01-01',official_evidence_url:'https://paloalto.gov/alpr'});
g.cameras.push({verification_status:'verified',location_accuracy:'exact',
 source_url:'https://paloalto.gov/gis'});
g.cameras.push({verification_status:'unverified',location_accuracy:'exact',
 source_url:'https://paloalto.gov/unverified'});
g.portals.push({agency_key:'pa_pd',agency_label:'Palo Alto CA PD',disclosure_status:'verified_source_snapshot',
 source_date:'2026-09-01',retention_days:30,portal_url:'https://transparency.flocksafety.com/palo-alto-ca-pd'});
g.portals.push({agency_key:'pa_pd',agency_label:'Palo Alto CA PD',disclosure_status:'verified_source_snapshot',
 source_date:'2026-10-01',retention_days:14,portal_url:'https://transparency.flocksafety.com/palo-alto-ca-pd'});
g.originalOutgoing.push({source_key:'pa_gov',source_kind:'original_government',
 source_url:'https://paloalto.gov/sharing',publisher_name:'PA agency',captured_scope:'partial',recipient_label:'County PD'});
g.secondary=[{source_agency_id:'pa-pd',agency_name:'Palo Alto CA PD'}];
g.identityMatches=[{first_party_agency_key:'pa_pd',
 source_agency_id:'pa-pd',match_basis:'original_flock_portal_slug_exact',
 first_party_portal_url:'https://transparency.flocksafety.com/palo-alto-ca-pd'}];
g.secondaryRetention=[{source_agency_id:'pa-pd',retention_days:25,observed_on:'2026-09-01',
 evidence_tier:'secondary_aggregated_portal_snapshot',source_url:'https://example.org/licensed'}];
const actual=run(g);
assert.equal(actual.counts.exactGovernmentPositions,1,'Do not promote unverified geometry');
assert.equal(actual.counts.originalSharingNames,1);
assert.equal(actual.counts.originalSharingSources,1);
assert.ok(actual.findings.some(x=>x.code==='sharing_excerpt'));
assert.ok(actual.findings.some(x=>x.code.startsWith('vendor_retention_change:')),
 'True first party source-dated differences are flagged');
assert.ok(actual.findings.some(x=>x.code.startsWith('same_date_cross_tier:')),
 'Exact identity same-day secondary inconsistency gets a review flag');
assert.ok(actual.findings.some(x=>x.code==='contract_gap'));
assert.ok(!actual.findings.some(x=>x.code==='identity_gap'));
assert.ok(actual.inventory.every(x=>x.sources.length>0));
assert.ok(actual.inventory.every(x=>x.sources.every(url=>url.startsWith('https://'))));
assert.ok(!actual.sourceUrls.includes('https://paloalto.gov/unverified'));
const wrong=base();
wrong.portals=g.portals.slice();
wrong.secondary=g.secondary.slice();
wrong.secondaryRetention=g.secondaryRetention.slice();
wrong.identityMatches=[]; // City name equivalence is NOT agency/portal identity.
const noFalse=run(wrong);
assert.ok(noFalse.findings.some(x=>x.code==='identity_gap'));
assert.ok(!noFalse.findings.some(x=>x.code.startsWith('same_date_cross_tier:')));
const offDate=base();
offDate.portals=g.portals.slice();
offDate.secondary=g.secondary.slice();
offDate.identityMatches=g.identityMatches.slice();
offDate.secondaryRetention=[{...g.secondaryRetention[0],observed_on:'2026-09-02'}];
assert.ok(!run(offDate).findings.some(x=>x.code.startsWith('same_date_cross_tier:')),
 'Different snapshot dates are not contradictions');
const same=base();
same.portals=[{...g.portals[0]},{...g.portals[0],retention_days:25}];
const sameDay=run(same);
assert.ok(sameDay.findings.some(x=>x.code.startsWith('same_day_vendor:')));
const contract=run(base(),[{
 contract_key:'one',source_url:'https://paloalto.gov/signed.pdf',
 signed_on:'2025-01-01',ends_on:'2026-01-01',amount_usd:1200
}]);
assert.equal(contract.counts.reviewedSignedContracts,1);
assert.ok(contract.findings.some(x=>x.code.startsWith('contract_end:')));
assert.ok(!contract.findings.some(x=>x.code==='contract_gap'));
assert.throws(()=>run({label:'Bad',key:'bad'}),/Incomplete/);
assert.equal(Audit.day('2026-02-30'),null);
assert.equal(Audit.safe('javascript:alert(1)'),null);
assert.equal(Audit.safe('https://user:pass@agency.gov/file'),null);
assert.equal(Audit.safe('https://agency.gov/file'),'https://agency.gov/file');

const auditManifest=require('../data/verified-independent-audits.json');
const shakopee=base();
shakopee.key='shakopee|MN';
shakopee.label='Shakopee, MN';
const independent=Audit.assess(shakopee,[],{
 contractStatus:'ok',auditArchiveStatus:'ok',asOf:'2026-10-26',
 independentAudits:auditManifest.reports
});
assert.equal(independent.counts.independentAuditorReports,5);
assert.ok(independent.inventory.some(x=>x.kind==='independent_auditor_report'&&
 x.sources.includes('https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf')));
assert.ok(independent.inventory.some(x=>x.kind==='auditor_reported_observation'&&
 x.sources.some(url=>url.includes('#page=2'))));
assert.equal(run(base(),[], 'ok').counts.independentAuditorReports,0);
const fake=Audit.assess(shakopee,[],{
 contractStatus:'ok',auditArchiveStatus:'ok',
 independentAudits:[{...auditManifest.reports[0],source_url:'https://evil.example/alpr.pdf'}]
});
assert.equal(fake.counts.independentAuditorReports,0,'Untrusted hosts cannot be original government auditor sources');
const missing=Audit.assess(shakopee,[],{contractStatus:'ok',auditArchiveStatus:'unavailable'});
assert.ok(missing.findings.some(x=>x.code==='independent_audit_archive_unavailable'));

const stillwater=base();
stillwater.key='stillwater|MN';stillwater.label='Stillwater, MN';
const stillwaterAudit=Audit.assess(stillwater,[],{
 contractStatus:'ok',auditArchiveStatus:'ok',
 independentAudits:auditManifest.reports
});
const woodbury=base();
woodbury.key='woodbury|MN';woodbury.label='Woodbury, MN';
const woodburyAudit=Audit.assess(woodbury,[],{
 contractStatus:'ok',auditArchiveStatus:'ok',
 independentAudits:auditManifest.reports
});
assert.equal(woodburyAudit.counts.independentAuditorReports,5,
 'Do not collapse distinct source-dated independent audits');
assert.ok(woodburyAudit.inventory.some(x=>x.sources.includes('https://www.lrl.mn.gov/docs/2024/mandated/240350.pdf')));
for(const [key,label,url,expected] of [
 ['edina|MN','Edina, MN','210885.pdf',4],
 ['west saint paul|MN','West Saint Paul, MN','261167.pdf',2],
 ['wyoming|MN','Wyoming, MN','261268.pdf',1]
]){
 const group={...base(),key,label};
 const assessed=Audit.assess(group,[],{contractStatus:'ok',auditArchiveStatus:'ok',independentAudits:auditManifest.reports});
 assert.equal(assessed.counts.independentAuditorReports,expected,'Source-bound original independent audit count '+key);
 assert.ok(assessed.inventory.some(i=>i.kind==='independent_auditor_report'&&i.sources.some(u=>u.endsWith(url))));
}
assert.equal(stillwaterAudit.counts.independentAuditorReports,1);
assert.ok(stillwaterAudit.inventory.some(x=>x.kind==='auditor_reported_observation'&&
 x.detail.includes('17 stationary Flock ALPR units')&&
 x.sources.includes('https://www.lrl.mn.gov/docs/2026/mandated/261351.pdf#page=2')));
assert.ok(!stillwaterAudit.inventory.some(x=>x.detail.includes('four active stationary')),
 'No unrelated agency observations must leak into Stillwater evidence');
const hennepin=base();
hennepin.key='hennepin county|MN';hennepin.label='Hennepin County, MN';
const hennepinAudit=Audit.assess(hennepin,[],{
 contractStatus:'ok',auditArchiveStatus:'ok',
 independentAudits:auditManifest.reports
});
assert.equal(hennepinAudit.counts.independentAuditorReports,4);
assert.ok(hennepinAudit.inventory.some(x=>x.kind==='auditor_reported_observation'&&
 x.detail.includes('four active stationary Flock ALPR units')&&
 x.sources.some(u=>u.includes('251683.pdf#page=2'))));
const unrelated=base();
unrelated.key='hennepin city|MN';unrelated.label='Hennepin City, MN';
assert.equal(Audit.assess(unrelated,[],{
 contractStatus:'ok',auditArchiveStatus:'ok',
 independentAudits:auditManifest.reports
}).counts.independentAuditorReports,0,'Agency identity must match exact source key');

console.log('AUTOMATED ACCOUNTABILITY ENGINE PASS: evidence boundaries, precise source-dated differences, private-safe public requests, fail-closed contracts');
