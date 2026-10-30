'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const P=require('../pilot-relevance.js'),D=require('../government-source-docket.js');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/qualified-original-government-docket-2026-10-29.json'),'utf8'));
const docket=D.build(raw);
assert.equal(docket.rows.length,53);assert.equal(docket.agencies.length,45);
assert.equal(P.PRESETS.length,5);assert.equal(new Set(P.PRESETS.map(x=>x.id)).size,5);
for(const preset of P.PRESETS){
 const list=P.rank(docket,preset.id);
 assert.equal(list.length,45);
 assert(list.every(x=>x.selected.length<=3&&x.selected.length>0));
 assert(list.every(x=>x.records.every(s=>s.watch_category==='historical_research_only')));
 assert(list.every(x=>x.selected.every(v=>v.source.source_url.startsWith('https://'))));
 assert(list.every(x=>!x.why.toLowerCase().includes('wrongdoing confirmed')));
 assert(list.every(x=>x.selected.every(v=>Array.isArray(v.reasons)&&v.score>=0)));
 const results=P.rank(docket,preset.id,'houston|TX');
 assert.equal(results.length,1);assert.equal(results[0].records.length,2);
 const report=P.pack(results[0]);
 for(const r of results[0].records){
  assert(report.includes(r.title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/'/g,'&#39;').replace(/"/g,'&quot;')));assert(report.includes(r.source_url.replace(/&/g,'&amp;')));assert(report.includes(r.status));
 }
 assert(report.includes('Original-source chronology and appendix'));
 assert(report.includes('Historical, source-attributed'));
 assert(report.includes('No request was submitted.'));
 assert(!report.includes('<script'));
}
const l=P.rank(docket,'public_spending','louisville|KY')[0];
assert.equal(l.records.length,2);
assert(l.records.some(x=>x.amount_usd===6650));
assert(l.records.some(x=>x.flock_specific===false));
assert(l.selected.length===2);
assert(P.pack(l).includes('NOT audited payment'));
const one=P.rank(docket,'local_accountability','new hanover county|NC')[0];
assert.equal(one.selected.length,1);
assert.match(one.limitation,/Only 1 original-government record/);
assert(P.pack(one).includes('missing records are not fabricated')===false);
assert.deepEqual(P.rank(docket,'technology','nowhere|CA'),[]);
assert.throws(()=>P.rank(docket,'fake'),/Unknown/);
assert.throws(()=>P.rank(docket,'technology','', 'Q'.repeat(161)),/exceeds/);
assert.throws(()=>P.group({rows:[{source_url:'https://evil.test'}]}),/Unreviewed/);
const share=P.sharePath('civil_liberties','san diego|CA');
assert(share.includes('focus=civil_liberties')&&share.includes('agency=san%20diego%7CCA'));
assert(!share.includes('question=')&&!share.includes('@'));
assert.throws(()=>P.sharePath('fake','san diego|CA'),/Invalid/);
assert.throws(()=>P.sharePath('civil_liberties','none<script>|CA'),/Invalid/);
const base=P.rank(docket,'technology','houston|TX')[0];
const malicious={...base,records:[{...base.records[0],title:'<img src=x onerror=alert(1)>',
 summary:'<script>alert(1)</script>',proof:'" onclick="evil()'}]};
const escaped=P.pack(malicious);
assert(!escaped.includes('<img'));assert(!escaped.includes('<script>alert(1)</script>'));
assert(escaped.includes('&lt;script&gt;alert(1)&lt;/script&gt;'));
assert(escaped.includes('&quot; onclick=&quot;evil()'));
const page=fs.readFileSync(path.join(__dirname,'../pilot-research.html'),'utf8');
for(const id of ['researchFocus','researchAgency','researchQuestion','recommendations','dossier','downloadPacket','shareResearchLink']){
 assert(page.includes('id="'+id+'"'));
}
assert(page.includes('No names, emails, search history or research questions are stored.'));
assert(!page.includes('katoptron00@gmail.com'));
const app=fs.readFileSync(path.join(__dirname,'../professional-intelligence-app.js'),'utf8');
assert(app.includes("searchParams.get('agency')"));
console.log('PILOT_RESEARCH_RELEVANCE_PASS: five beats, 45 validated jurisdictions, two added documents, source-complete exports, no confidential prospect data or invented records');
