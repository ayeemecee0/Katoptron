'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const res=await page.goto(new URL('policy-history.html',base).href,
   {waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(res.status(),200);
  await page.waitForFunction(()=>document.querySelector('#loadStatus')?.textContent?.includes('original-page-reviewed policy documents'),
   null,{timeout:18000});
  assert.ok((await page.locator('#agency option').count())>=12);
  assert.equal(await page.locator('#agency').inputValue(),'green-bay-police-wi');
  assert.equal(await page.locator('#history article').count(),2);
  assert.match(await page.locator('#history').textContent(),/30-day maximum/);
  assert.match(await page.locator('#history').textContent(),/seven days/);
  assert.match(await page.locator('#history').textContent(),/DRAFT · NOT VERIFIED ADOPTED/);
  assert.match(await page.locator('#comparisons').textContent(),/proposed change only/);
  assert.match(await page.locator('#comparisons').textContent(),/not proof of adoption/);
  const links=await page.locator('#comparisons a').evaluateAll(as=>as.map(a=>a.href));
  assert.equal(links.length,2);
  assert.ok(links.every(x=>x.startsWith('https://www.greenbaywi.gov/')&&/#page=\d+/.test(x)));
  assert.match(await page.locator('#watchStatus').textContent(),/off by default|No on-device source watch/);
  await page.locator('#track').click();
  assert.match(await page.locator('#watchStatus').textContent(),/0 new source-verified/);
  assert.equal(await page.locator('#review').isDisabled(),true);
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#loadStatus')?.textContent?.includes('original-page-reviewed policy documents'),
   null,{timeout:18000});
  assert.match(await page.locator('#watchStatus').textContent(),/0 new source-verified/);
  assert.equal(await page.locator('#track').isDisabled(),true);
  await page.locator('#untrack').click();
  assert.equal(await page.locator('#track').isDisabled(),false);
  await page.locator('#agency').selectOption('kittitas-police-wa');
  assert.match(await page.locator('#history').textContent(),/DRAFT · NOT VERIFIED ADOPTED/);
  assert.equal(await page.locator('#comparisonSection').isHidden(),true);
  assert.ok(!((await page.locator('#agency').textContent()).includes('Sultan')));
  assert.equal(errors.length,0,errors.join('; '));
  await page.goto(new URL('policy-history.html?agency=providence-police-ri',base).href,
   {waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#agency')?.value==='providence-police-ri',
   null,{timeout:18000});
  assert.match(await page.locator('#history').textContent(),/General Order 350.05/);
  console.log('POLICY HISTORY BROWSER PASS: verified source versions, Green Bay proposal vs published, mobile original-page links, Kittitas draft and on-device opt-in without replay');
 }finally{await browser.close();}
})().catch(e=>{console.error('POLICY HISTORY BROWSER FAILED',e);process.exit(1);});
