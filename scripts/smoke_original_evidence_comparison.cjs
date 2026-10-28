'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const res=await page.goto(new URL('agency-compare.html',base).href,
   {waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(res.status(),200);
  await page.waitForFunction(()=>document.querySelector('#loadStatus')?.textContent?.includes('18 individually source-identified'),
   null,{timeout:20000});
  assert.equal(await page.locator('#agencyA option').count(),19);
  assert.ok(!((await page.locator('#agencyA').textContent()).includes('Sultan')));
  assert.equal(await page.locator('#agencyA').inputValue(),'providence-police-ri');
  assert.equal(await page.locator('#agencyB').inputValue(),'brookings-police-sd');
  assert.equal(await page.locator('#comparison article.agency').count(),2);
  await page.locator('#topic').selectOption('retention');
  assert.match(await page.locator('#compareStatus').textContent(),/reviewed original-page finding/i);
  assert.match(await page.locator('#comparison').textContent(),/30 days/);
  const citations=await page.locator('#comparison a').evaluateAll(as=>as.map(a=>a.href));
  assert.ok(citations.length>=2);
  assert.ok(citations.every(x=>x.startsWith('https://')&&x.includes('#page=')));
  const compareLink=await page.locator('#share').getAttribute('href');
  assert.match(compareLink,/topic=retention/);
  assert.match(compareLink,/a=providence-police-ri/);
  assert.match(compareLink,/b=brookings-police-sd/);
  await page.locator('#agencyC').selectOption('auburn-police-wa');
  assert.equal(await page.locator('#comparison article.agency').count(),3);
  assert.match(await page.locator('#comparison').textContent(),/21 days/);
  await page.locator('#agencyB').selectOption('providence-police-ri');
  assert.match(await page.locator('#compareStatus').textContent(),/distinct/);
  assert.equal(await page.locator('#comparison article.agency').count(),0);
  assert.equal(await page.locator('#share').isHidden(),true);
  assert.equal(errors.length,0,errors.join('; '));
  await page.goto(new URL('agency-compare.html?a=kittitas-police-wa&b=mukilteo-police-wa&topic=retention',base).href,
   {waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#comparison')?.textContent?.includes('DRAFT'),
   null,{timeout:18000});
  assert.match(await page.locator('#comparison').textContent(),/not validated retention practice/i);
  assert.match(await page.locator('#comparison').textContent(),/attorney general registration date not policy date/);
  await page.locator('#topic').selectOption('contracts');
  assert.match(await page.locator('#comparison').textContent(),/No reviewed original-page finding indexed for this topic/);
  await page.goto(new URL('agency-compare.html?a=green-bay-police-wi&b=providence-police-ri&topic=retention',base).href,
   {waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#comparison')?.textContent?.includes('Green Bay Police Department'),
   null,{timeout:18000});
  const green=await page.locator('#comparison').textContent();
  assert.match(green,/30-day maximum/);
  assert.match(green,/seven days/);
  assert.match(green,/not a verified adopted policy change/);
  assert.match(green,/Original date unverified/);
  await page.locator('#topic').selectOption('all');
  assert.match(await page.locator('#comparison').textContent(),/not independently confirmed/);
  assert.equal(errors.length,0,errors.join('; '));
  console.log('AGENCY ORIGINAL COMPARISON CHROMIUM PASS: 18 agencies, topic scope, source-page deep links, missing evidence, duplicate rejection and narrow-screen view');
 }finally{await browser.close();}
})().catch(e=>{console.error('AGENCY ORIGINAL COMPARISON FAILED',e);process.exit(1);});
