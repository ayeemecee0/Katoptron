'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const r=await page.goto(new URL('robbinsdale-audits.html',base).href,
    {waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(r.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('Two separate original government-archived'),
    null,{timeout:18000});
  assert.equal(await page.locator('#audits article').count(),2);
  const text=await page.locator('#audits').textContent();
  assert.match(text,/2025 · FLOCK independent audit/);
  assert.match(text,/2026 · AXON independent audit/);
  assert.match(text,/two active stationary Flock ALPR units/);
  assert.match(text,/11 active AXON mobile/);
  assert.match(text,/no longer|30-day retention period|30-day default/);
  assert.match(await page.locator('#faq').textContent(),/two years/);
  assert.match(await page.locator('#comparison').textContent(),/How should the 2025 audit/);
  assert.ok((await page.locator('#audits a[href*="251675.pdf#page=2"]').count())>=2);
  assert.ok((await page.locator('#audits a[href*="260189.pdf#page=2"]').count())>=2);
  assert.equal(errors.length,0,errors.join('; '));
  await page.goto(new URL('nationwide-policy.html?state=MN',base).href,
   {waitUntil:'domcontentloaded',timeout:25000});
  await page.waitForFunction(()=>document.querySelector('#loadStatus')?.textContent?.includes('Validated 51/51'),
     null,{timeout:20000});
  await page.locator('#tier').selectOption('verified');
  assert.ok((await page.locator('a[href="./robbinsdale-audits.html"]').count())>=1);
  console.log('ROBBINSDALE HISTORICAL ORIGINAL AUDITS BROWSER PASS: MN links, correct vendor separation, source page 2 and outstanding disclosure question');
 }finally{await browser.close();}
})().catch(e=>{console.error('ROBBINSDALE AUDIT BROWSER FAILURE',e);process.exit(1);});
