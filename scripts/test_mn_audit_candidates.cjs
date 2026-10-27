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
 row('20-0577.pdf','Independent Audit of the Shakopee Police Department Automated License Plate Reader System'),
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
assert.equal(plan.curated_reports,42);
assert.equal(plan.flock_titles_unreviewed,0);
assert.equal(plan.candidates.length,0);
assert.equal(plan.exact_agency_historical_candidates,0);
assert.ok(!plan.candidates.some(x=>x.reason.includes('confirmed')));
assert.ok(['20-0577.pdf','26-0804.pdf','19-1276.pdf','25-1686.pdf'].every(id=>
 !plan.candidates.some(x=>x.report_id===id)),'Newly reviewed source must leave machine queue');
const notYetReviewed={...original,reports:original.reports.filter(x=>!x.id.includes('west-saint-paul-mn-independent-flock')&&!x.id.includes('wyoming-mn-independent-flock'))};
const preReview=H.plan(rows,notYetReviewed);
assert.equal(preReview.flock_titles_unreviewed,2,'Source titles remain candidates until PDFs independently reviewed');
assert.equal(preReview.candidates.length,2);

const agencyReports=require('../data/verified-agency-published-alpr-audits.json').reports;
const internal=row('19-1260.pdf','Biennial Audit of the Hennepin County Sheriff\'s Office Automated License Plate Reader Program');
assert.equal(H.plan([internal],original).candidates.length,1,'Agency internal audit is not in external independent manifest');
const reconciled=H.plan([internal],original,agencyReports);
assert.equal(reconciled.candidates.length,0,'Already page-reviewed agency internal source must leave review backlog');
assert.equal(reconciled.curated_reports,42,'Agency-internal source must not inflate independent-reviewed count');
assert.equal(reconciled.agency_authored_reviewed,1,'Internal source belongs in separate evidence tier');
assert.throws(()=>H.plan([internal],original,[{...agencyReports[0],source_url:'https://evil.example/plate.pdf'}]),/Untrusted/);
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
