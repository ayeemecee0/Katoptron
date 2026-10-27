'use strict';
const assert=require('node:assert/strict');
const D=require('../data/verified-nebraska-original-aggregate-reports.json');
const API=require('../nebraska-original-aggregate.js');
const r=API.catalog(D);
assert.equal(r.document.metrics.ncic_confirmed_matches,43);
assert.equal(r.document.metrics.ncic_noncorrelated_matches,0);
assert.equal(r.document.metrics.manual_plate_numbers_entered,126);
assert.equal(r.document.metrics.manual_entry_confirmed_matches,19);
assert.equal(r.document.metrics.manual_entry_noncorrelated_matches,1);
assert.equal(r.held.can_publish_numeric_findings,false);
assert.match(r.document.vendor_status,/manufacturer_not_proven/);
for(const fn of [
 d=>{d.documents[0].metrics.ncic_confirmed_matches=90;},
 d=>{d.documents[0].source_sha256='0'.repeat(64);},
 d=>{d.documents[0].camera_coordinates=[2,1];},
 d=>{d.held_unverified_originals[0].can_publish_numeric_findings=true;},
 d=>{d.documents[0].report_end='2026-12-31';}
]){
 const altered=JSON.parse(JSON.stringify(D));fn(altered);
 assert.throws(()=>API.catalog(altered),/Unverified/);
}
console.log('NEBRASKA 2025 AGGREGATE PASS: source-pinned Dakota only; Buffalo blank held; no vendor or camera counts');
