'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url=new URL('nationwide-source-monitor.html',process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/');
 try{
  const r=await page.goto(url.href,{waitUntil:'domcontentloaded',timeout:30000});
  assert.equal(r.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('Verified 51-state'),null,{timeout:22000});
  assert.equal(await page.locator('#states tr').count(),51);
  assert.equal(await page.locator('#metrics .metric').count(),6);
  assert.match(await page.locator('#metrics').textContent(),/81/);
  assert.match(await page.locator('#metrics').textContent(),/38/);
  assert.match(await page.locator('#baselineDate').textContent(),/2026-10-27/);
  await page.locator('#filter').fill('DE');
  assert((await page.locator('#states tr').count())>0);
  await page.locator('#filter').fill('');
  await page.locator('#states button').first().click();
  assert((await page.locator('#sourceDetails article').count())>0);
  assert.match(await page.locator('#sourceDetails').textContent(),/not independently verified|No archived retrieval/);
  const leading=await page.goto(new URL('nationwide-research-leads.html',process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/').href,{waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(leading.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('15 independently reviewed original-source'),null,{timeout:15000});
  assert.equal(await page.locator('#leads article').count(),15);
  const urls=await page.locator('#leads a').evaluateAll(all=>all.map(x=>x.href));
  assert(urls.every(x=>x.startsWith('https://')));
  assert.match(await page.locator('#leads').textContent(),/unresolved|Unresolved/i);
  const review=await page.goto(new URL('nationwide-document-review.html',process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/').href,{waitUntil:'domcontentloaded',timeout:20000});
  assert.equal(review.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('15 changed-source candidates triaged'),null,{timeout:14000});
  assert.equal(await page.locator('#changed article').count(),15);
  assert.equal(await page.locator('#held article').count(),13);
  assert.equal(await page.locator('#depth article').count(),8);
  assert.match(await page.locator('#status').textContent(),/No original-document wording change automatically approved/);
  assert.deepEqual(errors,[]);
  console.log('NATIONWIDE_SOURCE_MONITOR_BROWSER_PASS: 51 rows, 81 curated URLs, archived vs unobserved sources, no false statewide coverage');
 }catch(e){
  console.error('NATIONWIDE_SOURCE_MONITOR_BROWSER_FAILED',e.stack||e.message,
   'STATUS',await page.locator('#status').textContent().catch(()=>'?'),'ERRORS',errors);
  process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
