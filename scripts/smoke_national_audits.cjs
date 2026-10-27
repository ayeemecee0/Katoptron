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
  await page.waitForFunction(()=>document.querySelector('#oversightStatus')?.textContent?.startsWith('3 original government oversight'),
    null,{timeout:15000});
  await page.waitForFunction(()=>document.querySelector('#publisherStatus')?.textContent?.startsWith('14 official government'),
    null,{timeout:15000});
  assert.equal(await page.locator('#oversightResults article').count(),3);
  await page.waitForFunction(()=>document.querySelector('#primaryStatus')?.textContent?.startsWith('8 page-verified'),
   null,{timeout:18000});
  assert.equal(await page.locator('#primaryResults article').count(),8);
  assert.match(await page.locator('#primaryStatus').textContent(),/1 source\(s\) remain unavailable/);
  assert.match(await page.locator('#policyContrast').textContent(),/30-day maximum/);
  assert.match(await page.locator('#policyContrast').textContent(),/not verified as adopted/i);
  const primary=await page.locator('#primaryResults').textContent();
  assert.match(primary,/443,664 unique plate reads/);
  assert.match(primary,/seven days/i);
  assert.match(primary,/City Council ordered a halt/);
  assert.match(primary,/1,392,000/);
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
  assert.equal(await page.locator('#oversightResults article').count(),1);
  assert.equal(await page.locator('#publisherResults article').count(),2);
  await page.locator('#state').selectOption('WI');
  assert.equal(await page.locator('#results article').count(),1);
  assert.equal(await page.locator('#oversightResults article').count(),0);
  assert.match(await page.locator('#results').textContent(),/Green Bay/);
  await page.locator('#state').selectOption('CA');
  assert.equal(await page.locator('#results article').count(),2);
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
