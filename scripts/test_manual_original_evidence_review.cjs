'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,'data',name),'utf8'));
const ledger=read('manual-original-evidence-review-2026-10-29.json');
const additions=read('nationwide-reviewed-original-monitor-additions-2026-10-29.json');
assert.equal(ledger.schema_version,1);
assert.equal(ledger.discovery_candidates.length,6);
assert.equal(ledger.discovery_candidates.filter(x=>x.status==='original_pdf_page_visually_verified').length,4);
assert.equal(ledger.discovery_candidates.filter(x=>x.status==='held_pdf_redirect_original_parent_verified').length,2);
assert.equal(ledger.held_sources.length,16);
assert.equal(ledger.changed_source_candidates.length,25);
assert.equal(additions.sources.length,22);
const accepted=ledger.discovery_candidates.filter(x=>x.status==='original_pdf_page_visually_verified');
for(const x of accepted){
 assert(x.url.startsWith('https://')&&Number.isInteger(x.page)&&x.page>=1);
 assert(x.caveat.length>40&&x.claim.length>60&&x.source_date_note);
 const a=additions.sources.find(r=>r.record_origin==='manually_verified_original_document'&&r.record_id===x.id);
 assert(a&&a.source_url===x.url&&a.publisher===x.original_publisher);
 assert.equal(a.policy_change_verified_by_monitor,false);
}
assert(new Set(ledger.held_sources.map(x=>x.source_id)).size===16);
assert(ledger.held_sources.every(x=>x.source_identity_not_deleted&&x.monitor_recovered===false));
assert(ledger.held_sources.some(x=>x.source_id.startsWith('wv-')&&x.disposition.includes('not a Flock')));
assert(new Set(ledger.changed_source_candidates.map(x=>x.source_id)).size===25);
assert(ledger.changed_source_candidates.every(x=>!x.documentary_version_difference_approved));
assert.equal(ledger.review_summary.independently_confirmed_same_document_before_after_wording_differences,0);
for(const c of ledger.comparative_research_findings){
 assert(c.before_url.endsWith('#page=1')&&c.after_url.endsWith('#page=1'));
 assert(c.category.includes('not_verified_version_delta'));
}
const page=fs.readFileSync(path.join(root,'original-evidence-review.html'),'utf8');
const script=fs.readFileSync(path.join(root,'source-evidence-review.js'),'utf8');
for(const id of ['sourceCards','heldTable','changeList','comparisons','reviewStatus'])assert(page.includes('id="'+id+'"'));
assert(script.includes('textContent'));assert(script.includes('not a before/after')||page.includes('before-and-after'));
console.log('ORIGINAL_EVIDENCE_REVIEW_PASS: 4 page-reviewed government originals, 2 held PDFs, 16 held URLs dispositioned, 25 hash changes held without fabricated conclusions');
