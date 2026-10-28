'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await b.newPage({viewport:{width:390,height:844}});
  const errors=[];page.on('pageerror',err=>errors.push(err.message));
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const response=await page.goto(new URL('robbinsdale-audit.html',base).href,
    {waitUntil:'domcontentloaded',timeout:23000});
  assert.equal(response.status(),200);
  await page.waitForFunction(()=>document.querySelector('#sourceStatus')?.textContent?.includes('Five source findings'),null,{timeout:16000});
  assert.equal(await page.locator('#summary article').count(),2);
  assert.equal(await page.locator('#timeline article').count(),5);
  assert.equal(await page.locator('#findings article').count(),5);
  assert.equal(await page.locator('#findings a[href$="#page=2"]').count(),2);
  assert.equal(await page.locator('#findings a[href$="#page=5"]').count(),1);
  const pageText=await page.locator('main').textContent();
  assert.match(pageText,/License-plate photos retained two years|license-plate photographs retained two years|license-plate photographs retained two years/i);
  assert.match(pageText,/hits retained 30 days/);
  assert.match(pageText,/Not established as a contradiction/);
  assert.match(pageText,/currently configured|current platform access/);
  assert.match(pageText,/does not prove the legal status/i);
  assert.deepEqual(errors,[]);
  const xray=await page.goto(new URL('agency-xray.html',base).href,{waitUntil:'domcontentloaded'});
  assert.equal(xray.status(),200);
  assert.equal(await page.locator('a[href="./robbinsdale-audit.html"]').count(),1);
  const agency=await page.goto(new URL('agency-evidence-conversion.html',base).href,{waitUntil:'domcontentloaded'});
  assert.equal(agency.status(),200);
  assert.equal(await page.locator('#auditedIndependent a[href="./robbinsdale-audit.html"]').count(),1);
  console.log('ROBBINSDALE SOURCE-ORIGINAL CHROMIUM PASS: five state-archived historical audit pages, separately attributed 2026 retention categories, no fake present camera claims');
 }finally{await b.close();}
})().catch(e=>{console.error('ROBBINSDALE SOURCE ORIGINAL CHROMIUM FAIL',e);process.exit(1);});
