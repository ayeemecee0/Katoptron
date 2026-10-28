const assert=require('node:assert/strict');
const data=require('../data/wa-ago-remaining-original-acquisition-2026-10-27.json');
assert.equal(data.receipts.length,86);
assert.equal(data.new_pdf_original_acquisitions,60);
assert.equal(data.acquisition_holds,26);
assert.equal(data.previously_individually_page_reviewed,11);
assert.equal(data.new_verified_Flock_operator_agencies,0);
const loaded=data.receipts.filter(x=>x.acquisition_status==='retrieved_unreviewed_original_pdf');
assert.equal(loaded.length,60);
for(const x of loaded){assert.match(x.sha256,/^[a-f0-9]{64}$/);assert.ok(x.pdf_pages>=1);}
assert.ok(data.receipts.every(x=>x.original_individual_pages_reviewed===false));
console.log('WA original source receipt validation: 60 acquired, 26 held; no policy claims');