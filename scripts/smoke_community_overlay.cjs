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
  // Exact OSM coordinate canvas must load on FIRST render, without any click.
  await page.waitForFunction(()=>{
    const s=document.querySelector('#communityOverlayStatus')?.textContent||'';
    const normalized=s.toLowerCase();
    return normalized.includes('original osm report coordinates')||normalized.includes('original-coordinate layer unavailable');
  },null,{timeout:30000});
  const dotsStatus=await page.locator('#communityOverlayStatus').textContent();
  assert.ok(!dotsStatus.includes('unavailable'),'Original OSM position canvas unavailable: '+dotsStatus);
  const higherOfficialPane=await page.locator('.leaflet-pane').evaluateAll(
    panes=>panes.some(p=>p.style.zIndex==='460'&&p.classList.length>1));
  assert.equal(higherOfficialPane,true,
    'Government GIS points require a separate higher-stacking map pane');
  const nationalDots=await page.locator('.leaflet-overlay-pane canvas, .leaflet-overlay-pane path').count();
  assert.ok(nationalDots>0,'National OSM exact-coordinate dots did not render');
  assert.equal(await page.locator('.katoptron-osm-exact-canvas').count(),1,
   'Community all-zoom canvas missing');
  // Map search recenters both layers. Still no route plan.
  await page.locator('#mapSearch').fill(p.latitude+','+p.longitude);
  await page.locator('#mapSearchForm button').click();
  await page.waitForFunction(()=>{
    const s=document.querySelector('#communityOverlayStatus')?.textContent||'';
    return s.includes('original OSM report coordinates')||
      s.includes('original-coordinate layer unavailable');
  },null,{timeout:45000});
  const status=await page.locator('#communityOverlayStatus').textContent();
  assert.ok(status.includes('original OSM report coordinates'),status);
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
  console.log('NATIONAL OSM COMMUNITY OVERLAY PASS, original exact OSM dots at every zoom, official pins and route evidence separate');
 }catch(err){
  console.error('NATIONAL OSM COMMUNITY OVERLAY FAIL:',err.stack||err);
  process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error('Overlay browser harness failed:',e.message);process.exitCode=1});
