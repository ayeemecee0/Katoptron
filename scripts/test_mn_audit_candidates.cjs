'use strict';
const assert=require('node:assert/strict');
const H=require('../mn-audit-candidates.js');
const original=require('../data/verified-independent-audits.json');
function row(id,title,scope='unspecified_alpr_title',date='2024-06-01'){
 const key=id.slice(0,2)+id.slice(3,7);
 return {source_url:'https://www.lrl.mn.gov/docs/20'+id.slice(0,2)+'/mandated/'+key+'.pdf',
  report_id:id,report_title:title,listed_publishers:'Original state archive',
  publication_date:date,coverage_period:'originally indexed period',
  title_scope:scope,evidence_tier:'state_legislative_registry_index_metadata_only'};
}
const rows=[
 row('22-0708.pdf','Independent Audit of the Shakopee Police Department Automated License Plate Reader System'),
 row('26-0804.pdf','Richfield Police Department 2021 ALPR Audit Executive Summary'),
 row('19-1276.pdf','Biennial Audit of Woodbury Public Safety Department Automated License Plate Reader System'),
 row('25-1686.pdf','Champlin Police Department 2025 ALPR Audit (AXON) Executive Summary','other_vendor_named_in_title'),
 row('26-1167.pdf','West Saint Paul Police Department 2026 ALPR Audit (Flock System)','flock_named_in_title'),
 row('26-1268.pdf','Wyoming Police Department 2026 ALPR Audit (Flock System)','flock_named_in_title'),
 row('18-0202.pdf','Washington County, Stillwater, Minnesota Agreed-Upon Procedures'),
 row('25-1700.pdf','Independent Audit of West Hennepin Public Safety Department ALPR System'),
 row('25-1639.pdf','UMN Police Department 2025 ALPR Audit (Flock) Executive Summary','flock_named_in_title'),
 row('26-1013.pdf','Independent Audit of Shakopee Police Department 2026 ALPR System','unspecified_alpr_title','2026-06-15'),
];
const plan=H.plan(rows,original);
assert.equal(plan.scanned_reports,10);
assert.equal(plan.curated_reports,17);
assert.equal(plan.flock_titles_unreviewed,2);
assert.equal(plan.candidates.length,6);
assert.equal(plan.exact_agency_historical_candidates,4);
assert.equal(plan.candidates[0].priority,'P0');
assert.equal(plan.candidates[0].matched_agency,null); // no curated West Saint Paul
assert.equal(plan.candidates[0].jurisdiction_key,null);
const sh=plan.candidates.find(x=>x.report_id==='22-0708.pdf');
assert.equal(sh.jurisdiction_key,'shakopee|MN');
assert.equal(sh.identity_basis,'original_title_exact_curated_agency_phrase');
assert.equal(sh.title_scope,'unspecified_alpr_title');
assert.equal(sh.priority,'P1');
assert.ok(plan.candidates.some(x=>x.report_id==='26-0804.pdf'&&x.jurisdiction_key==='richfield|MN'));
assert.ok(plan.candidates.some(x=>x.report_id==='19-1276.pdf'&&x.jurisdiction_key==='woodbury|MN'));
assert.ok(plan.candidates.some(x=>x.report_id==='25-1686.pdf'&&x.priority==='P2'));
assert.ok(!plan.candidates.some(x=>['18-0202.pdf','25-1700.pdf','25-1639.pdf','26-1013.pdf'].includes(x.report_id)));
assert.ok(!plan.candidates.some(x=>x.reason.includes('confirmed')));
const single=[rows[0]];
assert.throws(()=>H.plan([...single,single[0]],original),/Duplicate/);
assert.throws(()=>H.plan([{...rows[0],source_url:'https://evil.example/docs/2022/mandated/220708.pdf'}],original),/Non-official/);
assert.throws(()=>H.plan([{...rows[0],publication_date:'2024-02-30'}],original),/Non-official/);
assert.throws(()=>H.plan([{...rows[0],report_id:'bad'}],original),/Non-official/);
const badManifest={...original,reports:[...original.reports,{...original.reports[0],source_url:'https://evil.example/docs/file.pdf'}]};
assert.throws(()=>H.plan(rows,badManifest),/provenance/);
assert.equal(H.titleHasPhrase('West Hennepin Public Safety','Hennepin County Sheriff\'s Office'),false);
assert.equal(H.originalUrl('https://www.lrl.mn.gov/docs/2026/mandated/261268.pdf?secret=1'),null);
console.log('MINNESOTA HISTORICAL CANDIDATE PASS: verified-source absence, exact agency matching, vendor boundaries, ranked metadata only, URL/date and duplicate safeguards');
