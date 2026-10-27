'use strict';
const assert=require('node:assert/strict');
const A=require('../agency-published-audits.js');
const manifest=require('../data/verified-agency-published-alpr-audits.json');
const rows=A.catalog(manifest);
assert.equal(rows.length,4);
assert.deepEqual(A.count(rows),{reports:4,agencies:3,states:3});
assert.deepEqual([...new Set(rows.map(x=>x.state))].sort(),['CA','MN','WI']);
assert.ok(rows.every(x=>x.publisher_type==='agency_authored_audit'||x.publisher_type==='agency_internal_audit'));
assert.ok(rows.every(x=>x.findings.every(f=>x.pages_reviewed.includes(f.page))));
const suspect=rows.find(x=>x.id==='san-bruno-ca-flock-audit-first-half-2026');
assert.match(suspect.findings[0].statement,/29 Flock searches/);
assert.match(suspect.findings[0].statement,/not a final confirmed legal finding/);
const badDay=rows.find(x=>x.id==='san-bruno-ca-flock-audit-december-2025');
assert.equal(badDay.source_date,null,'Chronologically inconsistent original memo header must not be silently corrected');
assert.match(badDay.source_date_note,/discrepancy is unresolved/);
const bay=rows.find(x=>x.state==='WI');
assert.match(bay.findings.map(x=>x.statement).join(' '),/299 agencies/);
assert.match(bay.findings.map(x=>x.statement).join(' '),/Unknown purge totals cannot be counted as zero/);
for(const attack of [
 'https://www.sanbruno.ca.gov.evil.example/DocumentCenter/View/9280/x',
 'https://evil.example/DocumentCenter/View/9280/x',
 'https://www.greenbaywi.gov/DocumentCenter/View/18762/x#fake',
 'https://www.lrl.mn.gov/docs/2020/mandated/200290.pdf',
 'https://www.sanbruno.ca.gov/DocumentCenter/View/9280/SBPD-Flock-ALPR-Annual-Audit---2025?current=1',
 'javascript:alert(1)'])
 assert.equal(A.safeUrl(attack),null);
assert.equal(A.valid({...bay,source_date:'2026-02-31'}),false);
assert.equal(A.valid({...bay,publisher_type:'independent_external_audit'}),false);
assert.equal(A.valid({...bay,findings:[{...bay.findings[0],page:99}]}),false);
assert.throws(()=>A.catalog({...manifest,reports:[bay,bay]}),/Duplicate/);
console.log('MULTISTATE AGENCY-AUTHORED AUDIT PASS: CA WI MN source tiers, page links, unsafe hosts, duplicate, unsupported date and evidence boundary');
