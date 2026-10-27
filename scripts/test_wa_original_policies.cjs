'use strict';
const assert=require('node:assert/strict');
const Policy=require('../wa-original-policies.js');
const raw=require('../data/verified-wa-agency-policies.json');
const docs=Policy.catalog(raw);
assert.equal(docs.length,2);
assert.deepEqual(docs.map(r=>r.agency_name),['Auburn Police Department','Black Diamond Police Department']);
const auburn=docs[0],black=docs[1];
assert.equal(auburn.page_count,8);
assert.deepEqual(auburn.pages_reviewed,[2,5,6,7]);
assert.equal(black.page_count,7);
assert.equal(black.verification_method,'original_pdf_sha256_visually_reviewed_raster_pages');
assert.ok(docs.every(r=>r.findings.every(f=>r.pages_reviewed.includes(f.page))));
assert.ok(docs.every(r=>Policy.safeSource(r)===r.source_url));
assert.ok(docs.every(r=>!('flock_vendor' in r)&&!('camera_count' in r)&&!('operational_status' in r)));
assert.match(auburn.findings[0].statement,/21 days/);
assert.match(black.findings[1].statement,/21 days/);
for(const row of docs){
 assert.equal(Policy.valid({...row,source_url:'https://example.evil/policy.pdf'}),false);
 assert.equal(Policy.valid({...row,flock_vendor:'Flock Safety'}),false);
 assert.equal(Policy.valid({...row,camera_count:20}),false);
 assert.equal(Policy.valid({...row,operational_status:'currently live'}),false);
 assert.equal(Policy.valid({...row,content_sha256:'0'.repeat(64)}),false);
 assert.equal(Policy.valid({...row,findings:[{page:30,statement:'Z'.repeat(99)}]}),false);
}
assert.equal(Policy.valid({...black,verification_method:'text_layer_ocr_confirmed'}),false);
assert.equal(Policy.valid({...black,verification_note:'not inspected'}),false);
assert.throws(()=>Policy.catalog({...raw,documents:[auburn,auburn]}),/Unverified/);
console.log('WA PAGE-REVIEWED ORIGINAL POLICIES PASS: two source-pinned government originals, scanned-vs-text, no Flock vendor or compliance inference');
