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
const secondary=[{
  source_agency_id:'folsom-ca-pd',agency_name:'Folsom CA PD',
  source_tier:'secondary_aggregated_portal_snapshot',is_reporting_portal:true
},{
  source_agency_id:'unrelated-ca-pd',agency_name:'Folsom CA PD',
  source_tier:'secondary_aggregated_portal_snapshot',is_reporting_portal:true
}];
const original=[{
  agency_label:'Folsom CA PD',agency_key:'folsom_ca_pd',
  disclosure_status:'verified_source_snapshot',
  portal_url:'https://transparency.flocksafety.com/folsom-ca-pd'
}];
const match=[{
  first_party_agency_key:'folsom_ca_pd',
  first_party_portal_url:'https://transparency.flocksafety.com/folsom-ca-pd',
  source_agency_id:'folsom-ca-pd',
  match_basis:'original_flock_portal_slug_exact'
},{
  first_party_agency_key:'folsom_ca_pd',
  first_party_portal_url:'https://transparency.flocksafety.com/another-city',
  source_agency_id:'unrelated-ca-pd',
  match_basis:'original_flock_portal_slug_exact'
}];
const tie=A.build([],original,[],[],secondary,[],[],match).find(g=>g.key==='folsom|CA');
assert.equal(tie.identityMatches.length,1,'Reject mismatched portal URLs');
assert.equal(tie.identityMatches[0].source_agency_id,'folsom-ca-pd');
assert.equal(tie.secondary.length,2,
 'Locality names may overlap but only the exact portal URL qualifies as an identity tie');
assert.equal(A.build([],original,[],[],secondary,[],[],[])[0].identityMatches.length,0,
 'No inference of portal operator from city name alone');
const agencyOnly=[{
 source_key:'elk_grove_original_government',
 source_agency_id:'elk-grove-ca-pd',
 recipient_label:'Roseville CA PD',
 recipient_source_agency_id:'roseville-ca-pd',
 identity_basis:'exact_source_agency_name',
 source_kind:'original_government',
 source_url:'https://elkgrove.gov/traffic/automated-license-plate-readers-alpr'
}];
const regionOnly=A.build([],[],[],[],[
 {source_agency_id:'elk-grove-ca-pd',agency_name:'Elk Grove CA PD',
  is_reporting_portal:false,source_tier:'secondary_aggregated_portal_snapshot'},
 {source_agency_id:'roseville-ca-pd',agency_name:'Roseville CA PD',
  is_reporting_portal:false,source_tier:'secondary_aggregated_portal_snapshot'}
],[],[],[],agencyOnly);
assert.equal(regionOnly.find(g=>g.key==='elk grove|CA')?.originalOutgoing.length,1);
assert.equal(regionOnly.find(g=>g.key==='roseville|CA')?.originalIncoming.length,1,
 'Exact original named recipient must get an evidence-limited dossier even without its own portal');
assert.equal(regionOnly.find(g=>g.key==='roseville|CA')?.originalOutgoing.length,0,
 'No reverse relationship can be inferred by creating incoming recipient profile');
const reviewedPolicy=[{
 event_key:'policy_verified_government_sha_receipt_long_123',
 locality_key:'green bay|WI',kind:'policy_draft_reviewed',
 title:'Original draft policy, not adopted',evidence_tier:'original_government',
 source_url:'https://greenbaywi.gov/DocumentCenter/View/19136',
 source_date:null,observed_at:'2026-10-28T01:00:00Z'
}];
const policyGroups=A.build([],[],[],[],[],[],reviewedPolicy);
const only=policyGroups.find(g=>g.key==='green bay|WI');
assert.ok(only,'Original source-only policy publication can create a watched locality');
assert.equal(only.cameras.length,0);
assert.equal(only.watchEvents.length,1);
const policyItem=A.updateItems(only)[0];
assert.equal(policyItem.type,'Unadopted policy draft');
assert.match(policyItem.confidence,/no evidence of an enacted change/);
assert.equal(A.build([],[],[],[],[],[],[{...reviewedPolicy[0],
 evidence_tier:'secondary_aggregated_portal_snapshot'}]).length,0,
 'Unattributed secondary source cannot become a verified original policy locality');
assert.equal(A.safeUrl('http://example.org'),null);
assert.equal(A.safeUrl('https://example.org/path'),'https://example.org/path');
assert.equal(A.safeUrl('https://user:pass@example.org'),null);
assert.throws(()=>A.build(null,[],[],[]),/Incomplete/);
console.log('AGENCY INTELLIGENCE PASS: no false merged localities, evidence tiers separate, bounded dated change items');
