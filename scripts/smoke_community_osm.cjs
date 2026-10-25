/* Live Chromium smoke for the nationwide community Flock dataset in Supabase. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');

(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:850}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 try{
  const response=await page.goto(new URL('community-map.html',base).href,
    {waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(response?.status(),200);
  await page.waitForFunction(()=>{
    const text=document.querySelector('#communityCount')?.textContent||'';
    return Number(text.replaceAll(',',''))>=1000;
  },null,{timeout:45000});
  const count=await page.locator('#communityCount').textContent();
  assert.ok(Number(count.replaceAll(',',''))>=1000,'Not enough independently labeled community observations');
  assert.ok((await page.locator('#status').textContent()).includes('density cells'));
  assert.ok((await page.locator('#sourceDate').textContent()).includes('snapshot'));
  await page.waitForFunction(()=>{const value=document.querySelector('#crossSourceStatus')?.textContent||'';return value.includes('assessed')||value.includes('unavailable');},null,{timeout:22000});
  const matchStatus=await page.locator('#crossSourceStatus').textContent();
  assert.ok(matchStatus.includes('government-source records assessed')&&matchStatus.includes('not confirmed identical cameras'),matchStatus);
  const density=await page.evaluate(async()=>{
    const c=window.KATOPTRON_CONFIG;
    const url=c.supabaseUrl+'/rest/v1/flock_public_osm_community_density?select=community_report_count&limit=1';
    const r=await fetch(url,{headers:{apikey:c.supabasePublishableKey},cache:'no-store'});
    if(!r.ok)throw Error('National coarse community density unavailable HTTP '+r.status);
    return r.json();
  });
  assert.ok(Array.isArray(density)&&density.length===1&&density[0].community_report_count>0);

  // Retrieve ONE already-published community-source coordinate to prove the
  // viewport-scoped map can display an actual database-backed camera record.
  const record=await page.evaluate(async()=>{
    const c=window.KATOPTRON_CONFIG;
    const url=c.supabaseUrl+'/rest/v1/flock_osm_community_points?select=osm_key,latitude,longitude&order=osm_key.asc&limit=1';
    const r=await fetch(url,{headers:{apikey:c.supabasePublishableKey},cache:'no-store'});
    if(!r.ok)throw Error('Published community point API HTTP '+r.status);
    const rows=await r.json();
    if(!Array.isArray(rows)||rows.length!==1)throw Error('No community source point found');
    return rows[0];
  });
  await page.locator('#coordinates').fill(record.latitude+','+record.longitude);
  await page.locator('#jumpForm button').click();
  await page.waitForFunction(()=>{
    const s=document.querySelector('#status')?.textContent||'';
    return s.includes('community Flock locations shown')||s.includes('More than 1,500')||s.includes('unavailable');
  },null,{timeout:40000});
  let status=await page.locator('#status').textContent();
  assert.ok(status.includes('community Flock locations shown'),'Map source retrieval did not succeed: '+status);
  assert.ok(Number.parseInt(status.replaceAll(',',''),10)>=1,'No real camera positions returned within source viewport: '+status);
  assert.deepEqual(errors,[],'Browser JavaScript errors');
  console.log('NATIONAL COMMUNITY FLOCK MAP PASS: '+count+' public ODbL points indexed; GIS and community separate');
 }catch(e){console.error('NATIONAL COMMUNITY FLOCK MAP FAILED:',e.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Nationwide community browser harness failed:',e.message);process.exitCode=1});
