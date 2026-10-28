'use strict';
const assert=require('node:assert/strict');
const A=require('../apache-junction-original-chapter.js');
const original=require('../data/apache-junction-original-chapter-and-map-receipts-2026-10-27.json');
const x=A.verify(original);
assert.equal(x.original_agenda_documents.length,2);
assert.equal(x.held_city_clerk_original.page_count,3);
assert.equal(x.city_clerk_adopted_copy_visually_reviewed,false);
assert.equal(x.individually_verified_exact_camera_coordinates,0);
assert.equal(x.agency_self_disclosure.claimed_cameras,30);
assert.equal(x.agency_self_disclosure.claimed_retention_days,30);
assert.equal(x.agency_self_disclosure.map_marked_date,'2026-08-24');
assert.match(x.scope_note,/do not prove final executed/);
assert.ok(x.original_agenda_documents[0].findings.some(f=>f.page===3&&/30 consecutive calendar days/.test(f.statement)));
assert.equal(x.original_agenda_documents[1].publication_status,
 'unsigned_agenda_ordinance_version_not_proof_of_executed_instrument');
assert.ok(x.original_agenda_documents.every(d=>d.findings.every(f=>f.original_page.endsWith('#page='+f.page))));
assert.equal(A.pdfPage('https://example.gov/file',1),'https://example.gov/file#page=1');
assert.equal(A.pdfPage('http://example.gov/file',1),null);
assert.equal(A.pdfPage('https://example.gov/file#wrong',1),null);
function corrupt(fn,match){
 const a=structuredClone(original);fn(a);assert.throws(()=>A.verify(a),match);
}
corrupt(a=>a.source_review_held[0].status='signed_and_verified',/held/);
corrupt(a=>a.source_review_held[0].original_sha256='0'.repeat(64),/held/);
corrupt(a=>a.source_page_reviewed[0].pdf_sha256='0'.repeat(64),/identity/);
corrupt(a=>a.source_page_reviewed[1].publication_status='executed_ordinance',/identity/);
corrupt(a=>a.source_page_reviewed[1].document_date='2026-10-06',/identity/);
corrupt(a=>a.source_page_reviewed[0].findings[1].page=5,/source PDF page/i);
corrupt(a=>a.agency_self_disclosure.exact_gis_coordinate_count=30,/diagram improperly/);
corrupt(a=>a.agency_self_disclosure.claimed_cameras=31,/diagram improperly/);
corrupt(a=>a.agency_self_disclosure.official_map_url='https://evil.net/map',/diagram improperly/);
corrupt(a=>a.source_page_reviewed[0].findings[2].statement='This approved Flock sharing now happens',/Source PDF page/);
console.log('APACHE GOVERNMENT SOURCE REVIEW PASS: original chapter/unsigned ordinance text distinct from uninspected City Clerk scanned source; schematic not coordinate pins');
