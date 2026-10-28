'use strict';
const assert=require('node:assert/strict');
const App=require('../ri-sd-original-policies.js');
const D=require('../data/verified-ri-sd-original-alpr-policies.json');
const rows=App.catalog(D);
assert.deepEqual(rows.map(x=>x.state),['RI','SD']);
assert.equal(rows[0].source_effective_date,'2026-09-04');
assert.equal(rows[1].source_effective_date,'2026-09-22');
assert.match(rows[0].findings[1].statement,/Flock Safety/);
assert.match(rows[0].findings[1].statement,/30 days/);
assert.match(rows[1].findings[1].statement,/30 days/);
assert.match(rows[1].findings[3].statement,/signature/);
for(const edit of [
 d=>{d.documents[0].source_url='https://evil.example/policy.pdf';},
 d=>{d.documents[0].camera_count=42;},
 d=>{d.documents[1].live_retention_verified=true;},
 d=>{d.documents[1].original_sha256='0'.repeat(64);},
 d=>{d.documents[0].kind='draft_unadopted';},
 d=>{d.documents.pop();}
]){
 const x=JSON.parse(JSON.stringify(D));edit(x);
 assert.throws(()=>App.catalog(x),/Unverified|missing|incomplete/);
}
console.log('RI/SD POLICY VERSIONS PASS: 2026 dated original source-pinned effective Providence and Brookings documents, not camera telemetry');
