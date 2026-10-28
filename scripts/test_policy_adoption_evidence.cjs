'use strict';
const assert=require('node:assert/strict');
const E=require('../policy-adoption-evidence.js');
const raw=require('../data/verified-policy-adoption-status-2026-10-27.json');
const value=E.validate(raw);
assert.equal(value.records.length,2);
assert.equal(value.government_actions_adopted,1);
assert.equal(value.published_unadopted_drafts,1);
const apache=value.records.find(r=>r.state==='AZ');
const green=value.records.find(r=>r.state==='WI');
assert.ok(apache);
assert.equal(apache.event_date,'2026-10-06');
assert.equal(apache.effective_date,null,'An empty effective-date field cannot be inferred from adoption');
assert.equal(apache.evidence_category,'official_government_HTML_source_listing_or_clerk_notice');
assert.equal(apache.source_document_page_reviewed,false,
 'Do not inflate source-page-verified PDF totals');
assert.match(apache.summary,/City Clerk/);
assert.match(green.summary,/not of enacted seven-day retention/);
assert.equal(green.event_date,null,'Draft listing review is not policy adoption');
assert.equal(green.effective_date,null);
assert.equal(green.status,'draft_published_no_adoption_verified');
assert.equal(green.reviewed_on,'2026-10-27');
function mutate(edit,expression){
 const fake=structuredClone(raw);edit(fake);
 assert.throws(()=>E.validate(fake),expression);
}
mutate(d=>d.records[0].effective_date='2026-10-06',/source action|authority|date basis/);
mutate(d=>d.records[0].status='adopted_effective',/source event date|status/);
mutate(d=>d.records[1].status='adopted_government_original_notice',/source event date|status/);
mutate(d=>d.records[1].event_date='2026-09-13',/source event date|status/);
mutate(d=>d.records[0].source_url='https://attacker.test/false',/authority/);
mutate(d=>d.records[0].corroboration_url='http://apachejunctionaz.gov/1241/Public-Safety-Technology',/authority/);
mutate(d=>d.records[0].limits='Enforced in the camera settings today',/authority/);
mutate(d=>d.records[1].proof='Adopted!',/authority/);
mutate(d=>d.records.push(structuredClone(d.records[0])),/incomplete|duplicate/);
mutate(d=>d.reviewed_on='2027-01-01',/date unverified/);
console.log('GOVERNMENT ACTION STATUS PASS: authenticated official city clerk adoption, unadopted draft listing, no effective-date inference, original PDF count separation, forged sources held');
