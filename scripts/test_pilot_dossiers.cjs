'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const Docket=require('../government-source-docket.js');
const Pilot=require('../pilot-dossiers.js');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/qualified-original-government-docket-2026-10-29.json'),'utf8'));
const dossiers=Pilot.build(Docket.build(data));
assert.equal(dossiers.length,8);
assert.equal(new Set(dossiers.map(x=>x.id)).size,8);
assert.equal(new Set(dossiers.map(x=>x.key)).size,8);
assert.ok(dossiers.every(d=>d.records.length>0&&d.records.length<=8));
for(const d of dossiers){
 assert(d.questions.length>=2);
 for(const rec of d.records){
  assert.equal(rec.locality_key,d.key);
  assert.equal(rec.watch_category,'historical_research_only');
  assert(Docket.validUrl(rec.source_url));
  const note=Pilot.recordNote(rec);
  assert(note.includes(rec.source_url)&&note.includes(rec.status)&&note.includes(rec.source_date));
  assert(note.length<=5000);
 }
 const html=Pilot.exportHtml(d,data.compiled_on);
 for(const rec of d.records){
  assert(html.includes(rec.source_url.replace(/&/g,'&amp;')));
  assert(html.includes(rec.status));
  assert(html.includes(rec.proof.replace(/&/g,'&amp;')));
 }
 assert(html.includes('not a live camera census'));
 assert(!html.includes('<script'));
}
assert.equal(dossiers.find(d=>d.id==='sacramento').records.length,3);
assert.equal(dossiers.find(d=>d.id==='new-hanover').records[0].flock_specific,false);
assert.match(dossiers.find(d=>d.id==='louisville').records[0].status,/denied/);
assert.match(dossiers.find(d=>d.id==='los-angeles').records[0].status,/pending_not_enacted/);
assert.throws(()=>Pilot.build({byLocality:()=>[]} ),/lacks bounded/);
assert.throws(()=>Pilot.exportHtml(null),/No original-source/);
const malicious={...dossiers[0],title:'<img src=x onerror=alert(1)>',records:[
 {...dossiers[0].records[0],summary:'<script>alert(1)</script>',source_url:'https://cityofwoodland.gov/?a=1&b=2'}]};
const escape=Pilot.exportHtml(malicious,'2026-10-29');
assert(!escape.includes('<img'));assert(!escape.includes('<script'));
assert(escape.includes('&lt;script&gt;'));
assert(escape.includes('a=1&amp;b=2'));
const page=fs.readFileSync(path.join(__dirname,'../pilot-dossiers.html'),'utf8');
assert(page.includes('id="downloadBrief"')&&page.includes('id="importLink"'));
const workspace=fs.readFileSync(path.join(__dirname,'../research-workspace.js'),'utf8');
assert(workspace.includes('research_case_notes'));
assert(workspace.includes('PilotDossiers.recordNote'));
assert(workspace.includes('source_url:record.source_url'));
assert(workspace.includes("sb.from('research_cases').delete()")); 
assert(workspace.includes('Partial private case'));
assert(workspace.includes("confirmationUrl.searchParams.set('dossier',selectedDossier)"));
assert(!workspace.includes("emailRedirectTo:win.location.origin+win.location.pathname"));
console.log('PILOT_DOSSIERS_PASS: eight vetted reporting-beat dossiers, citations, independent preview and escaped printable briefs');
