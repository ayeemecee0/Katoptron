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
  assert.match(await page.locator('main').textContent(),/not external independent audits/i);
  assert.match(await page.locator('#results').textContent(),/Northern California Regional Intelligence Center/);
  assert.match(await page.locator('#results').textContent(),/299 agencies/);
  assert.match(await page.locator('#results').textContent(),/internally contradictory date header/);
  for(const href of await page.locator('#results a').evaluateAll(as=>as.map(a=>a.href)))
   assert.ok(href.startsWith('https://www.lrl.mn.gov/')||
     href.startsWith('https://www.sanbruno.ca.gov/')||
     href.startsWith('https://www.greenbaywi.gov/'),'Only government originals may be linked');
  await page.locator('#state').selectOption('WI');
  assert.equal(await page.locator('#results article').count(),1);
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
