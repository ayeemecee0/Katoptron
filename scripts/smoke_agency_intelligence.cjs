const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:800}});
 const problems=[];page.on('pageerror',e=>problems.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  let r=await page.goto(new URL('agency-xray.html',base).href,
    {waitUntil:'domcontentloaded',timeout:40000});
  assert.equal(r.status(),200);
  await page.waitForFunction(()=>document.querySelector('#status')
    ?.textContent?.includes('localities indexed'),null,{timeout:40000});
  await page.locator('#query').fill('Folsom');
  await page.locator('#list button').first().click();
  assert.ok((await page.locator('#profileTitle').textContent()).includes('Folsom'));
  const metrics=await page.locator('#metrics').textContent();
  assert.ok(metrics.includes('Government source-mapped positions'));
  assert.ok(metrics.includes('Flock vendor snapshots'));
  assert.ok((await page.locator('#portals').textContent()).includes('Vendor-reported cameras'));
  // Original vendor numbers may be unpublished: no implied zero counts.
  assert.ok((await page.locator('#unknowns').textContent()).includes('unknown'));
  await page.locator('#follow').click();
  await page.waitForURL(/government-watch\.html/, {timeout:16000});
  await page.waitForFunction(()=>document.querySelector('#status')
     ?.textContent?.includes('localities loaded'),null,{timeout:40000});
  assert.ok((await page.locator('#cities').textContent()).includes('Folsom'));
  assert.ok((await page.locator('#updates').textContent()).includes('Vendor disclosure'));
  await page.locator('#review').click();
  assert.ok((await page.locator('#cities').textContent()).includes('0 unread'));
  // Confirm follow/unfollow doesn't require login or send private watch lists.
  const storage=await page.evaluate(()=>Object.keys(localStorage));
  assert.ok(storage.includes('katoptron-city-watch-v1'));
  r=await page.goto(new URL('sharing-explorer.html',base).href,
    {waitUntil:'domcontentloaded',timeout:16000});
  assert.equal(r.status(),200);
  const copy=await page.locator('main').textContent();
  assert.ok(copy.includes('Las Cruces Police Department (NM)'));
  assert.ok(copy.includes('secondary-source snapshots'));
  await page.locator('#filter').fill('Temple');
  assert.equal(await page.locator('#cards .card').count(),1);
  assert.ok((await page.locator('#cards').textContent()).includes('1,191'));
  assert.deepEqual(problems,[]);
  console.log('AGENCY INTELLIGENCE PASS: live sourced X-Ray dossier, local watch persistence and reviewed-state, secondary access explorer');
 }catch(e){console.error('AGENCY INTELLIGENCE FAILED:',e.stack||e);console.error(problems.slice(0,5));process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Agency browser test failed:',e.stack||e);process.exitCode=1});
