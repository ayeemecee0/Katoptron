const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1200,height:800}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  let r=await page.goto(new URL('agency-xray.html?place=folsom%7CCA',base).href,
    {waitUntil:'domcontentloaded',timeout:40000});
  assert.equal(r?.status(),200);
  await page.waitForFunction(()=>document.querySelector('#profileTitle')?.textContent?.includes('Folsom'),
     null,{timeout:45000});
  const href=await page.locator('#timelineLink').getAttribute('href');
  assert.ok(href?.includes('agency-timeline.html?place='));
  r=await page.goto(new URL(href,base).href,{waitUntil:'domcontentloaded',timeout:40000});
  assert.equal(r?.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')
    ?.textContent?.includes('dated records displayed'),null,{timeout:45000});
  assert.ok((await page.locator('#title').textContent()).includes('Folsom'));
  assert.ok((await page.locator('#timeline').textContent()).includes('source'));
  await page.locator('#kind').selectOption('vendor_snapshot');
  assert.ok((await page.locator('#timeline .event').count())>=1,
    'Folsom originally disclosed source-dated Flock portal snapshot');
  assert.ok((await page.locator('#timeline').textContent()).includes('Vendor statements do not authenticate'));
  await page.locator('#kind').selectOption('scheduled_contract_end');
  assert.ok((await page.locator('#timeline').textContent()).includes('That does not mean no event occurred.'),
    'Absence of signed contract must not imply a known renewal/termination');
  r=await page.goto(new URL('agency-timeline.html?place=palo%20alto%7CCA',base).href,
    {waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('dated records displayed'),
    null,{timeout:45000});
  const palo=await page.locator('#timeline').textContent();
  assert.ok(palo.includes('2023-04-03')&&palo.includes('Palo Alto council voted'),
   'Original 2023 recorded council decision must be dated, not an inferred installation');
  assert.ok(palo.includes('2026-04-21')&&palo.includes('partially redacted'),
   'Original source-date search log publication missing');
  const undated=await page.locator('#undated').textContent();
  assert.ok(undated.includes('three-year Flock cost estimate')&&undated.includes('165,900'),
   'Original undated government estimate must be shown separately from signed expenditure');
  r=await page.goto(new URL('agency-timeline.html?place=mill%20valley%7CCA',base).href,
    {waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>document.querySelector('#status')?.textContent?.includes('dated records displayed'),
    null,{timeout:45000});
  assert.ok((await page.locator('#timeline').textContent()).includes('2026-09-09'));
  assert.ok((await page.locator('#timeline').textContent()).includes('reported disabling'));
  r=await page.goto(new URL('original-acquisition.html',base).href,
    {waitUntil:'domcontentloaded',timeout:25000});
  assert.equal(r?.status(),200);
  await page.waitForFunction(()=>{
    const s=document.querySelector('#status')?.textContent||'';
    return s.includes('Latest successful acquisition accounting')||
     s.includes('No completed original-source acquisition scan published yet');
  },null,{timeout:40000});
  const counts=await page.locator('#stats').textContent();
  if(counts)assert.ok(counts.includes('Document link leads for review'));
  assert.ok((await page.locator('main').textContent()).includes('not proof that a contract was executed'));
  r=await page.goto(new URL('agency-timeline.html?place=nonexistent%7CZZ',base).href,
    {waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>document.querySelector('#status')
   ?.textContent?.includes('No source-backed agency dossier'),null,{timeout:45000});
  assert.equal(await page.locator('#timeline .event').count(),0);
  assert.deepEqual(errors,[]);
  console.log('AGENCY TIMELINE + ACQUISITION SCORECARD PASS: real source dates, Flock snapshots, signed-contract unknowns, aggregate metrics and no invented localities');
 }catch(e){console.error('AGENCY TIMELINE + SOURCE ACQUISITION FAILED:',e.stack||e);console.error(errors);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Timeline browser test failed:',e);process.exitCode=1});
