'use strict';
const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const p=await browser.newPage({viewport:{width:390,height:844}});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const response=await p.goto(new URL('new-state-policy-originals.html',base).href,{waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(response.status(),200);
  await p.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('Two original, source-page-reviewed'),null,{timeout:18000});
  assert.equal(await p.locator('#documents > section').count(),2);
  assert.equal(await p.locator('#documents section').first().locator('article').count(),4);
  assert.equal(await p.locator('#documents section').nth(1).locator('article').count(),7);
  assert.equal(await p.locator('article a[href$="#page=1"]').count(),3);
  assert.equal(await p.locator('article a[href$="#page=9"]').count(),1);
  assert.match(await p.locator('main').textContent(),/30-day retention/);
  assert.match(await p.locator('main').textContent(),/annual surveillance report|annual public report deadline/i);
  assert.match(await p.locator('#status').textContent(),/zero additional current camera positions/);
  assert.deepEqual(errors,[]);
  const map=await p.goto(new URL('index.html',base).href,{waitUntil:'domcontentloaded',timeout:20000});
  assert.equal(map.status(),200);
  assert.equal(await p.locator('a[href="./new-state-policy-originals.html"]').count(),1);
  console.log('ORIGINAL TWO-STATE PAGE CHROMIUM PASS: Idaho/Missouri source citations, policy boundaries, main map navigation and no live equipment claims');
 }finally{await browser.close();}
})().catch(e=>{console.error('TWO-STATE SOURCE CHROMIUM FAIL',e);process.exit(1)});
