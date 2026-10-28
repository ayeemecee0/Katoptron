'use strict';
const assert=require('node:assert/strict');
const P=require('../policy-history.js');
const B=require('../verified-agency-dossiers.js');
const W=require('../wa-original-agency-dossiers.js');
function index(){
 const core=B.catalog({
  okc:require('../data/verified-okc-2026-original-flock-contract-review.json'),
  ne:require('../data/verified-nebraska-original-aggregate-reports.json'),
  riSd:require('../data/verified-ri-sd-original-alpr-policies.json'),
  kittitas:require('../data/verified-wa-kittitas-scanned-draft-review.json'),
  waRegistry:require('../data/wa-original-agency-alpr-registrations.json'),
  waHeld:require('../data/wa-held-original-policy-diagnostics.json'),
  national:require('../data/verified-national-government-documents.json')
 },{
  okc:require('../okc-original-contracts.js'),ne:require('../nebraska-original-aggregate.js'),
  riSd:require('../ri-sd-original-policies.js'),
  kittitas:require('../wa-kittitas-draft-review.js'),
  national:require('../national-primary-documents.js')
 });
 const data={
  flock:require('../data/verified-wa-flock-policy-originals.json'),
  other:require('../data/verified-wa-agency-policies.json'),
  registry:require('../data/wa-original-agency-alpr-registrations.json'),
  receipts:require('../data/wa-ago-original-policy-source-inspection.json')
 };
 return W.combine(core,W.catalog(data,{
  flock:require('../wa-reviewed-flock-sources.js'),
  other:require('../wa-original-policies.js')
 }));
}
const validated=index();
assert.equal(validated.agencies,18);
const history=P.catalog(validated);
assert.ok(history.original_policy_documents>=12);
assert.ok(history.agency_count>=12);
assert.equal(history.comparisons.length,1);
const green=history.agencies.find(x=>x.key==='green-bay-police-wi');
assert.ok(green);
assert.equal(green.documents.length,2,'Activity report and vendor order cannot masquerade as policy versions');
const pair=history.comparisons[0];
assert.equal(pair.status,'proposed_not_adopted');
assert.equal(pair.agency_key,'green-bay-police-wi');
assert.equal(pair.old.date,'2026-05-04');
assert.equal(pair.proposed.date,null);
assert.match(pair.proposed.date_note,/DRAFT/i);
assert.match(pair.old.statement,/30-day maximum/);
assert.match(pair.proposed.statement,/seven days/);
assert.match(pair.interpretation,/not proof of adoption/);
assert.ok(pair.old.source_page.endsWith('#page=2'));
assert.ok(pair.proposed.source_page.endsWith('#page=4'));
assert.notEqual(pair.old.sha,pair.proposed.sha);
assert.ok(!green.documents.some(x=>/vendor_order_form|monthly_aggregate/.test(x.kind)));
assert.ok(!history.agencies.some(x=>x.key.includes('sultan')));
const kittitas=history.agencies.find(x=>x.key==='kittitas-police-wa');
assert.ok(kittitas?.documents.every(d=>d.status==='draft_unadopted'));
assert.equal(P.sourcePage('https://example.org/a.pdf?VersionId=abc',5),
 'https://example.org/a.pdf?VersionId=abc#page=5');
assert.equal(P.sourcePage('http://example.org/a.pdf',1),null);
assert.equal(P.sourcePage('https://example.org/a.pdf#page=1',1),null);
const empty=P.validateStore(null);
assert.deepEqual(P.updates(empty,green),[]);
const followed=P.follow(empty,green);
assert.equal(followed.follows.length,1);
assert.equal(P.updates(followed,green).length,0,'Initial follow must not replay historical sources');
const repeated=P.follow(followed,green);
assert.equal(repeated.follows.length,1);
const newly=structuredClone(green);
newly.documents.push({...newly.documents[0],id:'new-published-version',
 sha:'e'.repeat(64)});
const updates=P.updates(followed,newly);
assert.equal(updates.length,1);
assert.equal(updates[0].id,'new-published-version');
const seen=P.markReviewed(followed,newly);
assert.equal(P.updates(seen,newly).length,0);
assert.equal(P.updates(P.unwatch(seen,green.key),newly).length,0);
const malformed=structuredClone(validated);
malformed.dossiers.find(a=>a.key==='green-bay-police-wi').documents.find(d=>d.kind==='draft_policy_unadopted').kind='published_department_policy';
assert.throws(()=>P.catalog(malformed),/Proposed policy|Original policy/);
const forged=structuredClone(validated);
forged.dossiers.find(a=>a.key==='green-bay-police-wi').documents.find(d=>d.kind==='draft_policy_unadopted').source_url='http://unsafe.example.org/doc';
assert.throws(()=>P.catalog(forged),/Original policy document/);
const badDate=structuredClone(validated);
badDate.dossiers.find(a=>a.key==='green-bay-police-wi').documents.find(d=>d.kind==='draft_policy_unadopted').date='2026-09-13';
assert.throws(()=>P.catalog(badDate),/Original policy|Proposed policy/);
const wrongPage=structuredClone(validated);
wrongPage.dossiers.find(a=>a.key==='green-bay-police-wi').documents.find(d=>d.kind==='draft_policy_unadopted').findings[0].page=44;
assert.throws(()=>P.catalog(wrongPage),/Original policy document/);
const fakeStore=P.validateStore({schema:1,follows:['unsafe|CA'],seen:{'unsafe|CA':['bad']}});
assert.deepEqual(fakeStore.follows,[]);
console.log('POLICY HISTORY PASS: verified policy catalog, Green Bay published vs DRAFT distinction, original page links, on-device non-replay and tamper rejection');
