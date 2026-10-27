'use strict';
const assert=require('node:assert/strict');
const API=require('../wa-held-original-diagnostics.js');
const d=require('../data/wa-held-original-policy-diagnostics.json');
const registry=require('../data/wa-original-agency-alpr-registrations.json');
const receipts=require('../data/wa-ago-original-policy-source-inspection.json');
const entries=API.catalog(d,registry.registrations,receipts.receipts);
assert.equal(entries.length,7);
assert.equal(entries.filter(x=>x.diagnosis==='empty_page_content_streams').length,3);
assert.equal(entries.filter(x=>x.sha256_complete_original!==null).length,6);
assert.equal(entries.find(x=>x.agency_name==='Kittitas Police Department').page_count_structurally_readable,4);
assert.equal(entries.find(x=>x.agency_name==='Yakima Police Department').page_count_structurally_readable,738);
assert.equal(entries.find(x=>x.agency_name==='Kirkland Police Department').minimum_observed_bytes,16000001);
assert.match(API.label('empty_page_content_streams'),/no extractable content/);
assert.ok(entries.every(x=>!x.policy_page_content_verified&&!x.flock_vendor_confirmed&&!x.device_location_published));
for(const modify of [
 d=>{d.entries[0].sha256_complete_original='0'.repeat(64);},
 d=>{d.entries[0].page_count_structurally_readable=100;},
 d=>{d.entries[0].source_url='https://example.invalid/fake.pdf';},
 d=>{d.entries[0].policy_page_content_verified=true;},
 d=>{d.entries[0].operational_status='active';},
 d=>{d.entries[0].diagnosis='independently_verified_flock_installation';},
 d=>{d.entries.pop();}
]){
 const altered=JSON.parse(JSON.stringify(d));modify(altered);
 assert.throws(()=>API.catalog(altered,registry.registrations,receipts.receipts),/unverified|Unverified|incomplete|content claim/i);
}
console.log('WA HELD POLICY DIAGNOSTICS PASS: seven source-bound structural failure categories and no policy or Flock promotion');
