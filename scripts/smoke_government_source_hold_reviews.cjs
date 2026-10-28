'use strict';
const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const p=await b.newPage({viewport:{width:390,height:844}});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const res=await p.goto(new URL('government-source-hold-review.html',base).href,
   {waitUntil:'domcontentloaded',timeout:22000});
  assert.equal(res.status(),200);
  await p.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('12 historical official-source holds'),null,{timeout:12000});
  assert.equal(await p.locator('#stats .stat').count(),4);
  assert.equal(await p.locator('#cases article').count(),3);
  assert.match(await p.locator('#status').textContent(),/11 unresolved/);
  assert.match(await p.locator('#cases').textContent(),/Panama City Beach Police Department/);
  assert.match(await p.locator('#cases').textContent(),/Raleigh Police Department/);
  assert.match(await p.locator('#cases').textContent(),/superseded original government source lead/i);
  assert.equal(await p.locator('#cases a[href="https://www.lafayetteco.gov/m/newsflash/home/detail/10277"]').count(),1);
  assert.deepEqual(errors,[]);
  const next=await p.goto(new URL('agency-evidence-conversion.html',base).href,{waitUntil:'domcontentloaded',timeout:22000});
  assert.equal(next.status(),200);
  assert.equal(await p.locator('a[href="./government-source-hold-review.html"]').count(),1);
  console.log('REVIEW HELD GOV SOURCES CHROMIUM PASS: 12 historical sources, 1 superseded CO status, 11 still needing original verification, FL/NC held');
 }finally{await b.close();}
})().catch(e=>{console.error('GOV ORIGINAL HOLD REVIEW CHROMIUM FAILURE',e);process.exit(1)});
