/* M4 browser acceptance: route evidence is either fully counted or UNKNOWN.
 * Synthetic responses are intercepted, not published GIS/camera facts.
 * No real Geoapify traffic and no personal address collection.
 */
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1220,height:820}});
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const from=[38.5816,-121.4944],to=[38.6779,-121.1761];
 const camera={
  id:'00000000-0000-4000-8000-000000000001',
  record_key:'synthetic-test-camera',
  label:'INTERNAL FIXTURE · NOT A REAL CAMERA',
  jurisdiction_label:'Fixture, CA',latitude:38.6261,longitude:-121.38,
  location_accuracy:'exact',uncertainty_radius_m:0,
  source_type:'official_government',
  source_url:'https://testing.gov/fixture-gis',
  evidence_summary:'Browser-only synthetic test; no camera location established',
  source_flock_label_status:'source_flock_identified',
  last_confirmed_on:'2026-10-26',
  last_source_recheck_at:'2026-10-26T17:00:00Z',
  published_at:'2026-10-26T17:00:00Z',
  verification_method:'official_georeferenced_camera_record_v1'
 };
 let routeQueries=0,splits=0,mode='dense',malformed=0;
 try{
  await page.route('**/config.js',async route=>{
   const response=await route.fetch();let s=await response.text();
   s=s.replace(/locationProvider:\s*'[^']+'/,"locationProvider: 'demo'")
     .replace(/geoapifyPublicKey:\s*'[^']*'/,"geoapifyPublicKey: ''");
   await route.fulfill({status:200,contentType:'application/javascript',body:s});
  });
  await page.route('https://router.project-osrm.org/**',async route=>{
   await route.fulfill({status:200,contentType:'application/json',
    headers:{'access-control-allow-origin':'*'},body:JSON.stringify({
     code:'Ok',routes:[{distance:33000,duration:2100,
      geometry:{type:'LineString',coordinates:[
       [from[1],from[0]],[-121.37,38.63],[to[1],to[0]]]}}]})});
  });
  for(const table of ['flock_camera_locations','flock_public_tiered_camera_points']){
   await page.route('**/rest/v1/'+table+'?**',async route=>{
    const req=route.request();const header=req.headers()['prefer']||'';
    if(!header.includes('count=exact')){await route.continue();return;}
    routeQueries++;
    const parsed=new URL(req.url());
    const north=Number(parsed.searchParams.getAll('latitude').find(v=>v.startsWith('lte.'))?.slice(4));
    const south=Number(parsed.searchParams.getAll('latitude').find(v=>v.startsWith('gte.'))?.slice(4));
    const east=Number(parsed.searchParams.getAll('longitude').find(v=>v.startsWith('lte.'))?.slice(4));
    const west=Number(parsed.searchParams.getAll('longitude').find(v=>v.startsWith('gte.'))?.slice(4));
    assert.ok(Number.isFinite(east)&&Number.isFinite(west)&&Number.isFinite(south)&&Number.isFinite(north));
    if(mode==='bad-header'){
     malformed++;
     await route.fulfill({status:200,contentType:'application/json',
      headers:{'access-control-allow-origin':'*','access-control-expose-headers':'content-range'},
      body:'[]'});
     return;
    }
    if(table==='flock_camera_locations'&&east-west>0.06){
     splits++;
     await route.fulfill({status:200,contentType:'application/json',
      headers:{'content-range':'0-999/1201','access-control-allow-origin':'*',
       'access-control-expose-headers':'content-range'},
      body:JSON.stringify(Array.from({length:1000},(_,i)=>({
       ...camera,record_key:'synthetic-untrusted-page-'+i
      })))});
     return;
    }
    const onBox=table==='flock_camera_locations'&&
      camera.latitude>=south&&camera.latitude<=north&&
      camera.longitude>=west&&camera.longitude<=east;
    const rows=onBox?[camera]:[];
    await route.fulfill({status:200,contentType:'application/json',
     headers:{'content-range':rows.length?'0-0/1':'*/0',
      'access-control-allow-origin':'*','access-control-expose-headers':'content-range'},
     body:JSON.stringify(rows)});
   });
  }
  const url=process.env.KATOPTRON_SMOKE_BASE||'https://ayeemecee0.github.io/Katoptron/';
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
  await page.locator('#from').fill(from.join(','));
  await page.locator('#to').fill(to.join(','));
  await page.locator('#planRoute').click();
  await page.waitForFunction(()=>document.querySelector('#routeStatus')?.textContent?.startsWith('Checked '),
    null,{timeout:45000});
  assert.ok(splits>0,'No backend 1000-row truncation challenged');
  assert.ok(routeQueries>2,'Dense route must subdivide into smaller queries');
  assert.equal((await page.locator('#nearbyCount').textContent()).trim(),'1');
  assert.ok((await page.locator('#routeStatus').textContent()).includes('subdivision(s)'));
  assert.equal(await page.locator('#play').isDisabled(),false);

  mode='bad-header';
  await page.locator('#planRoute').click();
  await page.waitForFunction(()=>document.querySelector('#routeStatus')?.textContent?.includes('Evidence unavailable'),
    null,{timeout:45000});
  assert.ok(malformed>0);
  assert.equal((await page.locator('#nearbyCount').textContent()).trim(),'Unknown');
  assert.equal(await page.locator('#play').isDisabled(),true);
  assert.ok((await page.locator('#comparisonStatus').textContent()).includes('unavailable'));
  assert.ok(!errors.length,errors.join('; '));
  console.log('M4 BROWSER PASS: truncation subdivided; broken exact-count proof UNKNOWN, replay disabled');
 }catch(error){
  console.error('M4 BROWSER FAILED',error.stack||error);
  process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
