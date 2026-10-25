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
  await page.waitForFunction(()=>document.querySelector('#communityCount')?.textContent?.includes(','),null,{timeout:30000});
  await page.evaluate(()=>community.fitBounds([[33.747,-84.503],[34.003,-84.247]]));
  await page.waitForFunction(()=>{
    const status=document.querySelector('#status')?.textContent||'';
    return status.includes('no truncated subset is shown')||status.includes('unavailable');
  },null,{timeout:35000});
  const big=await page.locator('#status').textContent();
  assert.ok(big.includes('no truncated subset is shown'),big);
  assert.ok(Number.parseInt(big.replaceAll(',',''),10)>1000,big);
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
  await page.waitForFunction(()=>{
   const status=document.querySelector('#status')?.textContent||'';
   return status.includes('complete source query')||status.includes('unavailable');
  },null,{timeout:35000});
  const small=await page.locator('#status').textContent();
  assert.ok(small.includes('complete source query')&&
    Number.parseInt(small.replaceAll(',',''),10)>=1,small);
  console.log('COMMUNITY VIEWPORT COMPLETENESS PASS: crowded 1000-row-capped metro area withheld; complete zoomed points shown');
 }catch(e){console.error('COMMUNITY VIEWPORT COMPLETENESS FAILED',e.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error('Viewport test harness failed',e.message);process.exitCode=1});
