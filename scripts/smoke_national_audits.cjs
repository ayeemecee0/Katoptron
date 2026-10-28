'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const res=await page.goto(new URL('national-audits.html',base).href,{waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(res.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('source-pinned original'),
    null,{timeout:15000});
  assert.match(await page.locator('#status').textContent(),/^4 source-pinned/);
  assert.equal(await page.locator('#results article').count(),4);
  await page.waitForFunction(()=>document.querySelector('#riSdPolicyStatus')?.textContent?.startsWith('2 independently original-page-reviewed'),
   null,{timeout:15000});
  assert.equal(await page.locator('#riSdPolicyResults article').count(),2);
  const newPolicies=await page.locator('#riSdPolicyVersions').textContent();
  assert.match(newPolicies,/Providence Police Department/);
  assert.match(newPolicies,/Brookings Police Department/);
  assert.match(newPolicies,/September 4 and Brookings revised September 22/);
  assert.match(newPolicies,/Flock Safety as an ALPR data hosting vendor/);
  assert.match(newPolicies,/maximum of 30 days/);
  assert.match(newPolicies,/internal audit of ALPR database searching every 30 days/);
  assert.match(newPolicies,/federal immigration enforcement/);
  assert.match(newPolicies,/Chief of Police signature/);
  assert.match(newPolicies,/not independently confirmed system configuration/);
  const policyLinks=await page.locator('#riSdPolicyResults a').evaluateAll(as=>as.map(a=>a.href));
  assert.ok(policyLinks.some(x=>x.includes('/2026/10/350.05-Automated-License-Plate-Readers-ALPR.pdf#page=7')));
  assert.ok(policyLinks.some(x=>x.includes('/Policy-13D1---Automated-License-Plate-Recognition-System#page=5')));
  assert.ok(policyLinks.every(x=>x.startsWith('https://ppd.providenceri.gov/')||x.startsWith('https://www.cityofbrookings-sd.gov/')));

  await page.waitForFunction(()=>document.querySelector('#okcOriginalStatus')?.textContent?.startsWith('4 source-pinned original'),
    null,{timeout:15000});
  assert.equal(await page.locator('#okcOriginalResults article').count(),5);
  const okc=await page.locator('#okcContractOriginals').textContent();
  assert.match(okc,/signed Flock amendment/i);
  assert.match(okc,/approved renewal/i);
  assert.match(okc,/staff recommendation/i);
  assert.match(okc,/funds certificate/i);
  assert.match(okc,/\$270,000/);
  assert.match(okc,/90City-reported 2026 Flock readers/);
  assert.match(okc,/109City-reported partner agencies/);
  assert.match(okc,/7City-stated default retention/);
  assert.match(okc,/does not prohibit the city itself from sharing data/);
  assert.match(okc,/compelled disclosures/);
  assert.match(okc,/the mayor's signed approval dated August 18, 2026/);
  assert.match(okc,/recommendation, not a final vote/);
  assert.match(okc,/not proof that \$270,000 was spent/);
  assert.match(okc,/not independent verification of installed locations/);
  const okcLinks=await page.locator('#okcOriginalResults a').evaluateAll(as=>as.map(a=>a.href));
  assert.ok(okcLinks.some(x=>x.includes('/flock-amendment-august-2026.pdf#page=2')));
  assert.ok(okcLinks.some(x=>x.includes('/flock-renewal-letter-august-2026.pdf#page=1')));
  assert.ok(okcLinks.some(x=>x.includes('/flock-council-memo-august-2026.pdf#page=1')));
  assert.ok(okcLinks.some(x=>x.includes('/availability-of-funds-certificate-august-2026.pdf#page=1')));
  assert.ok(okcLinks.some(x=>x.includes('/Flock-Safety-license-plate-reader-LPR-usage-in-Oklahoma-City')));
  assert.ok(okcLinks.every(x=>x.startsWith('https://www.okc.gov/')));

  await page.waitForFunction(()=>document.querySelector('#nebraskaAggregateStatus')?.textContent?.startsWith('1 source-pinned, visually reviewed'),
   null,{timeout:15000});
  assert.equal(await page.locator('#nebraskaAggregateResults article').count(),1);
  const ne=await page.locator('#nebraskaAggregateResults').textContent();
  assert.match(ne,/Dakota County Sheriff's Office/);
  assert.match(ne,/43 · NCIC list confirmed matches/);
  assert.match(ne,/0 · NCIC list non-correlated matches/);
  assert.match(ne,/126 · Manually entered plate-number queries/);
  assert.match(ne,/19 · Manual-entry confirmed matches/);
  assert.match(ne,/1 · Manual-entry non-correlated matches/);
  assert.match(ne,/no populated reporting figures/);
  assert.match(ne,/does not prove the equipment manufacturer/);
  const neLinks=await page.locator('#nebraskaAggregateResults a').evaluateAll(as=>as.map(a=>a.href));
  assert.equal(neLinks.length,1);
  assert.ok(neLinks[0].startsWith('https://ncc.nebraska.gov/sites/default/files/Dakota%20County%20FLOCK%20REPORT%202025%20TO%20STATE.pdf'));
  assert.ok(neLinks[0].endsWith('#page=1'));
 
  await page.waitForFunction(()=>document.querySelector('#nationalCoverageStatus')?.textContent?.startsWith('51 jurisdictions enrolled.'),
   null,{timeout:15000});
  assert.match(await page.locator('#nationalCoverageStatus').textContent(),/51 have an original-government publication seed; 0 lack one/);
  const nationwide=await page.locator('#nationalCoverageMetrics').textContent();
  assert.match(nationwide,/51US states and DC enrolled/);
  assert.match(nationwide,/57Official publication links curated/);
  assert.match(nationwide,/31New government originals reachable at inspection/);
  assert.match(nationwide,/12New original sources held for verification/);
  assert.match(await page.locator('#nationalCoverageStatus').textContent(),/31 checked original sources retrieved; 12 held/);
  await page.locator('#nationalCoverageDetails').evaluate(x=>x.open=true);
  assert.equal(await page.locator('#nationalCoverageResults article').count(),51);
  assert.match(await page.locator('#nationalCoverage').textContent(),/not an independently verified Flock installation/);
  assert.match(await page.locator('#nationalCoverageResults').textContent(),/District of Columbia/);
  assert.match(await page.locator('#nationalCoverageResults').textContent(),/Alaska/);
  assert.match(await page.locator('#nationalCoverageResults').textContent(),/Wyoming/);
  assert.ok((await page.locator('#nationalCoverageResults a').evaluateAll(as=>as.map(a=>a.href))).every(u=>
   u.startsWith('https://')&&(u.includes('.gov/')||
    ['https://www.state.wv.us/','https://www.moline.il.us/',
     'https://www.naperville.il.us/','https://www.darien.il.us/'].some(prefix=>u.startsWith(prefix)))));
  await page.locator('#nationalCoverageSearch').fill('New York');
  assert.equal(await page.locator('#nationalCoverageResults article').count(),1);
  assert.match(await page.locator('#nationalCoverageResults').textContent(),/model policy not agency adoption/);
  await page.locator('#nationalCoverageSearch').fill('Wyoming');
  assert.equal(await page.locator('#nationalCoverageResults article').count(),1);
  assert.match(await page.locator('#nationalCoverageResults').textContent(),/unadopted state bill/);
  await page.locator('#nationalCoverageSearch').fill('Nevada');
  assert.match(await page.locator('#nationalCoverageResults').textContent(),/Source currently held/);
  await page.locator('#nationalCoverageSearch').fill('West Virginia');
  assert.equal(await page.locator('#nationalCoverageResults article').count(),1);
  assert.match(await page.locator('#nationalCoverageResults').textContent(),/other vendor alpr procurement not flock/);
  await page.locator('#nationalCoverageSearch').fill('');
  assert.equal(await page.locator('#nationalCoverageResults article').count(),51);
 
  await page.waitForFunction(()=>document.querySelector('#cityStatusState')?.textContent?.startsWith('2 dated original city'),
   null,{timeout:15000});
  assert.equal(await page.locator('#cityStatusResults article').count(),2);
  const statuses=await page.locator('#cityStatusResults').textContent();
  assert.match(statuses,/Moline Police Department/);
  assert.match(statuses,/City of Mill Valley/);
  assert.match(statuses,/Planned shutdown; completion not independently established/);
  assert.match(statuses,/City-reported cameras disabled at publication/);
  assert.match(statuses,/September 9, 2026/);
  assert.match(statuses,/not a third-party forensic audit/);
  assert.match(statuses,/Current live status remains unverified/);
  const cityUrls=await page.locator('#cityStatusResults a').evaluateAll(as=>as.map(a=>a.href));
  assert.deepEqual(cityUrls.sort(),[
    'https://www.cityofmillvalley.gov/m/newsflash/home/detail/1639',
    'https://www.moline.il.us/1955/License-Plate-Readers'
  ].sort());
  await page.waitForFunction(()=>document.querySelector('#oversightStatus')?.textContent?.startsWith('3 original government oversight'),
    null,{timeout:15000});
  await page.waitForFunction(()=>document.querySelector('#publisherStatus')?.textContent?.startsWith('14 official government'),
    null,{timeout:15000});
  assert.equal(await page.locator('#oversightResults article').count(),3);
  await page.waitForFunction(()=>document.querySelector('#primaryStatus')?.textContent?.startsWith('10 page-verified'),
   null,{timeout:18000});
  assert.equal(await page.locator('#primaryResults article').count(),10);
  assert.match(await page.locator('#primaryStatus').textContent(),/1 source\(s\) remain unavailable/);
  assert.match(await page.locator('#policyContrast').textContent(),/30-day maximum/);
  assert.match(await page.locator('#policyContrast').textContent(),/not verified as adopted/i);
  const primary=await page.locator('#primaryResults').textContent();
  assert.match(primary,/443,664 unique plate reads/);
  assert.match(primary,/seven days/i);
  assert.match(primary,/City Council ordered a halt/);
  assert.match(primary,/1,392,000/);
  assert.match(primary,/Moline Police Department/);
  assert.match(primary,/27,624\.98/);
  assert.match(primary,/visually reviewed scanned pages/i);
  assert.match(primary,/Signed in December 2024/);
  assert.match(primary,/one-time \$4,500 fee/);
  assert.match(primary,/February 1, 2028/);
  assert.match(primary,/not a verification that Flock equipment was actually disabled or removed/);
  assert.match(await page.locator('#molineContrast').textContent(),/cannot be treated as a verified five-camera expansion/);
  assert.ok((await page.locator('#primaryResults a').evaluateAll(as=>as.map(a=>a.href)))
   .some(x=>x.includes('/DocumentCenter/View/16700/Flock-Safety-Contract-Pause-September-2026#page=1')));
  assert.ok((await page.locator('#primaryResults a').evaluateAll(as=>as.map(a=>a.href)))
    .some(x=>x.includes('/DocumentCenter/View/15716/Flock-Safety-2023#page=5')));
  const pageLinks=await page.locator('#primaryResults a').evaluateAll(as=>as.map(x=>x.href));
  assert.ok(pageLinks.some(x=>x.includes('/DocumentCenter/View/19136/')&&x.includes('#page=4')));
  assert.ok(pageLinks.some(x=>x.includes('document.cfm?id=452847#page=3')));

  assert.equal(await page.locator('#publisherResults article').count(),14);
  const reviewed=await page.locator('#oversightResults').textContent();
  assert.match(reviewed,/San Mateo County Civil Grand Jury/);
  assert.match(reviewed,/Austin Police Department/);
  assert.match(reviewed,/Woodburn Police Department/);
  assert.match(reviewed,/Independent government oversight/);
  assert.match(reviewed,/Agency-authored impact assessment, not independent/);
  assert.match(reviewed,/NOT 582 individually verified Flock cameras/i);
  assert.match(reviewed,/May 2025/);
  const oversightLinks=await page.locator('#oversightResults a').evaluateAll(links=>links.map(x=>x.href));
  for(const href of oversightLinks)
   assert.ok(href.startsWith('https://sanmateo.courts.ca.gov/')||
    href.startsWith('https://services.austintexas.gov/')||
    href.startsWith('https://www.woodburn-or.gov/'));
  assert.ok(oversightLinks.some(x=>x.includes('auto-license-plate-readers-report.pdf#page=2')));
  assert.ok(oversightLinks.some(x=>x.includes('document.cfm?id=452710#page=2')));

  assert.match(await page.locator('main').textContent(),/not external independent audits/i);
  assert.match(await page.locator('#results').textContent(),/Northern California Regional Intelligence Center/);
  assert.match(await page.locator('#results').textContent(),/299 agencies/);
  assert.match(await page.locator('#results').textContent(),/internally contradictory date header/);
  for(const href of await page.locator('#results a').evaluateAll(as=>as.map(a=>a.href)))
   assert.ok(href.startsWith('https://www.lrl.mn.gov/')||
     href.startsWith('https://www.sanbruno.ca.gov/')||
     href.startsWith('https://www.greenbaywi.gov/'),'Only government originals may be linked');
  await page.locator('#state').selectOption('TX');
  assert.equal(await page.locator('#primaryResults article').count(),3);
  assert.equal(await page.locator('#cityStatusResults article').count(),0);
  assert.equal(await page.locator('#oversightResults article').count(),1);
  assert.equal(await page.locator('#publisherResults article').count(),2);
  await page.locator('#state').selectOption('IL');
  assert.equal(await page.locator('#cityStatusResults article').count(),1);
  assert.match(await page.locator('#cityStatusResults').textContent(),/Moline Police Department/);
  await page.locator('#state').selectOption('WI');
  assert.equal(await page.locator('#results article').count(),1);
  assert.equal(await page.locator('#oversightResults article').count(),0);
  assert.match(await page.locator('#results').textContent(),/Green Bay/);
  await page.locator('#state').selectOption('CA');
  assert.equal(await page.locator('#results article').count(),2);
  assert.equal(await page.locator('#cityStatusResults article').count(),1);
  assert.match(await page.locator('#cityStatusResults').textContent(),/Mill Valley/);
  await page.locator('#q').fill('29 Flock');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/July 2026/);
  const fits=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2);
  assert.ok(fits,'390px national report cards must fit viewport');
  assert.deepEqual(errors,[]);
  console.log('MULTISTATE PUBLIC AUDIT BROWSER PASS: attribution, original page citations, unsafe links, filter and mobile');
 }catch(e){console.error('MULTISTATE AUDIT SMOKE FAILED',e.stack||e,errors);process.exitCode=1;}
 finally{await browser.close();}
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
