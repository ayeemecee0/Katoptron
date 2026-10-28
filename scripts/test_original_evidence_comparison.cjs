'use strict';
const assert=require('node:assert/strict');
const Compare=require('../original-evidence-comparison.js');
const Base=require('../verified-agency-dossiers.js');
const WA=require('../wa-original-agency-dossiers.js');
const base=Base.catalog({
 okc:require('../data/verified-okc-2026-original-flock-contract-review.json'),
 ne:require('../data/verified-nebraska-original-aggregate-reports.json'),
 riSd:require('../data/verified-ri-sd-original-alpr-policies.json'),
 kittitas:require('../data/verified-wa-kittitas-scanned-draft-review.json'),
 waRegistry:require('../data/wa-original-agency-alpr-registrations.json'),
 waHeld:require('../data/wa-held-original-policy-diagnostics.json'),
 national:require('../data/verified-national-government-documents.json')
},{
 okc:require('../okc-original-contracts.js'),
 ne:require('../nebraska-original-aggregate.js'),
 riSd:require('../ri-sd-original-policies.js'),
 kittitas:require('../wa-kittitas-draft-review.js'),
 national:require('../national-primary-documents.js')
});
const wa=WA.catalog({
 flock:require('../data/verified-wa-flock-policy-originals.json'),
 other:require('../data/verified-wa-agency-policies.json'),
 registry:require('../data/wa-original-agency-alpr-registrations.json'),
 receipts:require('../data/wa-ago-original-policy-source-inspection.json')
},{
 flock:require('../wa-reviewed-flock-sources.js'),
 other:require('../wa-original-policies.js')
});
const index=WA.combine(base,wa);
assert.equal(index.agencies,18);
const sample=Compare.compare(index,['providence-police-ri','brookings-police-sd'],'retention');
assert.equal(sample.columns.length,2);
assert.ok(sample.total_matches>=2);
assert.ok(sample.columns.every(c=>c.documents.length&&c.documents[0].findings.every(f=>f.source_page_url.includes('#page='))));
assert.match(sample.columns[0].documents[0].findings[0].statement,/30 days/);
assert.match(sample.columns[1].documents[0].findings[0].statement,/30 days/);
const draft=Compare.compare(index,['kittitas-police-wa','mukilteo-police-wa'],'retention');
assert.equal(draft.columns[0].documents[0].date_basis,'manual_imprint_not_adoption');
assert.equal(draft.columns[1].documents[0].date_basis,'attorney_general_registration_date_not_policy_date');
assert.match(draft.columns[0].documents[0].findings[0].statement,/draft/i);
const green=Compare.compare(index,['green-bay-police-wi','providence-police-ri'],'retention');
assert.equal(green.columns.length,2);
assert.equal(green.columns[0].total_verified_documents,4);
assert.ok(green.columns[0].documents.some(d=>d.kind==='published_department_policy'&&
 d.findings.some(f=>/30-day maximum/i.test(f.statement))));
const draft=green.columns[0].documents.find(d=>d.kind==='draft_policy_unadopted');
assert.equal(draft.date,null);
assert.equal(draft.date_basis,'undated_original_not_verified_effective');
assert.match(draft.date_note,/DRAFT/);
assert.ok(draft.findings.some(f=>/not a verified adopted policy change/.test(f.statement)));
const greenAll=Compare.compare(index,['green-bay-police-wi','moline-police-il'],'all');
assert.ok(greenAll.columns[0].documents.some(d=>d.kind==='government_published_vendor_order_form'&&
 d.date===null&&/not independently confirmed/.test(d.date_note)));
const nuance=Compare.compare(index,['federal-way-police-wa','moline-police-il'],'all');
assert.ok(nuance.columns[0].documents[0].findings.some(f=>/proposed/i.test(f.statement)));
assert.ok(nuance.columns[1].documents.some(d=>d.findings.some(f=>/not (proof|confirmation)/i.test(f.statement))));
const absent=Compare.compare(index,['federal-way-police-wa','dakota-county-sheriff-ne'],'retention');
assert.equal(absent.total_matches,0);
assert.ok(absent.columns.every(c=>c.documents.length===0));
assert.match(absent.evidence_limit,/not no policy or cameras/i);
const three=Compare.compare(index,['providence-police-ri','brookings-police-sd','auburn-police-wa'],'oversight');
assert.equal(three.columns.length,3);
assert.ok(three.total_matches>0);
assert.equal(Compare.sourcePageUrl('https://example.org/doc.pdf?VersionId=abc',4),
 'https://example.org/doc.pdf?VersionId=abc#page=4');
assert.equal(Compare.sourcePageUrl('http://evil.example/file.pdf',1),null);
assert.equal(Compare.sourcePageUrl('https://example.org/a.pdf#already',1),null);
for(const args of [
 [index,['providence-police-ri'],'all'],
 [index,['providence-police-ri','providence-police-ri'],'all'],
 [index,['sultan-police-wa','brookings-police-sd'],'all'],
 [index,['providence-police-ri','brookings-police-sd'],'compliance'],
 [index,['providence-police-ri','brookings-police-sd','auburn-police-wa','moline-police-il'],'all'],
 [{...index,no_live_camera_or_sharing_claims:false},['providence-police-ri','brookings-police-sd'],'all']
 ])assert.throws(()=>Compare.compare(...args),/verified|distinct/i);
const broken=structuredClone(index);
broken.dossiers.find(x=>x.key==='providence-police-ri').documents[0].findings[0].page=120;
assert.throws(()=>Compare.compare(broken,['providence-police-ri','brookings-police-sd']),'Forged original page citation');
const changed=structuredClone(index);
changed.dossiers.find(x=>x.key==='providence-police-ri').documents[0].source_url='https://evil.example/';
changed.dossiers.find(x=>x.key==='providence-police-ri').documents[0].findings[0].page=0;
assert.throws(()=>Compare.compare(changed,['providence-police-ri','brookings-police-sd']));
console.log('ORIGINAL EVIDENCE COMPARISON PASS: 18 verified agency options; source-page scoped topics, drafts, uncertainty, missing findings and invalid attribution held');
