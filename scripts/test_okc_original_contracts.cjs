'use strict';
const assert=require('node:assert/strict');
const API=require('../okc-original-contracts.js');
const DATA=require('../data/verified-okc-2026-original-flock-contract-review.json');
const reviewed=API.catalog(DATA);
assert.equal(reviewed.documents.length,4);
assert.equal(reviewed.cityReport.city_2026_flock_readers_reported,90);
assert.equal(reviewed.cityReport.partner_agencies_reported_as_of_2026_08_18,109);
assert.equal(reviewed.cityReport.reported_default_data_retention_days,7);
assert.equal(reviewed.documents[0].pages_visually_reviewed.length,2);
assert.match(reviewed.documents[0].findings[0].statement,/prohibits Flock from voluntarily/);
assert.match(reviewed.documents[0].findings[1].statement,/legally compelled/);
assert.match(reviewed.documents[0].findings[2].statement,/August 18, 2026/);
assert.match(reviewed.documents[1].findings[0].statement,/does not prove that all contract payments/);
assert.match(reviewed.documents[2].findings[0].statement,/not a final vote/);
assert.match(reviewed.documents[3].findings[0].statement,/not proof that \$270,000 was spent/);
for(const edit of [
 d=>{d.documents[0].status='unsigned_template';},
 d=>{d.documents[2].status='council_approved_vote';},
 d=>{d.documents[0].png_sha256_by_page['2']='0'.repeat(64);},
 d=>{d.documents[0].verified_camera_coordinates=[[1,2]];},
 d=>{d.documents[1].source_sha256='0'.repeat(64);},
 d=>{d.city_self_report.partner_agencies_reported_as_of_2026_08_18=400;},
 d=>{d.documents.pop();}
]){
 const d=JSON.parse(JSON.stringify(DATA));edit(d);
 assert.throws(()=>API.catalog(d),/Original|incomplete|improperly|changed|Missing/);
}
console.log('OKC 2026 ORIGINAL CONTRACTS PASS: signed amendment vs approved renewal vs staff memo vs fund certification; source-pinned pages and city self-report limits');
