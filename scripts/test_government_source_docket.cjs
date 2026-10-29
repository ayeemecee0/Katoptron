/* Regression against source-identity drift, fabricated enactment and false camera counts. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const V=require('../government-source-docket.js');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/qualified-original-government-docket-2026-10-29.json')));
const result=V.build(raw);
assert.equal(result.rows.length,48);
assert.equal(result.states.length,18);
assert.equal(result.issuers.length,43);
assert.equal(result.agencies.length,42);
assert.equal(result.byLocality('sacramento county|CA').length,3);
for(const id of ['woodland-ca-police-alpr-faq-2026','san-diego-ca-sdpd-annual-alpr-audit-report-2025','houston-tx-flock-contract-agenda-2022','pasadena-ca-council-flock-report-directive-2026']){
 const record=result.get(id);assert.ok(record,'Pilot original missing: '+id);
 assert.equal(record.watch_category,'historical_research_only');
 assert.ok(record.open_questions.length>=2);
 assert.ok(!('latitude' in record)&&!('longitude' in record));
}
assert.equal(result.get('houston-tx-flock-contract-agenda-2022').amount_usd,6390000);
assert.match(result.get('houston-tx-flock-contract-agenda-2022').amount_basis,/NOT verified actual expenditure/);
assert.match(result.get('san-diego-ca-sdpd-annual-alpr-audit-report-2025').status,/not_independent_audit/);
for(const key of ['groton-ma-official-flock-contract-termination-2026',
 'shaker-heights-oh-flock-signed-amendment-announcement-2026',
 'la-crosse-wi-police-flock-end-contract-statement-2026',
 'sun-prairie-wi-flock-nonrenewal-city-statement-2026',
 'methuen-ma-city-flock-removal-pending-statement-2026']){
 const evidence=result.get(key);
 assert.ok(evidence,'New exact government original absent: '+key);
 assert.equal(evidence.watch_category,'historical_research_only');
 assert.equal(evidence.source_type,'government_hosted_primary_html');
 assert.equal(evidence.amount_usd,null);
}
for(const key of ['lakewood-ca-council-rejects-flock-2026','sheboygan-wi-flock-termination-request-2026','grand-rapids-mi-flock-oversight-order-proposed-2026','henrico-va-flock-contract-termination-announced-2026','fridley-mn-flock-access-restrictions-2026','richland-wa-flock-suspension-announced-2026','liberty-hill-tx-flock-removal-city-statement-2026','elgin-tx-flock-program-pause-2026','redmond-wa-flock-contract-termination-vote-2026','tukwila-wa-revised-flock-contract-adoption-2026']){
 const row=result.get(key);
 assert.ok(row,'New separately sourced government agency absent: '+key);
 assert.equal(row.watch_category,'historical_research_only');
 assert.equal(row.amount_usd,null);
 assert.ok(row.source_type==='government_hosted_primary');
}
for(const key of ["mill-valley-ca-flock-alpr-disabled-government-statement-2026","richmond-va-flock-nonrenewal-mayor-announcement-2026","panama-city-beach-fl-police-flock-suspension-2026","fort-wayne-in-flock-discontinuation-chief-statement-2026"]){const item=result.get(key);assert.ok(item);assert.equal(item.watch_category,'historical_research_only');assert.equal(item.amount_usd,null);}
assert.ok(result.get('lynchburg-va-flock-alpr-pause-police-original-2026'));
for(const key of ['frankfort-ky-flock-nonrenewal-commission-vote-2026','north-salt-lake-ut-flock-contract-agenda-2025','missouri-mo-alpr-executive-order-26-18-2026','apache-junction-az-public-safety-ordinance-1579-2026','durango-co-flock-to-axon-planned-transition-2026','salem-ma-flock-nonrenewal-mayor-statement-2026']){const record=result.get(key);assert.ok(record);assert.equal(record.watch_category,'historical_research_only');assert.equal(record.amount_usd,null);}
const commerceBudget=result.get('commerce-city-co-flock-budget-ord-2756-first-reading-2026');
assert.equal(commerceBudget.amount_usd,608900);
assert.match(commerceBudget.amount_basis,/not a paid invoice/);
assert.equal(commerceBudget.watch_category,'historical_research_only');
const commerce=result.get('commerce-city-co-flock-ord-2755-first-reading-2026');
assert.equal(commerce.status,'ordinance_first_reading_passed_not_final_adoption');
assert.equal(commerce.watch_category,'historical_research_only');
assert.match(commerce.summary,/not final approval/);
const toledo=result.get('toledo-oh-resolution-r-435-26');
assert.equal(toledo.status,'resolution_held_in_council_not_adopted');
assert.equal(toledo.watch_category,'historical_research_only');
assert.match(toledo.summary,/Neither termination nor approval/);
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
const mantecaReport=result.get('manteca-ca-flock-program-presentation-26-448');
assert.equal(mantecaReport.file_number,'26-448');
assert.match(mantecaReport.summary,/not an independent audit/);
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
console.log('GOVERNMENT_SOURCE_DOCKET_PASS: 48 original issuer records, 42 exact locality profiles, 18 states, historical-vs-adoption boundaries, protected ALPR GPS and email-event boundaries.');
