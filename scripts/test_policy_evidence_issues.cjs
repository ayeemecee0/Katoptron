'use strict';
const assert=require('node:assert/strict');
const E=require('../policy-evidence-issues.js');
const original={
 wa:require('../data/verified-wa-flock-policy-originals.json'),
 apache:require('../data/apache-junction-original-chapter-and-map-receipts-2026-10-27.json'),
 apacheResolution:require('../data/apache-junction-adopted-resolution-chapter-2026-10-28.json'),
 adoptions:require('../data/verified-policy-adoption-status-2026-10-27.json'),
 waPages:require('../data/wa-three-individual-flock-policy-page-source-findings-2026-10-27.json'),
 robbinsdale:require('../data/verified-robbinsdale-2025-independent-flock-audit.json')
};
const x=E.build(original);
assert.equal(x.items.length,5);
assert.equal(x.open_source_questions,4);
assert.equal(x.interpretive_cautions,1);
assert.equal(x.new_camera_coordinates,0);
assert.equal(x.verified_current_equipment,0);
assert.deepEqual(new Set(x.items.map(r=>r.state)),new Set(['WA','AZ','WI','MN']));
assert.equal(x.items.filter(i=>i.class==='textual_inconsistency').length,1);
assert.equal(x.items.filter(i=>i.status==='not_a_verified_conflict').length,1);
assert.match(x.items.find(i=>i.state==='AZ').title,/Signed resolution includes Chapter 17/);
assert.equal(x.items.find(i=>i.state==='AZ').citations.length,5);
assert(x.items.every(i=>i.citations.every(c=>c.url.startsWith('https://')&&c.label)));
assert(!x.items.some(i=>/confirmed violation|currently operating cameras|actual sharing verified/i.test(i.detail)));
function tamper(mutation){
 const copy=structuredClone(original);mutation(copy);
 assert.throws(()=>E.build(copy),/Source-provenance check failed/);
}
tamper(v=>v.wa.documents.find(d=>d.agency_name.startsWith('Sedro')).findings.find(f=>f.page===5).statement='No contradiction');
tamper(v=>v.wa.documents.find(d=>d.agency_name.startsWith('Sedro')).content_sha256='0'.repeat(64));
tamper(v=>v.apache.signed_original_visually_reviewed.legal_effective_date='2026-10-06');
tamper(v=>v.apacheResolution.original_sha256='0'.repeat(64));
tamper(v=>v.apacheResolution.legal_effective_date_verified=true);
tamper(v=>v.apacheResolution.notices_date_agrees_with_signed_resolution=true);
tamper(v=>v.apacheResolution.original_council_agenda_appendix_exact_match_verified=true);
tamper(v=>v.apache.source_page_reviewed[0].publication_status='authenticated_final');
tamper(v=>v.adoptions.records.find(d=>d.state==='WI').status='adopted');
tamper(v=>v.waPages.documents[2].publisher_actor='Sultan Police Department');
tamper(v=>v.robbinsdale.comparison_note='Confirmed 2026 retention violation');
console.log('PASS: four original-source questions and one non-conflict caution; forged adoption, dates, identity, and hashes held');
