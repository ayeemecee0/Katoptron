'use strict';
const assert=require('node:assert/strict');
const D=require('../verified-agency-dossiers.js');
const validators={
 okc:require('../okc-original-contracts.js'),
 ne:require('../nebraska-original-aggregate.js'),
 riSd:require('../ri-sd-original-policies.js'),
 kittitas:require('../wa-kittitas-draft-review.js'),
 national:require('../national-primary-documents.js')
};
const files={
 okc:require('../data/verified-okc-2026-original-flock-contract-review.json'),
 ne:require('../data/verified-nebraska-original-aggregate-reports.json'),
 riSd:require('../data/verified-ri-sd-original-alpr-policies.json'),
 kittitas:require('../data/verified-wa-kittitas-scanned-draft-review.json'),
 waRegistry:require('../data/wa-original-agency-alpr-registrations.json'),
 waHeld:require('../data/wa-held-original-policy-diagnostics.json'),
 national:require('../data/verified-national-government-documents.json')
};
const index=D.catalog(files,validators);
assert.equal(index.agencies,7);
assert.equal(index.original_documents,14);
assert.ok(index.findings>=20);
assert.equal(index.no_live_camera_or_sharing_claims,true);
const okc=D.byKey(index,'oklahoma-city-ok');
assert.equal(okc.documents.length,4);
assert.match(okc.documents[0].title,/Flock master agreement/);
assert.equal(okc.documents[0].date,'2026-08-18');
assert.equal(okc.state,'OK');
assert.ok(okc.documents.some(x=>x.kind==='original_staff_recommendation_not_vote_record'));
assert.ok(okc.documents.some(x=>x.kind==='signed_availability_of_funds_certification_not_payment'));
assert.ok(okc.documents.some(x=>x.findings.some(f=>/city itself from sharing/i.test(f.statement))));
const moline=D.byKey(index,'moline-police-il');
assert.equal(moline.documents.length,2);
assert.equal(moline.documents[0].date,'2026-09-15');
assert.equal(moline.documents[1].date,'2024-12-04');
assert.match(moline.documents[0].kind,/pause/);
assert.ok(moline.documents[0].findings.some(f=>/not confirmation/i.test(f.statement)||/not proof/i.test(f.statement)));
const green=D.byKey(index,'green-bay-police-wi');
assert.equal(green.documents.length,4);
assert.equal(green.agency,'Green Bay Police Department');
assert.ok(green.documents.some(d=>d.kind==='agency_monthly_aggregate_report'&&d.findings.some(f=>/443,664/.test(f.statement))));
assert.ok(green.documents.some(d=>d.kind==='published_department_policy'&&d.findings.some(f=>/30-day maximum/.test(f.statement))));
assert.ok(green.documents.some(d=>d.kind==='draft_policy_unadopted'&&d.date===null&&
 d.date_basis==='undated_original_not_verified_effective'&&/DRAFT/.test(d.date_note)));
assert.ok(green.documents.some(d=>d.kind==='government_published_vendor_order_form'&&d.date===null&&
 /not independently confirmed/.test(d.date_note)));
assert.match(green.notes.join(' '),/not known to be adopted/);
const draft=D.byKey(index,'kittitas-police-wa');
assert.equal(draft.documents[0].kind,'draft_not_proven_adopted');
assert.equal(draft.documents[0].date_basis,'manual_imprint_not_adoption');
const ne=D.byKey(index,'dakota-county-sheriff-ne');
assert.equal(ne.documents[0].date_basis,'report_period_end_not_publication');
assert.match(ne.documents[0].findings[0].statement,/43 NCIC confirmed matches/);
assert.ok(index.dossiers.every(r=>r.documents.every(d=>
 d.findings.every(f=>d.pages.includes(f.page)&&D.checkUrl(d.source_url)))));
assert.equal(D.byKey(index,'dakota-county-ok'),null);
for(const fn of [
 x=>{x.okc.documents[0].status='unapproved_staff_draft';},
 x=>{x.okc.documents[0].verified_camera_coordinates=[[35,-97]];},
 x=>{x.ne.documents[0].metrics.ncic_confirmed_matches=1000;},
 x=>{x.riSd.documents[0].source_url='https://evil.example/policy';},
 x=>{x.kittitas.document_lifecycle='adopted';},
 x=>{x.waHeld.entries.find(r=>r.agency_name==='Kittitas Police Department').source_url='https://evil.example/';},
 x=>{x.national.documents.find(r=>r.id==='moline-il-signed-pause-2026').status='deactivation_completed';}
]){
 const tampered=JSON.parse(JSON.stringify(files));fn(tampered);
 assert.throws(()=>D.catalog(tampered,validators),/original|Unverified|government|mismatch|invalid|Missing|changed|improperly|not|held/i);
}
console.log('AGENCY X-RAY ORIGINAL DOSSIERS PASS: 7 exact agencies / 14 page-reviewed source documents, no camera or sharing upgrades');
