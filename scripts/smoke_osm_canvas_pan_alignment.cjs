/* Real Chromium pixel-level regression for source-backed community dots.
 * A Leaflet map pane can have a nonzero translation after repeated pans;
 * the OSM canvas must continue painting at the actual map projection, not
 * at its stale layer-coordinate pixel positions.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1280,height:850}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  const r=await page.goto(new URL('community-map.html',base).href,
   {waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(r?.status(),200);
  await page.waitForFunction(()=>typeof exactSnapshot!=='undefined'&&
    exactSnapshot?.count>90000&&
    document.querySelector('.katoptron-osm-exact-canvas'),null,{timeout:60000});
  // Pick a real OSM observation in Sacramento; its original coordinate
  // must remain painted in-place even after many pans.
  const record=await page.evaluate(async()=>{
   const c=window.KATOPTRON_CONFIG;
   const q=new URLSearchParams({
    select:'osm_key,latitude,longitude',
    latitude:'gte.38.4',longitude:'gte.-121.7',
    order:'osm_key.asc',limit:'1'});
   q.append('latitude','lte.38.7');
   q.append('longitude','lte.-121.2');
   const r=await fetch(c.supabaseUrl+
      '/rest/v1/flock_osm_community_points?'+q.toString(),
       {headers:{apikey:c.supabasePublishableKey},cache:'no-store'});
   if(r.status!==200)throw Error('Original community source HTTP '+r.status);
   const rows=await r.json();
   if(rows.length!==1)throw Error('No real Sacramento original OSM source for pixel test');
   return rows[0];
  });
  const sample=await page.evaluate(async record=>{
   const point=[record.latitude,record.longitude];
   function snapshot(){
    const map=community;
    const canvas=document.querySelector('.katoptron-osm-exact-canvas');
    const geo=map.latLngToContainerPoint(point);
    const ratio=canvas.width/map.getSize().x;
    const x=Math.round(geo.x*ratio),y=Math.round(geo.y*ratio);
    const inside=x>=4&&y>=4&&x<canvas.width-4&&y<canvas.height-4;
    let alpha=0;
    if(inside){
     const pixels=canvas.getContext('2d').getImageData(x-3,y-3,7,7).data;
     for(let i=3;i<pixels.length;i+=4)alpha=Math.max(alpha,pixels[i]);
    }
    const layerOffset=map.containerPointToLayerPoint([0,0]);
    const canvasOffset=L.DomUtil.getPosition(canvas);
    return {alpha,inside,point:[geo.x,geo.y],pan:[layerOffset.x,layerOffset.y],
      canvasOffset:[canvasOffset.x,canvasOffset.y]};
   }
   community.setView(point,12,{animate:false});
   let initial=snapshot();
   community.panBy([170,-120],{animate:false});
   let after=snapshot();
   community.panBy([-70,90],{animate:false});
   let again=snapshot();
   // Real pan positions must diverge from the original layer origin.
   return {initial,after,again};
  },record);
  for(const stage of ['initial','after','again']){
   assert.ok(sample[stage].inside,
      stage+' OSM camera point is outside viewport: '+JSON.stringify(sample[stage]));
   assert.ok(sample[stage].alpha>0,
      stage+' community dots drifted off original map/source coordinate: '+
        JSON.stringify(sample));
   assert.ok(Math.abs(sample[stage].canvasOffset[0]-sample[stage].pan[0])<2&&
      Math.abs(sample[stage].canvasOffset[1]-sample[stage].pan[1])<2,
      stage+' canvas no longer pinned to viewport: '+JSON.stringify(sample));
  }
  assert.ok(Math.hypot(...sample.after.pan)>40,
   'Test did not trigger the nonzero mapPane offset regression');
  assert.ok(Math.hypot(sample.initial.point[0]-sample.after.point[0],
   sample.initial.point[1]-sample.after.point[1])>50,
   'Projected point must move with map tiles when map is panned');
  // Original-source popup must agree with the now-corrected painted dot.
  await page.evaluate(record=>{
   const p=community.latLngToContainerPoint([record.latitude,record.longitude]);
   community.fire('click',{containerPoint:p});
  },record);
  await page.waitForFunction(()=>document.querySelector('.leaflet-popup-content a')
   ?.getAttribute('href')?.startsWith('https://www.openstreetmap.org/'),
     null,{timeout:22000});
  const url=await page.locator('.leaflet-popup-content a').getAttribute('href');
  assert.equal(url,'https://www.openstreetmap.org/'+record.osm_key);
  assert.deepEqual(errors,[],'Browser script errors during OSM map pan');
  console.log('COMMUNITY CANVAS PAN ALIGNMENT PASS: source dot stays on true map coordinate after two nonzero pane translations and remains clickable');
 }catch(e){console.error('COMMUNITY CANVAS PAN ALIGNMENT FAILED:',e.stack||e.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('OSM pan-alignment browser harness failed:',e.message);process.exitCode=1});
