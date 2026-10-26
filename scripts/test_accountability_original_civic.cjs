const assert=require('node:assert/strict');
const A=require('../accountability-original.js');
const gov='https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf';
const base={
 milestone_key:'bellevue_id_resolution_25_11_2025_03_24',
 jurisdiction_label:'Bellevue, ID',event_type:'recorded_governing_body_decision',
 event_date:'2025-03-24',date_basis:'original_city_recorded_action_date',
 title:'Bellevue recorded Flock Safety authorizing vote',
 summary:'Original approved minutes documented a vote, not an executed contract or camera deployment.',
 source_url:gov,amount_usd:null,amount_basis:null,
 evidence_tier:'original_government_reviewed'
};
const rows=A.normalizeCivic([base]);
assert.equal(rows.length,1);
assert.equal(rows[0].event_key,'original_civic:'+base.milestone_key);
assert.equal(rows[0].state_code,'ID');
assert.equal(rows[0].event_type,'recorded_legislative_decision');
assert.equal(rows[0].event_date,'2025-03-24');
assert.equal(rows[0].amount_usd,null);
assert.equal(rows[0].person_label,null,
 'Original council outcome cannot imply any named official vote');
assert.equal(A.normalizeCivic([{...base,evidence_tier:'search_result_only'}]).length,0);
assert.equal(A.normalizeCivic([{...base,source_url:'https://flock.example/summary'}]).length,0);
assert.equal(A.normalizeCivic([{...base,source_url:'http://bellevueidaho.gov/unsafe'}]).length,0);
assert.equal(A.normalizeCivic([{...base,amount_usd:13300}]).length,0,
 'Authorization ceiling is NOT automatically executed contract value');
assert.equal(A.normalizeCivic([{...base,event_date:'2025-02-31'}]).length,0);
assert.equal(A.normalizeCivic([{...base,date_basis:'date_not_reported'}]).length,0);
const estimate={
 ...base,milestone_key:'valid_undated_estimate',
 event_type:'government_reported_estimate',
 event_date:null,date_basis:'date_not_reported',
 amount_usd:165900,amount_basis:'government_estimate_not_executed_contract'
};
const [row]=A.normalizeCivic([estimate]);
assert.equal(row.event_type,'original_government_estimate');
assert.equal(row.event_date,null);
assert.equal(row.amount_usd,165900);
assert.equal(A.normalizeCivic([{...estimate,amount_basis:'executed_contract'}]).length,0);
assert.equal(A.normalizeCivic([{...estimate,event_date:'2025-01-01'}]).length,0);
assert.throws(()=>A.normalizeCivic(null),/unavailable/);
console.log('M6 PASS: original government decision normalization, date/source integrity, and estimate-vs-contract separation');
