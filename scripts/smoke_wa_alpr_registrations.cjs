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
  await page.waitForFunction(()=>document.querySelector('#reviewedPolicyStatus')?.textContent?.startsWith('2 original agency'),
    null,{timeout:12000});
  assert.equal(await page.locator('#reviewedPolicyResults article').count(),2);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Auburn Police Department/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Black Diamond Police Department/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/21 days/);
  assert.match(await page.locator('#reviewedPolicyResults').textContent(),/Scanned original visually reviewed/);
  assert.match(await page.locator('#reviewedPolicyEvidence').textContent(),/not independent findings of compliance/);
  const originals=await page.locator('#reviewedPolicyResults a').evaluateAll(as=>as.map(a=>a.href));
  assert.ok(originals.some(x=>x.includes('VersionId=bPOrBG6TYUmkpHt6dVALLEcyhx2utLnH#page=5')));
  assert.ok(originals.some(x=>x.includes('/DocumentCenter/View/4324/BDPD-ALPR-Policy#page=4')));
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
