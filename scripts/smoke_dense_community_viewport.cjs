/* Regression for user-facing map completeness when Supabase caps REST at 1000.
 * This is read-only against real public OSM data; no routes or plate reads.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:850}});
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  const r=await page.goto(new URL('community-map.html',base).href,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(r?.status(),200);
  await page.waitForFunction(()=>window.exactSnapshot?.count>90000,null,{timeout:60000});
  await page.evaluate(()=>{
    community.fitBounds([[33.747,-84.503],[34.003,-84.247]]);
    if(community.getZoom()<10)community.setView([33.875,-84.375],10);
  });
  await page.waitForTimeout(800);
  const overview=await page.evaluate(()=>({
    zoom:community.getZoom(),
    count:exactSnapshot.count,
    canvas:document.querySelectorAll('.katoptron-osm-exact-canvas').length,
    blobs:document.querySelectorAll('.leaflet-overlay-pane .leaflet-interactive').length,
    status:document.querySelector('#status')?.textContent||''
  }));
  assert.ok(overview.zoom>=10&&overview.count>100000&&
    overview.canvas===1&&overview.blobs===0,
    'Dense metro must use original OSM dots, never invented regions: '+JSON.stringify(overview));
  // A closer view must display only a completely returned result.
  const point=await page.evaluate(async()=>{
   const cfg=window.KATOPTRON_CONFIG;
   const q=new URLSearchParams({
    select:'latitude,longitude',
    latitude:'gte.33.747',longitude:'gte.-84.503',
    order:'osm_key.asc',limit:'1'
   });
   q.append('latitude','lte.34.003');q.append('longitude','lte.-84.247');
   const r=await fetch(cfg.supabaseUrl+'/rest/v1/flock_osm_community_points?'+q.toString(),
    {headers:{apikey:cfg.supabasePublishableKey}});
   if(!r.ok)throw Error('Source sampling failed');
   const data=await r.json();
   if(!data.length)throw Error('No OSM observations inside test grid');
   return data[0];
  });
  await page.evaluate(({latitude,longitude})=>community.setView([latitude,longitude],16),point);
  await page.waitForTimeout(900);
  const exact=await page.evaluate(()=>({
    zoom:community.getZoom(),
    canvas:document.querySelectorAll('.katoptron-osm-exact-canvas').length,
    data:exactSnapshot.count,
    status:document.querySelector('#status')?.textContent||''
  }));
  assert.ok(exact.zoom>=16&&exact.canvas===1&&exact.data>100000&&
    exact.status.includes('individual community coordinates'),JSON.stringify(exact));
  console.log('COMMUNITY VIEWPORT COMPLETENESS PASS: nationally and locally visible true OSM coordinates, no approximation clusters');
 }catch(e){console.error('COMMUNITY VIEWPORT COMPLETENESS FAILED',e.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Viewport test harness failed',e.message);process.exitCode=1});
