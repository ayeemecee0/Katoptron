'use strict';
const assert=require('node:assert/strict');
const API=require('../wa-kittitas-draft-review.js');
const d=require('../data/verified-wa-kittitas-scanned-draft-review.json');
const registry=require('../data/wa-original-agency-alpr-registrations.json');
const held=require('../data/wa-held-original-policy-diagnostics.json');
const ok=API.review(d,registry.registrations,held.entries);
assert.equal(ok.original_page_count,4);
assert.equal(ok.document_lifecycle,'draft_not_proven_adopted');
assert.match(ok.findings[0].statement,/Flock online training/);
assert.match(ok.findings[0].statement,/Neither the draft nor its training reference verifies/);
assert.match(ok.findings[1].statement,/21-day/);
assert.match(ok.findings[2].statement,/annual/);
assert.ok(ok.page_png_sha256.every(x=>/^[a-f0-9]{64}$/.test(x)));
assert.ok(ok.findings.every(x=>x.page>=1&&x.page<=4));
assert.ok(!('confirmed_vendor' in ok));
for(const modification of [
 x=>{x.document_lifecycle='approved_policy';},
 x=>{x.page_png_sha256[0]='0'.repeat(64);},
 x=>{x.original_sha256='0'.repeat(64);},
 x=>{x.source_url='https://unrelated.example/fake.pdf';},
 x=>{x.adopted=true;},
 x=>{x.camera_count=3;},
 x=>{x.findings[0].page=4;},
 x=>{x.limits='four pages';}
]){
 const x=JSON.parse(JSON.stringify(d));modification(x);
 assert.throws(()=>API.review(x,registry.registrations,held.entries),/Unverified/);
}
console.log('KITTITAS DRAFT REVIEW PASS: four original page images and immutable source; no adopted status or Flock equipment');
