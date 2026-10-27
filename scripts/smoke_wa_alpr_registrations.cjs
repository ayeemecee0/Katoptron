'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const problems=[];page.on('pageerror',e=>problems.push(e.message));
 try{
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const response=await page.goto(new URL('wa-alpr-registrations.html',base).href,{waitUntil:'domcontentloaded',timeout:20000});
  assert.equal(response.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.startsWith('97 original Attorney General'),
    null,{timeout:12000});
  assert.equal(await page.locator('#results article').count(),97);
  await page.waitForFunction(()=>document.querySelector('#reviewedPolicyStatus')?.textContent?.startsWith('3 original agency'),
    null,{timeout:12000});
  assert.equal(await page.locator('#reviewedPolicyResults article').count(),3);
  await page.waitForFunction(()=>document.querySelector('#sourceTriageStatus')?.textContent?.includes('71 AGO-versioned'),
   null,{timeout:15000});
  assert.equal(await page.locator('#sourceTriageQueue article').count(),10);
  await page.waitForFunction(()=>document.querySelector('#heldOriginalStatus')?.textContent?.startsWith('7 original source'),
   null,{timeout:15000});
  assert.equal(await page.locator('#heldOriginalResults article').count(),7);
  const holdContent=await page.locator('#heldOriginalResults').textContent();
  assert.match(holdContent,/Kelso Police Department/);
  assert.match(holdContent,/Kittitas Police Department/);
  assert.match(holdContent,/Kirkland Police Department/);
  assert.match(holdContent,/Original PDF pages have no extractable content/);
  assert.match(holdContent,/Four-page image-based original requires visual review/);
  assert.match(holdContent,/Full policy manual exceeds bounded page guard/);
  assert.match(await page.locator('#heldOriginalEvidence').textContent(),/None is verified policy content or a confirmed Flock installation/);
  assert.equal(await page.locator('#heldOriginalResults a').count(),0);
  await page.waitForFunction(()=>document.querySelector('#flockOriginalStatus')?.textContent?.startsWith('8 individually original-page-reviewed'),
   null,{timeout:15000});
  assert.equal(await page.locator('#flockOriginalResults article').count(),9);
  assert.match(await page.locator('#flockOriginalResults').textContent(),/Federal Way Police Department/);
  assert.match(await page.locator('#flockOriginalResults').textContent(),/one Flock Safety location containing four fixed cameras/);
  assert.match(await page.locator('#flockOriginalResults').textContent(),/proposed second location/);
  assert.match(await page.locator('#flockOriginalResults').textContent(),/contradictory words and numerals/);
  assert.match(await page.locator('#flockOriginalResults').textContent(),/Sultan Police Department · Source attribution held/);
  const fc=await page.locator('#flockOriginalResults a').evaluateAll(as=>as.map(a=>a.href));
  assert.ok(fc.every(u=>u.startsWith('https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/')));
  assert.ok(!fc.some(u=>u.includes('Sultan%20PD%20Policy')));
  const queueSultan=page.locator('#sourceTriageQueue article').filter({hasText:'Sultan Police Department'});
  assert.equal(await queueSultan.locator('a').count(),0);
  assert.match(await queueSultan.textContent(),/Publisher identity mismatch/);
  const triage=await page.locator('#sourceTriageStatus').textContent();
  assert.match(triage,/64 machine-readable\/parseable PDF/);
  assert.match(triage,/7 source\(s\) held/);
  assert.match(triage,/11 separately page-reviewed/);
  assert.match(await page.locator('#sourceTriageMetrics').textContent(),/Original policies independently page-reviewed/);
  assert.match(await page.locator('#sourceTriageQueue').textContent(),/Arlington Police Department/);
  assert.match(await page.locator('#sourceTriageQueue').textContent(),/Normandy Park Police Department/);
  assert.match(await page.locator('#sourceTriageSection').textContent(),/not proof of installed cameras/);
  assert.ok((await page.locator('#sourceTriageQueue a').evaluateAll(as=>as.map(a=>a.href))).every(x=>
    x.startsWith('https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/')&&x.includes('#page=')));
  
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Auburn Police Department/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Black Diamond Police Department/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Normandy Park Police Department/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Flock Safety camera system/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/21 days/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Scanned original visually reviewed/);
  assert.match(await page.locator('#reviewedPolicyEvidence').textContent(),/not independent findings of compliance/);
  const originals=await page.locator('#reviewedPolicyResults a').evaluateAll(as=>as.map(a=>a.href));
  assert.ok(originals.some(x=>x.includes('VersionId=bPOrBG6TYUmkpHt6dVALLEcyhx2utLnH#page=5')));
  assert.ok(originals.some(x=>x.includes('/DocumentCenter/View/4324/BDPD-ALPR-Policy#page=4')));
  assert.ok(originals.some(x=>x.includes('VersionId=18O0TMpqPRPGCuXKIAFSRKWNSwGnRuaY#page=1')));
  assert.ok(originals.every(x=>x.startsWith('https://blackdiamondwa.gov/')||
    x.startsWith('https://agportal-s3bucket.s3.us-west-2.amazonaws.com/')));
  assert.match(await page.locator('main').textContent(),/has not independently verified/);
  const law=await page.locator('#washingtonLegalContext').textContent();
  assert.match(law,/March 30, 2026/);
  assert.match(law,/21 days/);
  assert.match(law,/specific exceptions/);
  assert.match(law,/July 1, 2027/);
  assert.match(law,/December 1, 2027/);
  assert.match(law,/December 1, 2026/);
  assert.match(law,/60-day Attorney General notice/);
  assert.match(law,/not findings that any listed agency uses Flock or complies with, or violates, the law/);
  const statutes=await page.locator('#washingtonLegalContext a').evaluateAll(as=>as.map(a=>a.href));
  assert.deepEqual(statutes,[
    'https://app.leg.wa.gov/RCW/default.aspx?cite=10.130.040',
    'https://app.leg.wa.gov/RCW/default.aspx?cite=10.130.030',
    'https://app.leg.wa.gov/RCW/default.aspx?cite=10.130.070'
  ]);

  assert.match(await page.locator('main').textContent(),/not a camera or equipment census/);
  assert.match(await page.locator('#stats').textContent(),/96/);
  const hrefs=await page.locator('#results article a').evaluateAll(as=>as.map(a=>a.href));
  assert.ok(hrefs.some(h=>h.includes('agportal-s3bucket.s3.us-west-2.amazonaws.com')));
  assert.ok(!hrefs.some(h=>h.includes('evil.example')));
  await page.locator('#search').fill('Aberdeen Police');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/Aberdeen Police Department/);
  await page.locator('#search').fill('Auburn Police');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/Read individually page-reviewed original policy summary/);
  await page.locator('#search').fill('Black Diamond');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/Read individually page-reviewed original policy summary/);
  await page.locator('#search').fill('Kelso Police');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/Original PDF pages have no extractable content/);
  await page.locator('#search').fill('Federal Way');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/individually verified original Flock-reference summary/);
  await page.locator('#search').fill('Sultan Police');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/Attribution hold/);
  assert.equal(await page.locator('#results article a').count(),0);
  assert.match(await page.locator('#results').textContent(),/held from direct promotion/);
  await page.locator('#search').fill('Normandy Park');
  assert.equal(await page.locator('#results article').count(),1);
  assert.match(await page.locator('#results').textContent(),/Read individually page-reviewed original policy summary/);
  await page.locator('#search').fill('Aberdeen Police');
  await page.locator('#search').fill('Cascadia');
  assert.equal(await page.locator('#results article').count(),1);
  await page.locator('#search').fill('ThereIsNoSuchAgencyXY');
  assert.equal(await page.locator('#results article').count(),0);
  assert.match(await page.locator('#results').textContent(),/does not establish/);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'Mobile 390px no horizontal overflow');
  assert.deepEqual(problems,[]);
  console.log('WASHINGTON OFFICIAL AGO REGISTER BROWSER PASS: 97 self-attested agencies, public policy links, no Flock assertion, source date, search & 390px');
 }catch(e){console.error('WA GOVERNMENT REGISTRY BROWSER FAILED',e.stack||e,problems);process.exitCode=1;}
 finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
