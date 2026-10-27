'use strict';
const assert=require('node:assert/strict');
const API=require('../wa-policy-source-triage.js');
const source=require('../data/wa-ago-original-policy-source-inspection.json');
const registry=require('../data/wa-original-agency-alpr-registrations.json');
const d=API.catalog(source,registry.registrations);
assert.equal(d.total,71);
assert.equal(d.counts.parsed,64);
assert.equal(d.counts.held,7);
assert.equal(d.counts.candidates,10);
assert.equal(d.receipts.filter(r=>r.inspection_status==='exact_pdf_text_detected').length,63);
assert.equal(d.receipts.filter(r=>r.inspection_status==='exact_pdf_scan_only').length,1);
assert.ok(d.receipts.every(r=>r.manufacturer_identity_assertion===false&&r.camera_coordinates_asserted===false));
assert.equal(d.byAgency.get('Normandy Park Police Department').potential_flock_term_pages.join(','),'1,3');
assert.equal(d.byAgency.get('Auburn Police Department').sha256,
 '484830933e46300a5471d3fccc4354f33ae1b683bc8401fa938b8a4d3f53863f');
assert.equal(API.exact('https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/A.pdf?VersionId=longVersion122333'),true);
for(const url of ['https://evil.example/ALPR/A.pdf?VersionId=longVersion122333',
 'https://agportal-s3bucket.s3.us-west-2.amazonaws.com.evil/ALPR/A.pdf?VersionId=longVersion122333',
 'https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/../A.pdf?VersionId=longVersion122333',
 'https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/A.pdf?VersionId=longVersion122333#page=1']){
 assert.equal(API.exact(url),false,url);
}
const idx=d.receipts.findIndex(r=>r.agency_name==='Arlington Police Department');
const forged=JSON.parse(JSON.stringify(source));
forged.receipts[idx].manufacturer_identity_assertion=true;
assert.throws(()=>API.catalog(forged,registry.registrations),/tampering/);
const forgedSource=JSON.parse(JSON.stringify(source));
forgedSource.receipts[idx].policy_source_url='https://evil.example/fake.pdf';
assert.throws(()=>API.catalog(forgedSource,registry.registrations),/tampering/);
const forgedHash=JSON.parse(JSON.stringify(source));
forgedHash.receipts[idx].sha256='0';
assert.throws(()=>API.catalog(forgedHash,registry.registrations),/Invalid/);
const fakeHeld=JSON.parse(JSON.stringify(source));
const held=fakeHeld.receipts.find(x=>x.inspection_status.startsWith('held'));
held.sha256='a'.repeat(64);
assert.throws(()=>API.catalog(fakeHeld,registry.registrations),/Held/);
assert.equal(API.receiptLabel(d.byAgency.get('Auburn Police Department')).includes('not automatically verified'),true);
assert.equal(API.receiptLabel(d.byAgency.get('Kelso Police Department')).startsWith('Source retrieval held'),true);
console.log('WA AGO 71 SOURCE TRIAGE PASS: 64 parsed; 7 held; 10 unreviewed Flock keyword leads; no vendor assertions');
