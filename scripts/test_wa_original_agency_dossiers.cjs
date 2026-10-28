'use strict';
const assert=require('node:assert/strict');
const WA=require('../wa-original-agency-dossiers.js');
const Base=require('../verified-agency-dossiers.js');
const waFiles={
 flock:require('../data/verified-wa-flock-policy-originals.json'),
 other:require('../data/verified-wa-agency-policies.json'),
 registry:require('../data/wa-original-agency-alpr-registrations.json'),
 receipts:require('../data/wa-ago-original-policy-source-inspection.json')
};
const waValidators={
 flock:require('../wa-reviewed-flock-sources.js'),
 other:require('../wa-original-policies.js')
};
const baseFiles={
 okc:require('../data/verified-okc-2026-original-flock-contract-review.json'),
 ne:require('../data/verified-nebraska-original-aggregate-reports.json'),
 riSd:require('../data/verified-ri-sd-original-alpr-policies.json'),
 kittitas:require('../data/verified-wa-kittitas-scanned-draft-review.json'),
 waRegistry:require('../data/wa-original-agency-alpr-registrations.json'),
 waHeld:require('../data/wa-held-original-policy-diagnostics.json'),
 national:require('../data/verified-national-government-documents.json')
};
const baseValidators={
 okc:require('../okc-original-contracts.js'),
 ne:require('../nebraska-original-aggregate.js'),
 riSd:require('../ri-sd-original-policies.js'),
 kittitas:require('../wa-kittitas-draft-review.js'),
 national:require('../national-primary-documents.js')
};
const wa=WA.catalog(waFiles,waValidators);
assert.equal(wa.length,11);
assert.equal(new Set(wa.map(x=>x.key)).size,11);
assert.ok(wa.every(r=>r.state==='WA'&&r.documents.length===1&&r.documents[0].state==='WA'));
const fed=wa.find(r=>r.key==='federal-way-police-wa');
assert.match(fed.tier,/historical_agency_training_bulletin/);
assert.equal(fed.documents[0].date,'2026-05-15');
assert.ok(fed.documents[0].findings.some(x=>/proposed/i.test(x.statement)));
const muk=wa.find(r=>r.key==='mukilteo-police-wa');
assert.equal(muk.documents[0].date_basis,'attorney_general_registration_date_not_policy_date');
assert.notEqual(muk.documents[0].date,null);
assert.ok(wa.some(r=>r.key==='black-diamond-police-wa'));
assert.ok(wa.some(r=>r.key==='normandy-park-police-wa'));
assert.ok(!wa.some(r=>r.key.includes('sultan')));
assert.ok(wa.every(r=>r.documents.every(d=>d.findings.every(f=>d.pages.includes(f.page)))));
const merged=WA.combine(Base.catalog(baseFiles,baseValidators),wa);
assert.equal(merged.agencies,17);
assert.equal(merged.original_documents,21);
assert.ok(merged.findings>30);
assert.ok(merged.no_live_camera_or_sharing_claims);
assert.ok(merged.dossiers.some(r=>r.key==='kittitas-police-wa'&&r.documents[0].kind==='draft_not_proven_adopted'));
assert.ok(merged.dossiers.some(r=>r.key==='oklahoma-city-ok'&&r.documents.length===4));
function tamper(callback){
 const x=JSON.parse(JSON.stringify(waFiles));callback(x);
 assert.throws(()=>WA.catalog(x,waValidators),/Unverified|Original|mismatch|incomplete|Missing|unverified|invalid|reviewed|source|publisher/);
}
tamper(x=>{x.flock.documents[0].source_url='https://evil.example/other';});
tamper(x=>{x.flock.documents[2].operational_status='live';});
tamper(x=>{x.flock.documents[2].findings[1].page=3;});
tamper(x=>{x.flock.held_review_candidates[0].publish_document_page_links=true;});
tamper(x=>{x.other.documents[0].source_url='https://elsewhere.example/a';});
tamper(x=>{x.other.documents[0].vendor='Flock Safety';});
tamper(x=>{x.flock.documents.pop();});
console.log('WA AGENCY X-RAY ORIGINAL DOSSIERS PASS: 11 original agency policy records + 6 existing profiles = 17 exact publishers / 21 originals; Sultan held');
