const assert=require('node:assert/strict');
const T=require('../agency-timeline.js');
const common='https://city.gov/flock';
const group={
 label:'Test, CA',
 events:[
 {event_key:'dated-program',event_type:'government_program',event_date:'2026-10-12',
  date_basis:'government_source_date',title:'Program website exists',summary:'Information posted; adoption date unknown',source_url:common},
 {event_key:'undated-vote',event_type:'editorially_reviewed_action',
  event_date:null,date_basis:'not_documented',title:'Government transparency resource',summary:'Undated',source_url:common+'/undated'},
 {event_key:'action1',event_type:'recorded_legislative_decision',event_date:'2026-07-02',
  date_basis:'recorded_minutes',title:'Council recorded action',source_url:common+'/minutes'}],
 programs:[{program_key:'test',program_status:'documented_at_source_date',source_date:'2026-10-11',official_evidence_url:common}],
 portals:[{agency_key:'testpd',agency_label:'Test CA PD',source_date:'2026-09-01',portal_url:'https://transparency.flocksafety.com/test-ca-pd',
   retention_days:30,reported_total_cameras:44}],
 originalOutgoing:[
  {source_key:'test_2026',source_observed_on:'2026-10-25',recipient_label:'Folsom CA PD',publisher_name:'Test CA PD',
   captured_scope:'published_list_excerpt',source_url:common+'/sharing'},
  {source_key:'test_2026',source_observed_on:'2026-10-25',recipient_label:'Elsewhere CA PD',publisher_name:'Test CA PD',
   captured_scope:'published_list_excerpt',source_url:common+'/sharing'}],
 secondaryRetention:[
 {source_agency_id:'test-ca-pd',observed_on:'2026-06-01',retention_days:30,source_url:'https://eyesonflock.com/portal/test-ca-pd'},
 {source_agency_id:'test-ca-pd',observed_on:'2026-09-01',retention_days:7,source_url:'https://eyesonflock.com/portal/test-ca-pd'}]
};
const contract=[{contract_key:'executed',contract_number:'2026-100',signed_on:'2026-05-01',
 ends_on:'2027-05-01',amount_usd:25000,source_url:common+'/signed'}];
const result=T.build(group,contract);
assert.equal(result.undated.length,1);
assert.ok(result.undated[0].date===null);
assert.equal(result.dated.filter(e=>e.kind==='sharing_observation').length,1,
 'Do not invent separate publication dates for each named recipient');
assert.equal(result.dated.filter(e=>e.kind==='retention_difference').length,1);
assert.equal(result.dated.filter(e=>e.kind==='scheduled_contract_end')[0].scheduled,true);
assert.ok(result.dated.find(e=>e.kind==='scheduled_contract_end').detail.includes('does NOT establish renewal'));
assert.ok(result.dated.find(e=>e.kind==='program_disclosure').detail.includes('not necessarily the start'));
assert.equal(T.filter(result.dated,'recorded_decision').length,1);
assert.equal(T.date('2026-02-30'),null);
assert.equal(T.safe('http://example.gov/source'),null);
const noChange=T.build({...group,secondaryRetention:[group.secondaryRetention[0]]});
assert.equal(noChange.dated.filter(e=>e.kind==='retention_difference').length,0,
 'One source reading cannot establish any actual policy difference');
const undated=T.build({...group,events:[{event_key:'missing-date',title:'Unknown adoption',source_url:common}]});
assert.equal(undated.undated.length,1);
assert.ok(!undated.dated.some(e=>e.title==='Unknown adoption'));
console.log('AGENCY TIMELINE PASS: dated vs undated, original publisher grouping, source comparability, scheduled-only contracts and no invented adoption or policy changes');
