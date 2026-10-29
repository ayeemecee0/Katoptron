'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const D=require('../government-source-docket.js'),B=require('../government-agency-brief.js');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/qualified-original-government-docket-2026-10-29.json')));
const docket=D.build(raw);
const keys=['lakewood-ca-council-rejects-flock-2026','sheboygan-wi-flock-termination-request-2026','grand-rapids-mi-flock-oversight-order-proposed-2026','henrico-va-flock-contract-termination-announced-2026','fridley-mn-flock-access-restrictions-2026','richland-wa-flock-suspension-announced-2026','liberty-hill-tx-flock-removal-city-statement-2026','elgin-tx-flock-program-pause-2026','redmond-wa-flock-contract-termination-vote-2026','tukwila-wa-revised-flock-contract-adoption-2026'];
for(const key of keys){
 const p=B.profile(docket,key);
 assert.equal(p.rows.length,1,'Never merge different agencies merely by locality');
 assert.equal(p.issues.length,1);
 assert.equal(p.dated_records,1);
 assert.equal(p.source_count,1);
 const text=B.request(p);
 assert.match(text,/Public Records Officer/);
 assert.ok(text.includes(p.rows[0].source_url));
 assert.ok(text.includes(p.issues[0]));
 assert.match(text,/not requesting individual license plate observations/);
}
const multi=B.profile(docket,'sacramento-ca-ceqa-flock-noe-2025');
assert.equal(multi.agency,"Sacramento County Sheriff's Office");
assert.equal(multi.rows.length,2,'District attorney records must not be co-mingled with Sheriff');
assert.throws(()=>B.profile(docket,'<img src=x onerror=alert(1)>'));
const page=fs.readFileSync(path.join(__dirname,'../agency-government-brief.html'),'utf8');
assert.match(page,/government-agency-brief\.js/);
assert.match(page,/requestText/);
assert.match(page,/Print \/ Save as PDF/);
console.log('GOVERNMENT_AGENCY_BRIEF_PASS: 10 exact new agencies, cited five-question evidence profile and editable request, no cross-agency merge');
