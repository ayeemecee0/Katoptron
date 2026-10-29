'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const T=require('../research-templates.js');
const roles=['journalist','nonprofit','legal_researcher'];
for(const role of roles){
 const d=T.draft(role,'Sacramento County Sheriff','https://www.saccounty.gov/records');
 assert.equal(d.role,role);
 assert.equal(d.questions.length,5);
 assert.match(d.body,/publicly releasable/);
 assert.match(d.body,/do not request private license-plate observations/);
 assert.match(d.body,/https:\/\/www.saccounty.gov\/records/);
 assert.ok(d.title.length>=20);
}
assert.throws(()=>T.draft('unverified_role','Agency','https://gov.example.gov'));
const page=fs.readFileSync(path.join(__dirname,'../research-workspace.html'),'utf8');
for(const id of ['templateRole','templatePreview','deleteCase','deleteWorkspace'])
 assert.ok(page.includes('id="'+id+'"'));
const workspace=fs.readFileSync(path.join(__dirname,'../research-workspace.js'),'utf8');
for(const x of ['deletePrivateCase','research_change_collaborator_role',
 'research_request_activity','chosenTemplate','research_case_requests'])
 assert.ok(workspace.includes(x));
const pricing=fs.readFileSync(path.join(__dirname,'../research-plans.html'),'utf8');
for(const x of ['not purchasable','No billing','Professional research pilot','under_50'])
 assert.ok(pricing.includes(x));
const pilot=fs.readFileSync(path.join(__dirname,'../research-pilot.js'),'utf8');
assert.match(pilot,/research_pilot_interest/);
assert.match(pilot,/\.delete\(\)/);
const sql=fs.readFileSync(path.join(__dirname,'../supabase/migrations/159_prevent_research_orphan_storage.sql'),'utf8');
assert.match(sql,/storage\.objects/);
assert.match(sql,/before delete on public\.research_cases/);
console.log('RESEARCH_PRO_WORKFLOWS_PASS: 3 role templates, deletion guard, opt-in-only pilot, no billing');
