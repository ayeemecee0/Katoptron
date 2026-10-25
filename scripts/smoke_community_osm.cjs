/* Chromium smoke for the nationwide openly licensed OSM Flock layer. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:850}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 let tileResponses=0;const failed=[];
 page.on('response',r=>{if(r.url().includes('cameras-us-hourly-filter/')&&r.status()===200)tileResponses++});
 page.on('pageerror',e=>failed.push(e.message));
 try{
  const response=await page.goto(new URL('community-map.html',base).href,
      {waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(response?.status(),200);
  await page.waitForFunction(()=>{
   const s=document.querySelector('#status')?.textContent||'';
   return s.includes('loaded')||s.includes('unavailable')||s.includes('provider issue');
  },{timeout:65000});
  const status=await page.locator('#status').textContent();
  assert.ok(status.includes('layer loaded'),'Map provider not ready: '+status+'; network: '+networkFailures.join(' | ').slice(0,850));
  const count=await page.locator('#communityCount').textContent();
  assert.ok(Number(count.replaceAll(',',''))>50000,
    'Source manifest vendor count missing, changed or unexpectedly small: '+count);
  await page.waitForTimeout(4500);
  assert.ok(tileResponses>0,'Filtered Flock community vector tiles did not successfully load');
  await page.locator('#coords').fill('38.5816,-121.4944');
  await page.locator('#jumpForm button').click();
  assert.ok((await page.locator('#status').textContent()).includes('near selected coordinates'));
  assert.deepEqual(failed,[],'Browser source map errors');
  console.log('OSM FLOCK NATIONAL MAP PASS, source-labeled cameras='+count+', tiles HTTP 200='+tileResponses);
 }catch(err){console.error('OSM FLOCK NATIONAL MAP FAILED:',err.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(err=>{console.error('OSM smoke harness failed:',err.message);process.exitCode=1});
