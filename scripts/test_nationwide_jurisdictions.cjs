'use strict';
const assert=require('node:assert/strict');
const API=require('../nationwide-jurisdictions.js');
const sources=require('../data/nationwide-government-jurisdiction-registry.json');
const old=require('../data/national-government-audit-source-portals.json');
const receiptData=require('../data/nationwide-original-government-source-receipts.json');
const check=API.sourceReceipts(receiptData,sources);
assert.equal(check.counts.accessible,31);
assert.equal(check.counts.held,12);
assert.equal(check.receipts.size,45);
assert.equal(check.counts.held,14);
for(const id of ['ma-groton-municipal-contract-termination-2026','oh-shaker-heights-data-contract-policy-2026']){
 const r=check.receipts.get(id);
 assert.equal(r.pending_unobserved,true);
 assert.equal(r.sha256_at_observation,null);
 assert.equal(r.flock_equipment_verified,false);
}
assert.equal(check.receipts.get('dc-independent-government-policy-recommendation').page_count_at_observation,6);
assert.equal(check.receipts.get('ny-state-model-policy-not-agency-adoption').status,'held_redirect');
function rejectReceipt(mut){
 const r=JSON.parse(JSON.stringify(receiptData));mut(r);
 assert.throws(()=>API.sourceReceipts(r,sources),/invalid|incomplete|Held|Source|Nationwide/i);
}
rejectReceipt(r=>{r.receipts[0].flock_equipment_verified=true;});
rejectReceipt(r=>{r.receipts[0].source_url='https://evil.example';});
rejectReceipt(r=>{r.receipts[0].state='NY';});
rejectReceipt(r=>{r.receipts.pop();});
rejectReceipt(r=>{const held=r.receipts.find(x=>x.status.startsWith('held'));held.sha256_at_observation='0'.repeat(64);});
const result=API.catalog(sources,old);
assert.equal(result.total,51);
assert.equal(result.seeded,51);
assert.equal(result.without,0);
assert.equal(result.seedUrls,45);
assert.equal(result.legacyUrls,14);
assert.equal(result.reviewedInstallationsClaimed,0);
assert.equal(result.states.length,51);
assert.ok(result.states.every(x=>x.name&&x.seeds.length+x.existing.length>=1));
assert.ok(result.states.some(x=>x.state==='DC'));
assert.equal(result.states.find(x=>x.state==='WA').existing.length>=1,true);
assert.equal(result.states.find(x=>x.state==='WV').seeds[0].publisher_role,'other_vendor_alpr_procurement_not_flock');
assert.equal(result.states.find(x=>x.state==='NY').seeds[0].publisher_role,'state_model_policy_not_agency_adoption');
assert.equal(result.states.find(x=>x.state==='WY').seeds[0].publisher_role,'unadopted_state_bill');
assert.equal(API.safe('https://www.state.wv.us/admin/purchase/Awards/Documents/2026/Q2/A_0926_CPO_PSC2600000003.pdf'),
 'https://www.state.wv.us/admin/purchase/Awards/Documents/2026/Q2/A_0926_CPO_PSC2600000003.pdf');
for(const url of ['https://evil.example/report','http://www.texas.gov/flock',
 'https://notreal.wv.us/fake','https://www.state.wv.us.evil.example/path',
 'https://www.texas.gov/../internal','https://www.texas.gov/%2e%2e/private',
 'https://www.texas.gov/path#frag']){
 assert.equal(API.safe(url),null,url);
}
function bad(change){
 const r=JSON.parse(JSON.stringify(sources));change(r);
 assert.throws(()=>API.catalog(r,old),/authentic|incomplete|enrollment|government|Unverified|false/);
}
bad(r=>{r.jurisdictions.pop();});
bad(r=>{r.jurisdictions[1].state=r.jurisdictions[0].state;});
bad(r=>{r.official_seed_sources[0].source_url='https://evil.example/policy';});
bad(r=>{r.official_seed_sources[0].camera_coordinates=[1,2];});
bad(r=>{r.official_seed_sources[0].flock_installed=true;});
bad(r=>{r.official_seed_sources[0].origin_role='vendor_deployment_verified';});
bad(r=>{r.official_seed_sources[0].id=r.official_seed_sources[1].id;});
console.log('NATIONWIDE 51/51 SOURCE-SEEDED PASS: 43 new originals, 14 legacy source links, zero equipment census assertions');
