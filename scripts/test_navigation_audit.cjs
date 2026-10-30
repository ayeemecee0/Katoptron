'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const nav=html.match(/<nav aria-label="Main navigation">([\s\S]*?)<\/nav>/)?.[1];
assert.ok(nav,'Homepage must have primary navigation');
const links=[...nav.matchAll(/href="([^"]+)"/g)].map(m=>m[1]);
assert.ok(links.length<=8,'Overloaded homepage: retain at most eight primary choices');
assert.equal(new Set(links).size,links.length,'No duplicated primary link');
for(const required of ['index.html','agency-xray.html','professional-intelligence.html',
 'research-workspace.html','government-watch.html','submit.html'])
 assert.ok(links.includes('./'+required),'Expected core user workflow '+required);
assert.ok(links.includes('#research-library'));
const archive=html.match(/<section class="sidebar-section" id="research-library"[\s\S]*?<\/section>/)?.[0];
assert.ok(archive&&archive.includes('<details>'));
for(const filename of ['community-map.html','nearby.html','records.html','portals.html',
 'accountability.html','agency-intelligence-hub.html','pilot-research.html','pilot-dossiers.html',
 'research-plans.html','nationwide-policy.html','nationwide-source-monitor.html',
 'nationwide-research-leads.html','nationwide-document-review.html','agency-evidence-conversion.html',
 'new-state-policy-originals.html','agency-audit.html','mn-alpr-audits.html',
 'original-acquisition.html','sharing-explorer.html','analytics.html','research-acquisition.html']){
 assert.ok(archive.includes('href="./'+filename+'"'),'Specialist route preserved: '+filename);
 assert.ok(fs.existsSync(path.join(root,filename)),'Specialist page must exist: '+filename);
}
console.log('NAVIGATION_AUDIT_PASS: 7 core links, specialist evidence archive accessible, no deletes');
