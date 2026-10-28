'use strict';
const assert=require('node:assert/strict');
const Core=require('../verified-agency-dossiers.js');
const WA=require('../wa-original-agency-dossiers.js');
const Loader=require('../agency-original-loader.js');
const Intel=require('../agency-intelligence-v2.js');
const Change=require('../agency-change-tracker.js');
const raw={
 okc:require('../data/verified-okc-2026-original-flock-contract-review.json'),
 ne:require('../data/verified-nebraska-original-aggregate-reports.json'),
 riSd:require('../data/verified-ri-sd-original-alpr-policies.json'),
 kittitas:require('../data/verified-wa-kittitas-scanned-draft-review.json'),
 waRegistry:require('../data/wa-original-agency-alpr-registrations.json'),
 waHeld:require('../data/wa-held-original-policy-diagnostics.json'),
 national:require('../data/verified-national-government-documents.json'),
 flock:require('../data/verified-wa-flock-policy-originals.json'),
 other:require('../data/verified-wa-agency-policies.json'),
 receipts:require('../data/wa-ago-original-policy-source-inspection.json')
};
const b=Core.catalog(raw,{
 okc:require('../okc-original-contracts.js'),ne:require('../nebraska-original-aggregate.js'),
 riSd:require('../ri-sd-original-policies.js'),kittitas:require('../wa-kittitas-draft-review.js'),
 national:require('../national-primary-documents.js')
});
const w=WA.catalog({flock:raw.flock,other:raw.other,registry:raw.waRegistry,receipts:raw.receipts},{flock:require('../wa-reviewed-flock-sources.js'),
 other:require('../wa-original-policies.js')});
const index=WA.combine(b,w);
const investigation=Intel.build(index);
assert.equal(investigation.total_agencies,18);
assert.equal(investigation.transitions.length,3);
const moline=investigation.profile('moline-police-il');
assert.equal(moline.documents,2);
assert.equal(moline.transitions.length,1);
assert.equal(moline.transitions[0].kind,'executed_contract_status_change');
assert.equal(moline.transitions[0].substantive,true);
assert.match(moline.transitions[0].after,/not independently established/);
const green=investigation.profile('green-bay-police-wi');
assert.equal(green.documents,4);
assert.equal(green.transitions[0].kind,'unadopted_policy_proposal');
assert.equal(green.transitions[0].substantive,false);
assert.equal(green.transitions[0].event_date,null);
assert.match(green.transitions[0].after,/No adopted policy change/);
const okc=investigation.profile('oklahoma-city-ok');
assert.equal(okc.documents,4);
assert.equal(okc.transitions[0].kind,'signed_contract_amendment');
assert.match(okc.transitions[0].after,/does not verify platform configuration/);
const fed=investigation.profile('federal-way-police-wa');
assert.match(fed.findings.map(f=>f.statement).join(' '),/proposed/);
assert.equal(fed.transitions.length,0);
const sedro=investigation.profile('sedro-woolley-police-wa');
assert.match(sedro.findings.map(f=>f.statement).join(' '),/thirty \(21\) days/);
const unknown=investigation.profile('arlington-police-wa');
assert(unknown.gaps.some(g=>g.includes('No individually page-reviewed signed Flock agreement')));
assert.throws(()=>investigation.profile('sultan-police-wa'),/unknown agency/);
const compared=investigation.compare(['green-bay-police-wi','moline-police-il','oklahoma-city-ok']);
assert.equal(compared.columns.length,3);
assert.equal(compared.topics.length,5);
assert.match(compared.method,/NOT agency compliance grades/);
assert.throws(()=>investigation.compare(['moline-police-il','moline-police-il']),/distinct agencies/);
assert.throws(()=>investigation.compare(['bogus','green-bay-police-wi']),/unknown agency/);
assert(!investigation.transitions.some(x=>x.verified_policy_effectiveness===true));
const adoption=require('../data/verified-policy-adoption-status-2026-10-27.json');
const apacheResolution=require('../data/apache-junction-adopted-resolution-chapter-2026-10-28.json');
const events=Change.events(investigation,{adoption,apacheResolution});
assert.equal(events.length,4);
assert.equal(events.filter(x=>x.substantive).length,3);
assert.equal(events.filter(x=>!x.substantive).length,1);
assert.deepEqual(new Set(events.map(e=>e.alert_category)),
 new Set(['contract_document','government_decision','policy_draft_reviewed']));
assert(events.every(x=>x.sources.every(s=>s.url.includes('#page=')&&s.sha.length===64)));
assert(events.every(x=>x.verified_policy_effectiveness===false));
const fake=structuredClone(index);
fake.dossiers.find(x=>x.key==='moline-police-il').documents[0].sha='f'.repeat(64);
assert.throws(()=>Intel.build(fake),/expected original/);
const fakeGB=structuredClone(index);
fakeGB.dossiers.find(x=>x.key==='green-bay-police-wi').documents
 .find(x=>x.id==='green-bay-wi-policy-draft-sept-2026').kind='published_department_policy';
assert.throws(()=>Intel.build(fakeGB),/published policy vs proposed draft/);
const fakeResolution=structuredClone(apacheResolution);
fakeResolution.legal_effective_date_verified=true;
assert.throws(()=>Change.events(investigation,{adoption,apacheResolution:fakeResolution}),/resolution/);
const fakeAction=structuredClone(adoption);
fakeAction.records.find(x=>x.state==='AZ').effective_date='2026-10-06';
assert.throws(()=>Change.events(investigation,{adoption:fakeAction,apacheResolution}),/adoption/);
const fakeHash=structuredClone(apacheResolution);
fakeHash.original_sha256='f'.repeat(64);
assert.throws(()=>Change.events(investigation,{adoption,apacheResolution:fakeHash}),/resolution/);
assert.equal(Object.keys(Loader.SOURCES).length,10);
console.log('M12 ORIGINAL INVESTIGATION PASS: 18 exact agencies, 25 original PDFs, 3 source-qualified original transitions, Apache official signed appendix, 4 change/proposal entries, strict no-enactment/no-camera boundaries');
