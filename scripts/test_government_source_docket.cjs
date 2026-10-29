/* Regression against source-identity drift, fabricated enactment and false camera counts. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const V=require('../government-source-docket.js');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/qualified-original-government-docket-2026-10-29.json')));
const result=V.build(raw);
assert.equal(result.rows.length,14);
assert.equal(result.states.length,6);
assert.equal(result.issuers.length,11);
assert.equal(result.agencies.length,10);
assert.equal(result.byLocality('sacramento county|CA').length,3);
const da=result.get('sacramento-ca-district-attorney-alpr-access-policy-2026');
assert.equal(da.flock_specific,false);
assert.equal(da.kind,'published_policy');
assert.match(da.summary,/does not employ or deploy ALPR readers/);
const sheriff=result.get('sacramento-ca-sheriff-alpr-general-order-2016');
assert.equal(sheriff.source_date,'2016-04');
assert.equal(sheriff.flock_specific,false);
assert.match(sheriff.status,/historical_policy_not_verified_current/);
const filing=result.get('sacramento-ca-ceqa-flock-noe-2025');
assert.equal(filing.kind,'environmental_notice');
assert.match(filing.status,/not_operational_verification/);
const allentown=result.get('allentown-pa-ipvm-15-8653');
assert.equal(allentown.amount_usd,10000);
assert.match(allentown.amount_basis,/NOT a Flock vendor agreement/);
const grand=result.get('south-san-francisco-ca-grand-jury-response-26-2219');
assert.match(grand.summary,/audit data were not archived/);
assert.match(grand.status,/not_final_adoption_verified/);
const elpaso=result.get('el-paso-tx-item-26-1092');
assert.match(elpaso.status,/header_discrepancy/);
for(const r of result.rows){
 assert.equal(r.watch_category,'historical_research_only');
 assert.equal(V.validUrl(r.source_url),true);
 assert.ok(r.proof&&r.summary.length>90);
 assert.ok(r.open_questions.length>=1);
 assert.ok(r.open_questions.every(q=>q.length>20));
 assert.ok(!Object.hasOwn(r,'latitude')&&!Object.hasOwn(r,'longitude'));
}
const mutate=(fn)=>{const clone=JSON.parse(JSON.stringify(raw));fn(clone.sources);return clone};
for(const changed of [
 mutate(rows=>rows[0].source_url='http://malicious.example.com/'),
 mutate(rows=>rows[0].source_url='https://ceqanet.lci.ca.gov.evil.org/2025051277'),
 mutate(rows=>rows[0].status='signed_current_flock_contract'),
 mutate(rows=>rows[0].watch_category='government_decision'),
 mutate(rows=>rows[1].source_date='2016-04-01'),
 mutate(rows=>rows[1].flock_specific='unknown'),
 mutate(rows=>rows.push({...rows[0]})),
 mutate(rows=>rows[5].amount_usd=-1000),
])assert.throws(()=>V.build(changed));
const html=fs.readFileSync(path.join(__dirname,'../agency-xray.html'),'utf8');
assert.match(html,/governmentDocketStatus/);
assert.match(html,/government-source-docket\.js/);
assert.match(html,/renderExactGovSources\(group\.key\)/);
const page=fs.readFileSync(path.join(__dirname,'../government-evidence.html'),'utf8');
assert.match(page,/qualified-original-government-docket-2026-10-29\.json/);
console.log('GOVERNMENT_SOURCE_DOCKET_PASS: 14 issuer-verified records, 10 exact locality profiles, 6 states, historical-vs-adoption boundaries, protected ALPR GPS and email-event boundaries.');
