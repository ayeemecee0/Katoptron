'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const I=require('../professional-intelligence.js'),D=require('../government-source-docket.js');
const read=name=>JSON.parse(fs.readFileSync(path.join(__dirname,'../data',name),'utf8'));
const docket=D.build(read('qualified-original-government-docket-2026-10-29.json'));
const national=I.leadFromNational([
 read('nationwide-original-source-research-leads-2026-10-29.json'),
 read('nationwide-original-research-leads-expanded-2026-10-29.json')
]);
assert.equal(national.length,15);
assert.equal(new Set(national.map(x=>x.id)).size,15);
assert(national.every(x=>x.observed_at===null&&!x.fresh&&x.original_url.startsWith('https://')));
assert(national.every(x=>x.label==='Source-attributed national research starter'&&x.unknown.length>=2));
assert(national.some(x=>x.locality_key.endsWith('|AZ')));
assert(!national.some(x=>x.label.includes('confirmed documentary difference')));
const all=[...I.leadFromDocket(docket),...national];
const ranked=I.rankForResearch(all,'contract','executed agreement');
assert(ranked.length>8);
assert(ranked.every(x=>Number.isFinite(x.score)&&x.why_ranked.includes('research question')));
assert(ranked.some(x=>x.matched_terms>0));
assert.equal(I.rankForResearch(all,'contract','', 'missing place|CA').length,0);
assert.throws(()=>I.rankForResearch(all,'unapproved topic'),/Invalid/);
assert.throws(()=>I.rankForResearch(all,'contract','x'.repeat(161)),/Invalid/);
const jobs=I.acquisitionBacklog(all,docket.rows,20);
assert.equal(jobs.length,20);
assert.equal(new Set(jobs.map(x=>x.task_id)).size,20);
assert(jobs.every(x=>x.source_url.startsWith('https://')&&x.status==='missing_evidence_not_claim_of_wrongdoing'));
assert(jobs.every(x=>x.draft.submitted===false&&x.draft.body.includes(x.source_url)));
assert(jobs.every(x=>x.draft.body.includes('IF HELD')&&x.draft.body.includes('No statutory deadline is assumed')));
assert(jobs.every(x=>!x.draft.body.includes('request individual license-plate observations')));
assert.throws(()=>I.acquisitionBacklog(all,docket.rows,500),/Bounded/);
const policy=all.find(x=>x.topics.includes('policy'));
assert(I.acquisition(policy,docket.rows).requested_record_types.some(x=>/policy versions|policy/.test(x)));
const contract=all.find(x=>x.topics.includes('contract'));
assert(I.acquisition(contract,docket.rows).requested_record_types.some(x=>/Signed agreements|Solicitations/.test(x)));
const watched=[{
 id:'reviewed:new-20261029',locality_key:'houston|TX',agency:'Houston',topics:['contract'],title:'Original reviewed agreement',
 summary:'Dated reviewed government contract',status:'contract_document',source_date:'2026-10-29',
 observed_at:'2026-10-29T20:00:00Z',original_url:'https://www.houstontx.gov/contracts/example',
 unknown:['Signed amendment status unresolved'],label:'Reviewed public Watch record'
}];
const p=[{locality_key:'houston|TX',topics:['contract'],research_question:'',opted_in_at:'2026-10-29T19:00:00Z'}];
const out=I.digest([...watched,...national],p,'2026-10-30T02:00:00Z');
assert.equal(out.newReviewed.length,1);assert.equal(out.historical.length,0);
assert.equal(out.automatic_email_enabled,false);
assert.equal(I.digest([...watched,...national],p,'2026-11-12T02:00:00Z').newReviewed.length,0);
assert.equal(I.digest([...watched,...national],[{...p,opted_in_at:'2026-10-30T02:00:00Z'}],'2026-10-30T04:00:00Z').newReviewed.length,0);
assert.throws(()=>I.leadFromNational([{schema_version:1,leads:[{
 ...read('nationwide-original-research-leads-expanded-2026-10-29.json').leads[0],
 policy_enactment_inferred:true}]},read('nationwide-original-source-research-leads-2026-10-29.json')]),/qualified/);
const html=fs.readFileSync(path.join(__dirname,'../professional-intelligence.html'),'utf8');
for(const id of ['leadQuestion','gapBacklog','gapBacklogStatus','copyWeeklyDigest','weeklyDigestStatus'])
 assert(html.includes('id="'+id+'"'));
const app=fs.readFileSync(path.join(__dirname,'../professional-intelligence-app.js'),'utf8');
for(const marker of ['I.leadFromNational','I.rankForResearch','I.acquisitionBacklog','I.digest','renderGapBacklog'])
 assert(app.includes(marker));
assert(app.includes('No email preferences changed.'));
console.log('INTELLIGENCE_EXPANSION_PASS: 15 publisher-attributed national starters, 20 source-cited gap tasks, relevance ranking and opt-in 7-day digest; no new Watch events or fabricated proof');
