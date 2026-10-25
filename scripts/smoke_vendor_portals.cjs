/* Live/static Playwright smoke for first-party vendor disclosure snapshots.
 * This test reads public data only, never harvests Flock or writes records.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');

(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:880}});
 const errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'https://ayeemecee0.github.io/Katoptron/';
 try{
  const url=new URL('portals.html',base);
  const r=await page.goto(url.href,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(r?.status(),200,'Original vendor directory page not served');
  await page.waitForFunction(()=>document.querySelector('#snapshotCount')?.textContent==='13',{timeout:30000});
  assert.equal((await page.locator('#agencyCount').textContent()).trim(),'13');
  assert.equal(await page.locator('#results .card').count(),13);
  await page.locator('#search').fill('Menifee');
  assert.equal(await page.locator('#results .card').count(),1);
  const menifee=await page.locator('#results .card').innerText();
  assert.ok(menifee.includes('44'),'Menifee vendor-reported mixed camera count absent');
  assert.ok(menifee.includes('2026-07-09'),'Historical evidence source date absent');
  const href=await page.locator('#results .card a').getAttribute('href');
  assert.equal(href,'https://transparency.flocksafety.com/menifee-ca-pd');
  await page.locator('#search').fill('Folsom');
  assert.equal(await page.locator('#results .card').count(),1);
  assert.ok((await page.locator('#results .card').innerText()).includes('Not reported'),
    'Missing camera count was fabricated as zero');
  await page.locator('#search').fill('College Place');
  assert.equal(await page.locator('#results .card').count(),1);
  assert.ok((await page.locator('#results .card').innerText()).includes('8'));
  await page.locator('#search').fill('');
  const links=await page.locator('#results .card a').evaluateAll(nodes=>
    nodes.map(a=>new URL(a.href).hostname));
  assert.ok(links.length===13&&links.every(h=>h==='transparency.flocksafety.com'));
  assert.ok((await page.locator('.explain').innerText()).includes('not a count of verified individual ALPR map pins'));
  assert.deepEqual(errors,[],'Source listing has browser JavaScript errors');
  console.log('VENDOR PORTAL BROWSER PASS: 13 dated direct-source agency records / 5 states; no GIS camera mixing');
 }catch(e){
  console.error('VENDOR PORTAL BROWSER FAILED',e.message);
  process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error('Vendor portal browser harness failed:',e.message);process.exitCode=1});
