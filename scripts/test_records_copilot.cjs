'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const C=require('../records-copilot.js');

const source='https://city.gov/records/signed-agreement';
for(const topic of Object.keys(C.RECORD_TYPES)){
 const d=C.draft({agency:'City of Example, CA',source_url:source,topic,
  start_date:'2025-01-01',end_date:'2026-10-30',fee_cap:25,format:'either'});
 assert.equal(d.submitted,false);
 assert.equal(d.source_verified_by_software,false);
 assert.ok(d.records.length>=3);
 assert.match(d.body,/existing, publicly releasable/);
 assert.match(d.body,/2025-01-01/);
 assert.match(d.body,/2026-10-30/);
 assert.match(d.body,/license-plate observations/);
 assert.match(d.body,/if held/i);
 assert.match(d.body,/fees exceeding \$25.00/);
 assert.ok(!/you must respond within \d+ days/i.test(d.body));
 assert.ok(d.check_before_sending.length>=4);
}
assert.match(C.draft({agency:'City of Example',topic:'sharing'}).body,/Date range not yet specified/);
for(const url of ['javascript:alert(1)','http://example.gov/x','https://city.gov@evil.com/s','https://city.gov/x#local','https://city.gov:444/records']){
 assert.equal(C.safeUrl(url),null,'invalid original URL must be rejected: '+url);
 assert.throws(()=>C.draft({agency:'City of Example',source_url:url}));
}
for(const d of [
 {start_date:'2026-10-31',end_date:'2026-10-30'},
 {start_date:'2026-02-30'},
 {fee_cap:'-1'},
 {fee_cap:'1e10'},
 {fee_cap:'10000.01'}]){
 assert.throws(()=>C.draft({agency:'City of Example',...d}));
}
assert.throws(()=>C.draft({agency:'City of Example',topic:'unrecognized'}));
const original={id:'request-1',subject:'Executed contract',recipient:'Records Office',
 status:'sent',sent_on:'2026-10-29',body:'Please provide records'};
for(const outcome of Object.keys(C.OUTCOMES)){
 const d=C.followUp(original,outcome,'Only a summary, without plate data');
 assert.equal(d.category,outcome);
 assert.equal(d.submitted,false);
 assert.equal(d.original_request_id,'request-1');
 assert.match(d.subject,/Follow-up/);
 assert.match(d.body,/not independently authenticated/);
 assert.match(d.body,/2026-10-29/);
 assert.match(d.body,/No|no/);
 assert.ok(d.check_before_sending.length>=3);
}
const denied=C.followUp(original,'denial');
assert.match(denied.body,/stated legal provision/);
assert.match(denied.body,/If an administrative review or appeal process is available/);
const noRecords=C.followUp(original,'no_records');
assert.match(noRecords.body,/offices, repositories and date range searched/);
const fees=C.followUp(original,'fees');
assert.match(fees.body,/itemized estimate/);
assert.throws(()=>C.followUp({...original,status:'draft'},'denial'));
assert.throws(()=>C.followUp(original,'unknown_response'));
const injection=C.draft({agency:'Some\nAgency\nCC: outsider@example.com'});
assert.doesNotMatch(injection.body,/^CC: outsider/m);
const page=fs.readFileSync(path.join(__dirname,'../research-workspace.html'),'utf8');
const client=fs.readFileSync(path.join(__dirname,'../research-workspace.js'),'utf8');
for(const id of ['recordsCopilot','copilotTopic','copilotCustodian','copilotSourcePick','copilotSource','copilotStart','copilotEnd','copilotFee','copilotFormat',
 'copilotPrep','copilotPrior','copilotOutcome','copilotSummary','copilotFollowupPrep','copilotPreview','copilotSubject',
 'copilotRecipient','copilotBody','copilotChecklist','copilotCopy','copilotSave','copilotStatus']){
 assert.ok(page.includes('id="'+id+'"'),'copilot must show '+id);
 assert.ok(client.includes("$('"+id+"')")||client.includes("$('"+id+"')."),'copilot must wire '+id);
}
assert.match(page,/src="\.\/records-copilot\.js"/);
assert.match(client,/KatoptronRecordsCopilot/);
assert.match(client,/status:'draft'/);
assert.match(client,/stagedCopilotCaseId!==selectedC.id/);
assert.match(client,/params\.get\('agency'\)/);
assert.match(client,/params\.get\('source'\)/);
assert.doesNotMatch(client,/mailto:.*\$\{/);
console.log('RECORDS_COPILOT_PASS: five source-scoped requests, nine human-classified outcomes, safe deep-links and private draft handoff');
