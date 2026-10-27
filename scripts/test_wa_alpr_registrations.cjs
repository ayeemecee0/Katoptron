'use strict';
const assert=require('node:assert/strict');
const W=require('../wa-alpr-registrations.js');
const d=require('../data/wa-original-agency-alpr-registrations.json');
const rows=W.catalog(d);
assert.equal(d.source_url,'https://www.atg.wa.gov/ALPR');
assert.equal(rows.length,97);
assert.equal(rows.filter(x=>x.policy_links_from_official_ago_page.length).length,96);
assert.equal(rows.filter(x=>!x.submitted_on).length,1);
assert.ok(rows.every(x=>x.registry_status==='agency_self_certification_listed_by_state_AG_not_independently_verified'));
assert.ok(rows.every(x=>x.policy_links_from_official_ago_page.every(u=>W.safe(u)===u)));
assert.equal(new Set(rows.map(x=>x.agency_name.toLowerCase())).size,97);
assert.ok(rows.every(x=>!('flock_vendor' in x)&&!('camera_count' in x)&&!('latitude' in x)&&!('longitude' in x)));
assert.ok(rows.some(x=>x.agency_name==='Aberdeen Police Department'));
assert.ok(rows.some(x=>x.agency_name==='Cascadia College'));
for(const x of ['http://agportal-s3bucket.s3.us-west-2.amazonaws.com/x.pdf',
 'https://agportal-s3bucket.s3.us-west-2.amazonaws.com.evil.example/file',
 'https://127.0.0.1/private','javascript:alert(1)',
 'https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/x.pdf?admin=1']){
 assert.equal(W.safe(x),null);
}
assert.throws(()=>W.catalog({...d,registrations:[...rows.slice(0,96),rows[0]]}),/Unverified/);
assert.throws(()=>W.catalog({...d,flock_vendor_assertions_published:1}),/Unverified/);
assert.throws(()=>W.catalog({...d,source_url:'https://evil.example/alpr'}),/Unverified/);
console.log('WASHINGTON ALPR OFFICIAL REGISTRY PASS: 97 original public agency self-certifications, 96 policy sources, dates, no implied Flock devices or GPS, strict public links');
