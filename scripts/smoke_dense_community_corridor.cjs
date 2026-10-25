/* Dense urban corridor regression: production-backed public OSM data, no writes.
 * A fixed Atlanta area is large enough to overflow the previous 1000-row
 * source request. Adaptive subdivision must finish all boxes or fail closed.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1200,height:800}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  const base=process.env.KATOPTRON_SMOKE_BASE||'http://127.0.0.1:8765/';
  const response=await page.goto(new URL('index.html',base).href,{
   waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(response?.status(),200);
  const result=await page.evaluate(async()=>{
   const c=window.KATOPTRON_CONFIG;
   const geo=window.KatoptronRouteGeometry;
   const evaluator=window.KatoptronCommunityRoute;
   if(!geo||!evaluator||!c?.supabasePublishableKey)throw Error('Evidence client unavailable');
   const route={points:[[33.75,-84.50],[34.0,-84.25]]};
   const fetchRows=async(b,signal)=>{
    const q=new URLSearchParams({
     select:'osm_key,latitude,longitude',order:'osm_key.asc',limit:'1001'
    });
    q.append('latitude','gte.'+b.south.toFixed(7));
    q.append('latitude','lte.'+b.north.toFixed(7));
    q.append('longitude','gte.'+b.west.toFixed(7));
    q.append('longitude','lte.'+b.east.toFixed(7));
    const r=await fetch(c.supabaseUrl.replace(/\\/$/,'')+
     '/rest/v1/flock_osm_community_points?'+q.toString(),{
     headers:{apikey:c.supabasePublishableKey},signal,cache:'no-store'
    });
    if(!r.ok)throw Error('Public community REST '+r.status);
    return r.json();
   };
   const initial=await fetchRows({
    south:33.747,north:34.003,west:-84.503,east:-84.247
   },new AbortController().signal);
   if(initial.length<=1000)throw Error('Urban fixture no longer exceeds legacy cutoff');
   const scan=await evaluator.scanRoute(route,geo,fetchRows,new AbortController().signal);
   const stats=evaluator.summarize(route,scan.records,[],geo,false);
   return {initial:initial.length,queries:scan.queries,records:scan.records.length,
     nearRoute:stats.communityNearRoute,uncertainOverlap:stats.possibleOverlaps};
  });
  assert.equal(result.initial,1001);
  assert.ok(result.queries>1&&result.queries<=240,
    'Dense urban area was not fully subdivided: '+JSON.stringify(result));
  assert.ok(result.records>1000,'Source inventory unexpectedly truncated');
  assert.equal(result.uncertainOverlap,null);
  assert.deepEqual(errors,[]);
  console.log('DENSE URBAN OSM ROUTE PASS: baseline page=1001 (old fail); adaptive queries='+
   result.queries+'; complete unique source records='+result.records+
   '; community proximity='+result.nearRoute+'; official overlaps remain unknown');
 }catch(e){console.error('DENSE URBAN OSM ROUTE FAILED:',e.message);process.exitCode=1}
 finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
