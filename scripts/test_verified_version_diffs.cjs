'use strict';
const assert=require('node:assert/strict');
const Diff=require('../verified-version-diffs.js');
const good={
 id:'review-one',kind:'signed_contract_amendment',title:'Original change',agency_key:'test-county',state:'CA',
 before:'Earlier signed contract requires a documented review and written request from the agency.',
 after:'Later signed amendment requires a documented review and a supervisor request from the agency.',
 status:'signed_amendment_source_review',substantive:true,verified_policy_effectiveness:false,actual_device_or_platform_configuration_verified:false,
 sources:[{label:'Original PDF page 2',url:'https://city.gov/contract.pdf#page=2',sha:'a'.repeat(64)}]
};
const r=Diff.fromEvents([good]);
assert.equal(r.length,1);assert.equal(r[0].category,'contract_document');assert.equal(r[0].evidence.length,1);
assert.match(r[0].delta.removed,/written/);assert.match(r[0].delta.added,/supervisor/);
assert.equal(Diff.validSource({url:'https://city.gov@evil.test/file#page=3',sha:'a'.repeat(64)}),false);
assert.throws(()=>Diff.fromEvents([{...good,sources:[{...good.sources[0],sha:'fake'}]}]));
assert.throws(()=>Diff.fromEvents([good,good]));
assert.throws(()=>Diff.fromEvents([{...good,verified_policy_effectiveness:true}]));
assert.throws(()=>Diff.fromEvents([{...good,kind:'unadopted_policy_proposal'}]),/Unadopted/);
const draft={...good,id:'draft',kind:'unadopted_policy_proposal',substantive:false};
assert.equal(Diff.fromEvents([draft])[0].category,'policy_proposal');
assert.match(Diff.fromEvents([draft])[0].interpretation,/not adopted/);
console.log('VERIFIED_SOURCE_DIFFS_PASS: source-pin guard, type enforcement, claim-only diff and non-adoption distinction');
