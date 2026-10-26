const assert=require('node:assert/strict');
const A=require('../agency-intelligence.js');
assert.equal(A.locality('Folsom CA PD'),'folsom|CA');
assert.equal(A.locality('Folsom, CA'),'folsom|CA');
assert.equal(A.locality('West Sacramento CA PD'),'west sacramento|CA');
assert.notEqual(A.locality('Sacramento, CA'),A.locality('West Sacramento CA PD'));
assert.equal(A.locality('Placer County CA SO'),'placer county|CA');
assert.equal(A.locality('Unknown'),null);
assert.equal(A.locality('Trophy Club TX PD'),'trophy club|TX');
assert.equal(A.labelForKey('trophy club|TX'),'Trophy Club, TX');
const groups=A.build(
 [{jurisdiction_label:'Folsom, CA',event_date:'2026-09-01',
   event_key:'gov-1',title:'City council agenda',source_url:'https://folsom.ca.gov/record'}],
 [{agency_label:'Folsom CA PD',agency_key:'folsom_ca_pd',source_date:'2026-08-01',
   disclosure_status:'verified_source_snapshot',reported_total_cameras:20,portal_url:'https://transparency.flocksafety.com/folsom-ca-pd'},
  {agency_label:'Folsom CA PD',disclosure_status:'unverified'}],
 [{jurisdiction_label:'West Sacramento, CA',record_key:'valid',
   verification_status:'verified',location_accuracy:'exact'},
  {jurisdiction_label:'Folsom, CA',record_key:'untrusted',
   verification_status:'unverified',location_accuracy:'exact'}],
 [{jurisdiction_label:'Folsom, CA',record_status:'verified'}]
);
const folsom=groups.find(x=>x.key==='folsom|CA');
assert.ok(folsom);
assert.equal(folsom.events.length,1);
assert.equal(folsom.portals.length,1);
assert.equal(folsom.cameras.length,0);
assert.equal(folsom.programs.length,1);
assert.equal(groups.find(x=>x.key==='west sacramento|CA').cameras.length,1);
const activities=A.updateItems(folsom);
assert.equal(activities.length,2);
assert.equal(activities[0].type,'Government record');
assert.equal(activities[1].type,'Vendor disclosure');
assert.equal(A.safeUrl('http://example.org'),null);
assert.equal(A.safeUrl('https://example.org/path'),'https://example.org/path');
assert.equal(A.safeUrl('https://user:pass@example.org'),null);
assert.throws(()=>A.build(null,[],[],[]),/Incomplete/);
console.log('AGENCY INTELLIGENCE PASS: no false merged localities, evidence tiers separate, bounded dated change items');
