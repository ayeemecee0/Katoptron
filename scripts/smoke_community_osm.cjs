/* Live Chromium smoke for the nationwide community Flock dataset in Supabase. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');

(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:850}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('framenavigated',frame=>{
   if(frame===page.mainFrame())console.log('COMMUNITY SMOKE NAVIGATED',frame.url());
 });
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
  await page.waitForFunction(()=>typeof exactSnapshot!=='undefined'&&exactSnapshot?.count>90000&&
    document.querySelector('.katoptron-osm-exact-canvas'),null,{timeout:60000});
  const canvasInfo=await page.evaluate(()=>({
    count:exactSnapshot.count,
    zoom:community.getZoom(),
    canvas:document.querySelectorAll('.katoptron-osm-exact-canvas').length,
    hasBlobs:document.querySelectorAll('.leaflet-overlay-pane .leaflet-interactive').length
  }));
  assert.equal(canvasInfo.zoom,4,'Original OSM coordinates must render nationally');
  assert.equal(canvasInfo.canvas,1,'Missing single national community canvas');
  assert.equal(canvasInfo.hasBlobs,0,'No approximate national reporting circles allowed');
  assert.ok((await page.locator('#status').textContent()).includes('individual small points'));
  assert.ok((await page.locator('#sourceDate').textContent()).includes('snapshot'));
  await page.waitForFunction(()=>Number((document.querySelector('#uniqueCoordinateCount')?.textContent||'').replaceAll(',',''))>100000,null,{timeout:22000});
  const observed=Number(count.replaceAll(',',''));
  const unique=Number((await page.locator('#uniqueCoordinateCount').textContent()).replaceAll(',',''));
  const extras=Number((await page.locator('#colocatedExtraCount').textContent()).replaceAll(',',''));
  const old=Number((await page.locator('#oldSourceEditCount').textContent()).replaceAll(',',''));
  assert.equal(unique+extras,observed,'Snapshot must reconcile to complete OSM inventory');
  assert.ok(extras>0&&old>1000,'Source co-location and OSM history measurements absent');
  assert.ok((await page.locator('#qualityStatus').textContent()).includes('do not prove a camera is inactive or duplicated'));

  await page.waitForFunction(()=>{const value=document.querySelector('#crossSourceStatus')?.textContent||'';return value.includes('assessed')||value.includes('unavailable');},null,{timeout:22000});
  const matchStatus=await page.locator('#crossSourceStatus').textContent();
  assert.ok(matchStatus.includes('government-source records assessed')&&matchStatus.includes('not confirmed identical cameras'),matchStatus);
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
  await page.waitForFunction(()=>community.getZoom()===13,null,{timeout:20000});
  assert.equal(await page.locator('.katoptron-osm-exact-canvas').count(),1,
    'Original OSM dots must remain drawn at street-level zoom');
  // Click the original data dot using the map's geographic projection;
  // the popup must link to its traceable public OpenStreetMap record.
  await page.evaluate(row=>{
    const pixel=community.latLngToContainerPoint([row.latitude,row.longitude]);
    community.fire('click',{containerPoint:pixel});
  },record);
  await page.waitForFunction(()=>document.querySelector('.leaflet-popup-content')?.textContent
    ?.includes('Inspect original OSM record'),null,{timeout:22000});
  const link=await page.locator('.leaflet-popup-content a').getAttribute('href');
  assert.ok(link?.includes(record.osm_key),'Original OSM source identity lost');
  assert.deepEqual(errors,[],'Browser JavaScript errors');
  console.log('NATIONAL COMMUNITY FLOCK MAP PASS: '+count+' public ODbL points indexed; GIS and community separate');
 }catch(e){console.error('NATIONAL COMMUNITY FLOCK MAP FAILED:',e.stack||e.message);console.error('PAGE ERRORS',errors.slice(0,5));process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Nationwide community browser harness failed:',e.message);process.exitCode=1});
