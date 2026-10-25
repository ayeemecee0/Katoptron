/* Real-Supabase, mocked-router smoke: community evidence opt-in never
 * changes official route encounters or simulates plate reads.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:960}});
 const failures=[];page.on('pageerror',e=>failures.push(e.message));
 const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
 try{
  await page.route('**/config.js',async route=>{
    const response=await route.fetch();
    let source=await response.text();
    source=source.replace(/locationProvider:\s*'[^']+'/,"locationProvider: 'demo'")
      .replace(/geoapifyPublicKey:\s*'[^']*'/,"geoapifyPublicKey: ''");
    await route.fulfill({status:200,contentType:'application/javascript',body:source});
  });
  const r=await page.goto(new URL('index.html',base).href,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(r?.status(),200);
  await page.waitForFunction(()=>document.querySelector('#nationalStats')?.textContent?.includes('verified camera points'),null,{timeout:30000});
  assert.equal(await page.locator('#compareCommunityRoute').isChecked(),false);
  const source=await page.evaluate(async()=>{
    const c=window.KATOPTRON_CONFIG;
    const u=c.supabaseUrl+'/rest/v1/flock_osm_community_points?select=latitude,longitude&order=osm_key.asc&limit=1';
    const resp=await fetch(u,{headers:{apikey:c.supabasePublishableKey}});
    if(!resp.ok)throw Error('Public community source HTTP '+resp.status);
    const rows=await resp.json();
    if(rows.length!==1)throw Error('Missing community camera source fixture');
    return rows[0];
  });
  const lat=Number(source.latitude),lon=Number(source.longitude);
  assert.ok(Number.isFinite(lat)&&Number.isFinite(lon));
  await page.route('https://router.project-osrm.org/**',route=>
    route.fulfill({status:200,contentType:'application/json',
      headers:{'access-control-allow-origin':'*'},
      body:JSON.stringify({code:'Ok',routes:[
       {distance:1700,duration:170,
        geometry:{type:'LineString',coordinates:[[lon-.008,lat],[lon,lat],[lon+.008,lat]]}},
       {distance:2800,duration:250,
        geometry:{type:'LineString',coordinates:[[lon-.008,lat],[lon,lat+.015],[lon+.008,lat]]}}
      ]})}));
  await page.locator('#from').fill(lat+','+(lon-.008));
  await page.locator('#to').fill(lat+','+(lon+.008));
  await page.locator('#planRoute').click();
  await page.waitForFunction(()=>document.querySelector('#comparisonStatus')?.textContent?.includes('2/2 driving routes completely checked'),null,{timeout:40000});
  const before=await page.locator('#nearbyCount').textContent();
  const original=await page.locator('#observationCount').textContent();
  const stats=await page.locator('#nationalStats').textContent();
  await page.locator('#compareCommunityRoute').check();
  await page.waitForFunction(()=>{
    const value=document.querySelector('#communityRouteStatus')?.textContent||'';
    return value.startsWith('Selected route:')||value.startsWith('Community route evidence UNKNOWN:');
  },null,{timeout:45000});
  const value=await page.locator('#communityRouteStatus').textContent();
  assert.ok(value.startsWith('Selected route:'),'Community corridor query failed: '+value);
  assert.ok(/Selected route: [1-9][0-9]* OSM community observations/.test(value),value);
  assert.ok(value.includes('not detected vehicles or active-device counts'));
  await page.waitForFunction(()=>{
   const entries=[...document.querySelectorAll('.community-comparison-evidence')];
   return entries.length===2&&entries.every(e=>e.textContent.includes('community-mapped OSM observation(s)'));
  },null,{timeout:45000});
  const alternatives=await page.locator('.community-comparison-evidence').allTextContents();
  assert.equal(alternatives.length,2);
  assert.ok(alternatives.every(x=>!x.includes('UNKNOWN')),alternatives.join(' | '));
  await page.locator('#routeChoice').selectOption('1');
  await page.waitForFunction(()=>document.querySelector('#communityRouteStatus')?.textContent?.startsWith('Selected route:'),null,{timeout:10000});
  const secondSelected=await page.locator('#communityRouteStatus').textContent();
  assert.ok(secondSelected.includes('OSM community observations within'),secondSelected);
  await page.locator('#routeChoice').selectOption('0');
  await page.waitForFunction(()=>document.querySelector('#communityRouteStatus')?.textContent?.startsWith('Selected route:'),null,{timeout:10000});
  assert.equal((await page.locator('#communityRouteStatus').textContent()).includes('UNKNOWN'),false);

  assert.equal(await page.locator('#nearbyCount').textContent(),before);
  assert.equal(await page.locator('#observationCount').textContent(),original);
  assert.equal(await page.locator('#nationalStats').textContent(),stats);
  await page.locator('#compareCommunityRoute').uncheck();
  assert.ok((await page.locator('#communityRouteStatus').textContent()).includes('Off by default'));
  assert.deepEqual(failures,[]);
  console.log('COMMUNITY ROUTE EVIDENCE PASS: independent OSM route count, official simulation unchanged');
 }catch(error){console.error('COMMUNITY ROUTE EVIDENCE FAILED',error.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
