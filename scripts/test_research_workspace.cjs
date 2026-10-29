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
const html=fs.readFileSync(path.join(__dirname,'../research-workspace.html'),'utf8');
for(const key of ['research-workspace.js','createRequest','uploadFile','inviteRole','exportCase','caseStatus','requestBody'])
 assert.ok(html.includes(key));
const schema=fs.readFileSync(path.join(__dirname,'../supabase/migrations/151_research_workspace_rls_policies.sql'),'utf8');
assert.match(schema,/research_case_read/);assert.match(schema,/research_request_update/);
assert.match(schema,/auth\.uid\(\)/);
const storage=fs.readFileSync(path.join(__dirname,'../supabase/migrations/152_research_workspace_invites_and_storage.sql'),'utf8');
assert.match(storage,/public=false/);
assert.match(storage,/security definer set search_path = ''/);
assert.match(storage,/expires_at>now\(\)/);
assert.match(storage,/research_storage_read/);
console.log('RESEARCH_WORKSPACE_PASS: secure source URL, evidence export, case requests, invite and storage policies');
