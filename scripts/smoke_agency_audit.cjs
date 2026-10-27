'use strict';
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const problems=[],base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const page=await browser.newPage({viewport:{width:390,height:844}});
 page.on('pageerror',e=>problems.push(e.message));
 try{
  const r=await page.goto(new URL('agency-audit.html',base).href,{waitUntil:'domcontentloaded',timeout:40000});
  assert.equal(r.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('indexed localities'),
   null,{timeout:65000});
  await page.locator('#q').fill('Folsom');
  const option=page.locator('#matches button').filter({hasText:'Folsom, CA'}).first();
  assert.equal(await option.count(),1,'Known source-backed Folsom locality not indexed');
  await option.click();
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('Audit generated'),
    null,{timeout:55000});
  assert.equal(await page.locator('#report').isVisible(),true);
  assert.match(await page.locator('#reportTitle').textContent(),/Folsom/);
  assert.match(await page.locator('#disclaimer').textContent(),/NOT a legality/);
  assert.match(await page.locator('#counts').textContent(),/Flock portal snapshots/);
  const refs=page.locator('#sources a');
  assert.ok(await refs.count()>0,'Audit must show citable original source URLs');
  for(const href of await refs.evaluateAll(as=>as.slice(0,10).map(a=>a.href)))
    assert.ok(href.startsWith('https://'),'Source links must be HTTPS');
  assert.ok(!(await page.locator('#findings').textContent()).includes('noncompliant'),
    'Do not present inferred wrongdoing');
  await page.locator('#draft').click();
  assert.equal(await page.locator('#requestText').isVisible(),true);
  assert.match(await page.locator('#requestText').inputValue(),/DRAFT ONLY — NOT SENT/);
  assert.match(await page.locator('#requestText').inputValue(),/not requesting individual plate reads/i);
  const link=page.url();
  assert.ok(link.includes('place=folsom%7CCA'),'Reproducible permalink missing');
  const width=await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+2);
  assert.ok(width,'Mobile layout overflows viewport');
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('Audit generated'),
    null,{timeout:65000});
  assert.match(await page.locator('#reportTitle').textContent(),/Folsom/);
  await page.goto(new URL('agency-audit.html?place=shakopee%7CMN',base).href,
    {waitUntil:'domcontentloaded',timeout:40000});
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('Audit generated'),
    null,{timeout:55000});
  assert.match(await page.locator('#reportTitle').textContent(),/Shakopee, MN/);
  assert.match(await page.locator('#counts').textContent(),/Independent original audit reports/);
  assert.match(await page.locator('#sources').textContent(),/Independent audit of Shakopee Police Department ALPR system/);
  assert.match(await page.locator('#sources').textContent(),/30-day retention setting/);
  assert.match(await page.locator('#historicalFindings').textContent(),/Different ALPR technologies documented across audits/);
  assert.match(await page.locator('#historicalFindings').textContent(),/Elsag/);
  assert.match(await page.locator('#historicalFindings').textContent(),/Axon/);
  assert.ok(!(await page.locator('#historicalFindings').textContent()).includes('(+'),
   'Different mobile/fixed systems cannot be combined as a numeric increase');
  assert.ok((await page.locator('#sources a').evaluateAll(links=>
    links.some(a=>a.href.startsWith('https://www.lrl.mn.gov/docs/2026/mandated/261013.pdf')))),
    'Original Minnesota archive evidence source must be directly inspectable');
  for(const [id,name,sourceFragment] of [
   ['stillwater%7CMN','Stillwater, MN','17 stationary Flock ALPR units'],
   ['hennepin%20county%7CMN','Hennepin County, MN','four active stationary Flock ALPR units'],
   ['richfield%7CMN','Richfield, MN','eight stationary Flock ALPR units'],
   ['woodbury%7CMN','Woodbury, MN','17 active stationary Flock ALPR units'],
   ['brooklyn%20center%7CMN','Brooklyn Center, MN','nine active stationary ALPR units'],
   ['champlin%7CMN','Champlin, MN','six active stationary/flex Flock ALPR devices'],
   ['corcoran%7CMN','Corcoran, MN','nine active stationary Flock ALPR units'],
   ['orono%7CMN','Orono, MN','three active stationary/flex ALPR devices']
  ]){
   await page.goto(new URL('agency-audit.html?place='+id,base).href,
     {waitUntil:'domcontentloaded',timeout:40000});
   await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('Audit generated'),
     null,{timeout:55000});
   assert.equal(await page.locator('#reportTitle').textContent(),name);
   assert.match(await page.locator('#counts').textContent(),new RegExp((name==='Woodbury, MN'?'2':'1')+'Independent original audit reports'));
   assert.ok((await page.locator('#sources').textContent()).includes(sourceFragment),
     'Publisher-attributed dated exact-identity observations should appear');
   assert.match(await page.locator('#disclaimer').textContent(),/NOT a legality/);
  }
  await page.goto(new URL('agency-audit.html?place=woodbury%7CMN',base).href,
   {waitUntil:'domcontentloaded',timeout:40000});
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('Audit generated'),
   null,{timeout:55000});
  const historical=page.locator('#historicalFindings');
  assert.match(await historical.textContent(),/15 → 17 \(\+2\)/);
  assert.match(await historical.textContent(),/not verified additions/);
  const citations=await historical.locator('a').evaluateAll(items=>items.map(x=>x.href));
  assert.ok(citations.some(x=>x.includes('/240350.pdf#page=2')));
  assert.ok(citations.some(x=>x.includes('/260248.pdf#page=2')));
  assert.equal(await page.locator('#reportTitle').textContent(),'Woodbury, MN');
  assert.deepEqual(problems,[],'Unexpected browser exceptions');
  console.log('AUTOMATED ACCOUNTABILITY BROWSER PASS: live agency evidence, citations, safe draft, deep link, 390px viewport');
 }catch(e){console.error('AUTOMATED ACCOUNTABILITY BROWSER FAILED:',e.stack||e,problems.slice(0,4));process.exitCode=1;}
 finally{await browser.close();}
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
