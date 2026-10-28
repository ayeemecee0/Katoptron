'use strict';
const assert=require('node:assert/strict');
const API=require('../ny-wv-original-events.js');
const D=require('../data/verified-ny-wv-original-flock-events.json');
const r=API.catalog(D);
assert.equal(r.length,4);
assert.deepEqual(r.map(x=>x.state),['NY','NY','WV','WV']);
assert.match(r[0].findings[0].statement,/July 2025/);
assert.match(r[0].findings[1].statement,/National Search/);
assert.match(r[1].findings[0].statement,/12–1/);
assert.match(r[1].findings[1].statement,/does not independently establish/);
assert.match(r[2].findings[0].statement,/not a legislative vote/);
assert.match(r[3].findings[1].statement,/not proof of a passed bill/);
for(const mutate of [
 d=>{d.records[0].source_page_png_sha256='0'.repeat(64);},
 d=>{d.records[0].operational_camera_count=12;},
 d=>{d.records[1].finished_camera_removal_verified=true;},
 d=>{d.records[1].source_date='2026-04-07';},
 d=>{d.records[2].enacted_wv_flock_statute=true;},
 d=>{d.records[3].status='passed_binding_law';},
 d=>{d.records.pop();}
]){
 const d=JSON.parse(JSON.stringify(D));mutate(d);
 assert.throws(()=>API.catalog(d),/Unverified|Incomplete|altered|incomplete/);
}
console.log('NY/WV ORIGINAL GOVERNMENT EVENTS PASS: 2025 active self report precedes 2026 approved termination; WV hearing not law or camera program');
