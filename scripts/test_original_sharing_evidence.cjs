const assert=require('node:assert/strict');
const A=require('../agency-original-sharing.js');
const record={
 source_key:'elk_grove_original_government',
 source_agency_id:'elk-grove-ca-pd',
 publisher_name:'Elk Grove Police Department',
 source_url:'https://elkgrove.gov/traffic/automated-license-plate-readers-alpr',
 source_kind:'original_government',source_section:'External agencies who EGPD shares Flock ALPR data with',
 captured_scope:'complete_published_list',
 source_observed_on:'2026-10-25',recipient_observed_on:'2026-10-25',
 recipient_label:'Folsom CA PD',recipient_source_agency_id:'folsom-ca-pd',
 identity_basis:'exact_source_agency_name',source_status:'publisher_named_as_of_observation'
};
const unresolved={...record,recipient_label:'Agency as printed',
 recipient_source_agency_id:null,identity_basis:'unresolved_original_publisher_label'};
const cat=A.validate([record,unresolved]);
const network={adj:{'elk-grove-ca-pd':['folsom-ca-pd']}};
const x=A.forAgency(cat,'elk-grove-ca-pd',network);
assert.equal(x.outbound.length,2);
assert.equal(x.outbound[0].alsoSecondary,true);
assert.equal(x.outbound[1].alsoSecondary,null);
const target=A.forAgency(cat,'folsom-ca-pd',network);
assert.equal(target.inbound.length,1,'Only exact matched recipient ID yields inward fact');
assert.equal(target.outbound.length,0,'Forward edge does not establish reverse sharing');
assert.equal(A.forAgency(cat,'random-ca-pd',network).inbound.length,0);
assert.throws(()=>A.validate([record,record]),/Duplicate/);
assert.throws(()=>A.validate([{...record,source_url:'http://unsafe.example'}]),/Missing publisher/);
assert.throws(()=>A.validate([{...unresolved,identity_basis:'exact_source_agency_name'}]),/Unqualified/);
assert.throws(()=>A.validate([{...record,recipient_source_agency_id:null}]),/Unqualified/);
assert.equal(A.validate([{...record,source_status:'no_longer_listed'}]).records[0].source_status,'no_longer_listed');
console.log('ORIGINAL SHARING EVIDENCE PASS: government/vendor tiers, exact-only identity, no reversed direction and historical source statuses');
