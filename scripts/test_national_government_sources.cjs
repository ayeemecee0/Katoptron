'use strict';
const assert=require('node:assert/strict');
const G=require('../national-government-sources.js');
const reviewed=require('../data/verified-national-government-oversight.json');
const registry=require('../data/national-government-audit-source-portals.json');
const rows=G.oversightCatalog(reviewed),publishers=G.portals(registry);
assert.equal(rows.length,3);
assert.equal(publishers.length,14);
assert.deepEqual([...new Set(publishers.map(x=>x.state))].sort(),['CA','DE','IL','OR','TX','VA','WA','WI']);
assert.deepEqual(G.counts(rows),{documents:3,agencies:3,states:3});
assert.equal(rows.filter(x=>x.publisher_type==='independent_government_oversight').length,2);
assert.equal(rows.filter(x=>x.publisher_type==='agency_authored_impact_assessment').length,1);
const austin=rows.find(x=>x.state==='TX');
assert.equal(austin.source_date,null,'A month-only report never gains an invented publication day');
assert.match(austin.source_date_note,/Month and year/);
const grand=rows.find(x=>x.id==='san-mateo-ca-2026-grand-jury');
assert.match(grand.findings.map(x=>x.statement).join(' '),/NOT 582 individually verified Flock/i);
const impact=rows.find(x=>x.state==='OR');
assert.match(impact.findings[0].statement,/November 11, 2025/);
assert.equal(G.overview({...impact,publisher_type:'independent_government_oversight'}),false);
assert.equal(G.overview({...grand,source_url:'https://sanmateo.courts.ca.gov.evil.example/report.pdf'}),false);
assert.equal(G.overview({...grand,content_sha256:'0'.repeat(63)}),false);
assert.equal(G.overview({...grand,findings:[{...grand.findings[0],page:70}]}),false);
for(const bad of ['javascript:alert(1)',
 'https://www.woodburn-or.gov.evil.example/report',
 'http://www.woodburn-or.gov/DocumentCenter/View/3298/report',
 'https://www.sanbruno.ca.gov/DocumentCenter/View/9280/doc?token=secret',
 'https://services.austintexas.gov/edims/document.cfm?id=452710&secret=1',
 'https://attorneygeneral.delaware.gov@evil.example/2026/post'])
 assert.equal(G.safe(bad),null);
assert.throws(()=>G.oversightCatalog({...reviewed,reports:[rows[0],rows[0],rows[2]]}),/Incomplete/);
assert.throws(()=>G.portals({...registry,sources:[...registry.sources,registry.sources[0]]}),/Unverified/);
const forged={...registry.sources[0],url:'https://other-site.example/'};
assert.equal(G.publisher(forged),false);
console.log('NATIONAL GOVERNMENT SOURCE PRESENTATION PASS: publisher independence, 6-state original registry, original page citations, unknown date, strict URLs and forgery guards');
