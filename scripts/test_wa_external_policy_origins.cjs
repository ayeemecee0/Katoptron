'use strict';
const assert=require('node:assert/strict');
const API=require('../wa-external-policy-origins.js');
const data=require('../data/wa-ag-external-policy-source-inspection.json');
const reg=require('../data/wa-original-agency-alpr-registrations.json');
const d=API.catalog(data,reg.registrations);
assert.equal(d.total,25);
assert.equal(d.uniqueLinks,24);
assert.equal(d.counts.retrieved,14);
assert.equal(d.counts.held,11);
assert.equal(d.counts.pdf,4);
assert.equal(d.counts.html,10);
assert.ok(d.rows.every(r=>r.manufacturer_identity_assertion===false));
assert.ok(d.rows.every(r=>r.installed_equipment_assertion===false));
assert.ok(d.rows.every(r=>r.camera_coordinates_assertion===false));
const diamond=d.rows.find(x=>x.agency_name==='Black Diamond Police Department');
assert.equal(diamond.content_sha256,'8ccf182125bf61bc624be72cb389f5ce218d36cf60f9db62d5ba8d58418f2446');
const king=d.rows.find(x=>x.agency_name==="King County Sheriff's Office");
const maple=d.rows.find(x=>x.agency_name==='Maple Valley Police Department');
assert.equal(king.policy_source_url,maple.policy_source_url);
assert.match(API.label('held_redirect'),/redirect/i);
for(const bad of ['https://evil.example/','http://www.pasco-wa.gov/DocumentCenter/View/123',
 'https://www.pasco-wa.gov.evil.example/DocumentCenter/',
 'https://www.pasco-wa.gov/../private','https://www.pasco-wa.gov/path#fragment']){
 assert.equal(API.exact(bad),false,bad);
}
function tamper(fn){
 const x=JSON.parse(JSON.stringify(data));fn(x);
 assert.throws(()=>API.catalog(x,reg.registrations),/Unreviewed|provenance|facts|invalid|verified|count|source|AGO|PDF|HTML/i);
}
tamper(x=>{x.receipts[0].policy_source_url='https://evil.example.pdf';});
tamper(x=>{x.receipts[0].manufacturer_identity_assertion=true;});
tamper(x=>{x.receipts[0].camera_coordinates_assertion=true;});
tamper(x=>{x.receipts[0].content_sha256='0'.repeat(63);});
tamper(x=>{x.receipts.pop();});
const held=d.rows.find(x=>x.inspection_status.startsWith('held'));
tamper(x=>{x.receipts.find(r=>r.agency_name===held.agency_name).content_sha256='0'.repeat(64);});
console.log('WA EXTERNAL 25 LINKS PASS: 14 retrieved, 11 held, 24 unique URLs; no vendor or camera implications');
