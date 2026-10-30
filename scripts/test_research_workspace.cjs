'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const U=require('../research-workspace.js');
assert.equal(U.sourceUrl('https://city.gov/records/2026'),'https://city.gov/records/2026');
for(const url of ['javascript:alert(1)','http://city.gov','https://city.gov@evil.com','https://example.gov/a#secret','file:///etc/passwd'])
 assert.equal(U.sourceUrl(url),null,'Reject unsafe source URL: '+url);
assert.equal(U.agencyKey('sacramento county|CA'),'sacramento county|CA');
assert.equal(U.agencyKey('sacramento county|california'),null);
const record=U.exportData({id:'w',title:'Test'},{id:'c',agency_key:'folsom|CA',title:'Investigation',status:'open'},
 [{subject:'Records',recipient:'Agency',body:'Please provide contract records',status:'draft',sent_on:null,response_due_on:null,response_received_on:null}],
 [{note:'Publisher statement only',source_url:'https://city.gov/c',created_at:'2026-10-29T00:00:00Z'}],
 [{filename:'response.pdf',file_size:123,created_at:'2026-10-29'}]);
assert.equal(record.attachments_metadata_only.length,1);
assert.ok(!JSON.stringify(record).includes('service_role'));
assert.ok(record.warning.includes('NOT included'));
const cited=U.htmlBrief({id:'w',title:'Test'},{id:'c',agency_key:'folsom|CA',title:'Research <unsafe>',status:'open'},[],[
 {note:'Fact <img src=x onerror=alert(1)>',source_url:'https://city.gov/records?a=1&b=2',created_at:'2026-10-29'},
 {note:'No verified citation',source_url:'javascript:alert(1)',created_at:'2026-10-29'}
],[]);
assert.match(cited,/Research &lt;unsafe&gt;/);
assert.match(cited,/Fact &lt;img/);
assert.doesNotMatch(cited,/<img/);
assert.doesNotMatch(cited,/href="javascript/);
assert.match(cited,/city.gov\/records\?a=1&amp;b=2/);
assert.match(cited,/NOT independently verified/);
assert.doesNotMatch(cited,/<script/);
const html=fs.readFileSync(path.join(__dirname,'../research-workspace.html'),'utf8');
for(const key of ['research-workspace.js','createRequest','uploadFile','inviteRole','teamSecurity','pendingInvites','teamActivity','exportCase','exportBrief','pilotStart','pilotAgency','caseStatus','requestBody'])
 assert.ok(html.includes(key));
assert.match(U.htmlBrief({id:'w',title:'W'},{id:'c',agency_key:'county|CA',title:'Case',status:'open'},[],[],[]),/Private case export/);
const secure=fs.readFileSync(path.join(__dirname,'../supabase/migrations/162_research_team_audit_ledger.sql'),'utf8');
assert.match(secure,/enable row level security/);
assert.match(secure,/research_team_activity_owner_read/);
assert.match(secure,/revoke all on function katoptron_private/);
assert.doesNotMatch(secure,/invite_token.*values/);
const schema=fs.readFileSync(path.join(__dirname,'../supabase/migrations/151_research_workspace_rls_policies.sql'),'utf8');
assert.match(schema,/research_case_read/);assert.match(schema,/research_request_update/);
assert.match(schema,/auth\.uid\(\)/);
const storage=fs.readFileSync(path.join(__dirname,'../supabase/migrations/152_research_workspace_invites_and_storage.sql'),'utf8');
assert.match(storage,/public=false/);
assert.match(storage,/security definer set search_path = ''/);
assert.match(storage,/expires_at>now\(\)/);
assert.match(storage,/research_storage_read/);
const member=fs.readFileSync(path.join(__dirname,'../supabase/migrations/153_research_collaborator_owner_controls.sql'),'utf8');
assert.match(member,/research_list_collaborators/);assert.match(member,/research_remove_collaborator/);
const identity=fs.readFileSync(path.join(__dirname,'../supabase/migrations/154_research_immutable_case_and_request_identity.sql'),'utf8');
assert.match(identity,/Original case author and workspace identity are immutable/);
assert.match(identity,/Records request author and parent case are immutable/);
console.log('RESEARCH_WORKSPACE_PASS: secure source URL, evidence export, case requests, invite and storage policies');
