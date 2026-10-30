'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const D=require('../government-source-docket.js');
const I=require('../professional-intelligence.js');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/qualified-original-government-docket-2026-10-29.json'),'utf8'));
const index=D.build(raw),historical=I.leadFromDocket(index);
assert.equal(historical.length,index.rows.length);
assert(historical.every(l=>!l.fresh&&l.label==='Historical research lead'&&!l.observed_at));
assert(historical.every(l=>l.originals.every(s=>D.validUrl(s.url))));
assert(historical.every(l=>l.unknown.length&&l.steps.length&&l.why));
assert(I.topics({kind:'published_policy',title:'Data retention policy',summary:'',status:''}).includes('policy'));
assert.throws(()=>I.leadFromDocket({rows:[{source_url:'javascript:alert(1)'}]}),/Unverified/);
const sample={event_key:'document_verified_001',locality_key:'houston|TX',source_agency_id:'houston',
 kind:'contract_document',title:'Executed contract amendment review',summary:'Original government amendment was reviewed; execution status requires original agreement review',
 evidence_tier:'original_government',source_date:'2026-10-20',observed_at:'2026-10-29T11:00:00Z',source_url:'https://houstontx.gov/contract'};
const reviewed=I.leadFromWatch([sample,sample,{...sample,event_key:'draft_from_vendor',evidence_tier:'vendor'},
 {...sample,event_key:'unreviewed_001',source_url:'javascript:bad'}]);
assert.equal(reviewed.length,1);assert.equal(reviewed[0].fresh,false);
assert.equal(I.personalize(reviewed,[{locality_key:'houston|TX',topics:['contract'],research_question:'',
 opted_in_at:'2026-10-29T10:00:00Z'}]).newItems.length,1);
assert.equal(I.personalize(reviewed,[{locality_key:'houston|TX',topics:['contract'],research_question:'',
 opted_in_at:'2026-10-29T12:00:00Z'}]).newItems.length,0);
assert.equal(I.personalize(reviewed,[{locality_key:'houston|TX',topics:['policy'],research_question:'',
 opted_in_at:'2026-10-29T10:00:00Z'}]).newItems.length,0);
assert.equal(I.personalize(reviewed,[{locality_key:'houston|TX',topics:['contract'],research_question:'xyznotinrecord',
 opted_in_at:'2026-10-29T10:00:00Z'}]).newItems.length,0);
const pairs=I.compare(index);
assert(pairs.some(x=>x.type==='missing_evidence'));
assert(pairs.every(x=>!x.interpretation.includes('confirmed wrongdoing')));
const sha='a'.repeat(64);
const pinned={id:'source-review',title:'Authenticated original change',agency:'moline|IL',
 category:'contract_document',interpretation:'Document-only change',delta:{same:false,removed:'Earlier wording',added:'Later signed wording'},
 evidence:[{label:'Original PDF page 2',url:'https://city.gov/document.pdf#page=2',sha}]};
const confirmed=I.compare(index,[pinned]);
assert(confirmed.some(x=>x.type==='confirmed_documentary_difference'));
assert(!I.compare(index,[{...pinned,evidence:[{...pinned.evidence[0],sha:'fake'}]}])
 .some(x=>x.type==='confirmed_documentary_difference'));
assert(!I.compare(index,[{...pinned,category:'policy_proposal'}])
 .some(x=>x.type==='confirmed_documentary_difference'));
assert(I.crossAgency(index,'contract').length>2);
assert.throws(()=>I.crossAgency(index,'theft'),/Unknown/);
const l=historical.find(x=>x.locality_key==='houston|TX');
const draft=I.acquisition(l,index.rows);
assert(draft.body.includes(l.original_url));assert(draft.submitted===false);
assert(draft.body.includes('does not seek individual license-plate observations'));
assert(draft.existing.length>=1);
const report=I.packageHtml(l,pairs,draft);
assert(report.includes(l.original_url));assert(report.includes('Unsent editable records request'));
assert(report.includes('Official roles to contact'));assert(report.includes('Evidence boundary'));
assert(!report.includes('<script'));assert(!report.includes('actual_spending_verified'));
const injection=I.packageHtml({...l,title:'<img src=x onerror=alert(1)>',summary:'<script>bad</script>'},pairs,draft);
assert(!injection.includes('<img'));assert(!injection.includes('<script>bad</script>'));
assert(injection.includes('&lt;script&gt;bad&lt;/script&gt;'));
assert.throws(()=>I.packageHtml({...l,original_url:'http://unsafe'},[],draft),/Verified/);
const migration=fs.readFileSync(path.join(__dirname,'../supabase/migrations/163_research_intelligence_follows.sql'),'utf8');
for(const term of ['enable row level security','auth.uid()','grant update(topics,research_question)',
 'opted_in_at timestamptz not null default now()','intelligence_follows_delete_own'])
 assert(migration.includes(term));
assert(!/grant update\s+on table public\.research_intelligence_follows/.test(migration));
const page=fs.readFileSync(path.join(__dirname,'../professional-intelligence.html'),'utf8');
for(const id of ['leadCards','comparisonList','crossAgency','copyRequest','followList','downloadPackage','draftBody'])
 assert(page.includes('id="'+id+'"'));
const client=fs.readFileSync(path.join(__dirname,'../professional-intelligence-app.js'),'utf8');
assert(client.includes('flock_agency_watch_events'));assert(client.includes('research_intelligence_follows'));
assert(client.includes("No email preferences changed."));assert(!client.includes('sendEmail('));
console.log('PROFESSIONAL_INTELLIGENCE_PASS: five engines, source validation, event baselines, comparison classifications, acquisition, escaped packages and follow security');
