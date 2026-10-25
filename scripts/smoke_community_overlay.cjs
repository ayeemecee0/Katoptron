/* Test default-on national OSM layer is source-linked and never
 * pollutes the official camera map or simulated route evidence.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:950}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const failures=[];page.on('pageerror',e=>failures.push(e.message));
 try{
  const response=await page.goto(new URL('index.html',base).href,
    {waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(response?.status(),200);
  await page.waitForFunction(()=>document.querySelector('#nationalStats')?.textContent?.includes('verified camera points in'),null,{timeout:35000});
  assert.equal(await page.locator('#showCommunity').isChecked(),true);
  assert.equal(await page.locator('#showExact').isChecked(),true,
    'Official GIS tier must remain visible and independently selectable');
  assert.ok((await page.locator('#nationalStats').textContent()).includes('verified camera points'));
  const original=await page.locator('#nationalStats').textContent();
  // A portal record must never be considered verified camera inventory.
  const p=await page.evaluate(async()=>{
    const c=window.KATOPTRON_CONFIG;
    const r=await fetch(c.supabaseUrl+
      '/rest/v1/flock_osm_community_points?select=osm_key,latitude,longitude&order=osm_key.asc&limit=1',
      {headers:{apikey:c.supabasePublishableKey}});
    if(!r.ok)throw Error('No public ODbL source coordinate: HTTP '+r.status);
    return (await r.json())[0];
  });
  assert.ok(p&&Number.isFinite(p.latitude)&&Number.isFinite(p.longitude));
  // National community density must load on FIRST render, without any click.
  await page.waitForFunction(()=>{
    const s=document.querySelector('#communityOverlayStatus')?.textContent||'';
    return s.includes('National community-report density')||s.includes('national community density')||
      s.includes('Community density unavailable');
  },null,{timeout:30000});
  const density=await page.locator('#communityOverlayStatus').textContent();
  assert.ok(!density.includes('unavailable'),'Community density was inaccessible: '+density);
  const officialPane=page.locator('.leaflet-officialEvidencePane-pane');
  assert.equal(await officialPane.count(),1,'Government evidence must have a distinct frontmost map pane');
  const nationalDots=await page.locator('.leaflet-overlay-pane canvas, .leaflet-overlay-pane path').count();
  assert.ok(nationalDots>0,'National community density cells did not render');
  // Map search recenters both layers. Still no route plan.
  await page.locator('#mapSearch').fill(p.latitude+','+p.longitude);
  await page.locator('#mapSearchForm button').click();
  await page.waitForFunction(()=>{
    const s=document.querySelector('#communityOverlayStatus')?.textContent||'';
    return s.includes('community-reported camera observations shown')||
      s.includes('Community locations unavailable')||s.includes('More than 1,500');
  },null,{timeout:45000});
  const status=await page.locator('#communityOverlayStatus').textContent();
  assert.ok(status.includes('community-reported camera observations shown'),status);
  assert.ok(Number.parseInt(status.replaceAll(',',''),10)>0,status);
  assert.equal(await page.locator('#showCommunity').isChecked(),true);
  assert.equal(await page.locator('#routeComparisonList li').count(),0,
   'Community overlay must not simulate route detections');
  assert.equal(await page.locator('#timelineEvents li').count(),0,
   'OSM community points are not plate lookups');
  assert.equal(await page.locator('#nationalStats').textContent(),original,
   'Community overlay must not change official GIS national counts');
  await page.locator('#showExact').uncheck();
  assert.equal(await page.locator('#showCommunity').isChecked(),true,
    'Government visibility must not disable community coverage');
  await page.locator('#showExact').check();
  await page.locator('#showCommunity').uncheck();
  assert.ok((await page.locator('#communityOverlayStatus').textContent()).includes('overlay off'));
  assert.equal(await page.locator('#routeComparisonList li').count(),0);
  await page.locator('#showCommunity').check();
  assert.equal(await page.locator('#showCommunity').isChecked(),true,
    'Nationwide layer must be independently restorable');
  assert.deepEqual(failures,[]);
  console.log('NATIONAL OSM COMMUNITY OVERLAY PASS, default nationwide density, original-source points and official evidence independently selectable');
 }catch(err){
  console.error('NATIONAL OSM COMMUNITY OVERLAY FAIL:',err.stack||err);
  process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error('Overlay browser harness failed:',e.message);process.exitCode=1});
