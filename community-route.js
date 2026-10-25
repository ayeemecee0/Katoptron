/* Source-separated, bounded, opt-in OSM route comparison.
 * No ALPR reads, exposure probabilities, official evidence promotion or
 * simulated encounters are created from community points.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronCommunityRoute=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const RADIUS_M=120,OVERLAP_M=30;
 const PAGE_LIMIT=1000,MAX_QUERIES=240,MAX_RECORDS=40000;
 const MIN_SPLIT_SPAN=0.00015,MAX_ALTERNATIVES=5;
 const SOURCE_TABLE='flock_osm_community_points';
 function summarize(route,osm,official,geo,officialComplete){
  if(!route||!Array.isArray(route.points)||!Array.isArray(osm)||
    !geo||typeof geo.closestOnRoute!=='function'||typeof geo.haversine!=='function')
   throw Error('Cannot summarize incomplete community route data');
  const ids=new Set(),candidates=[];
  for(const r of osm){
   if(!r||typeof r.osm_key!=='string'||
     !/^(node|way)\/[1-9][0-9]{0,17}$/.test(r.osm_key)||
     !Number.isFinite(Number(r.latitude))||!Number.isFinite(Number(r.longitude)))
    throw Error('Malformed community camera source');
   if(ids.has(r.osm_key))continue;
   ids.add(r.osm_key);
   const p=[Number(r.latitude),Number(r.longitude)];
   if(geo.closestOnRoute(p,route.points).distance<=RADIUS_M)candidates.push(p);
  }
  let possibleOverlaps=null;
  if(officialComplete&&Array.isArray(official)){
   const exact=official.filter(p=>p&&p.location_accuracy==='exact'&&
     p.evidence_tier!=='independently_corroborated'&&
     Number.isFinite(Number(p.latitude))&&Number.isFinite(Number(p.longitude)));
   possibleOverlaps=candidates.filter(p=>exact.some(o=>
     geo.haversine(p,[Number(o.latitude),Number(o.longitude)])<=OVERLAP_M)).length;
  }
  const uniqueMappedCoordinates=new Set(candidates.map(p=>p[0].toFixed(7)+','+p[1].toFixed(7))).size;
  return {communityNearRoute:candidates.length,uniqueMappedCoordinates,
    colocatedExtraObservations:candidates.length-uniqueMappedCoordinates,
    possibleOverlaps,proximityMeters:RADIUS_M,overlapMeters:OVERLAP_M};
 }
 function splitBox(box){
  const latitudeSpan=box.north-box.south;
  const longitudeSpan=box.east-box.west;
  if(latitudeSpan<=MIN_SPLIT_SPAN&&longitudeSpan<=MIN_SPLIT_SPAN)
   throw Error('Community observations too dense for complete bounded search');
  // Longitude is scaled to a comparable physical distance at mid-latitude.
  const adjustedLon=longitudeSpan*Math.cos((box.south+box.north)*Math.PI/360);
  if(latitudeSpan>=adjustedLon&&latitudeSpan>MIN_SPLIT_SPAN){
   const mid=(box.north+box.south)/2;
   return [{...box,north:mid},{...box,south:mid}];
  }
  if(longitudeSpan<=MIN_SPLIT_SPAN)
   throw Error('Community observations too dense for complete bounded search');
  const mid=(box.west+box.east)/2;
  return [{...box,east:mid},{...box,west:mid}];
 }
 function format(result,officialStatus){
  if(!result)return 'Checking community source evidence…';
  if(result.status==='unavailable')
   return 'COMMUNITY UNKNOWN · corridor could not be completely checked. Missing evidence is not zero.';
  if(result.status==='checking')return 'Checking independent OSM community locations…';
  const n=result.summary.communityNearRoute;
  const overlap=officialStatus?.status==='complete'
   ?result.summary.possibleOverlaps+' possible overlaps with government-source locations (30m); not confirmed same cameras'
   :'possible government-source overlaps unknown';
  return n+' community-mapped OSM observation(s) within 120m · '+
   result.summary.uniqueMappedCoordinates+' mapped coordinate position(s) ('+
   result.summary.colocatedExtraObservations+' co-located extra observation(s)) · '+overlap+
   '. Neither count estimates actual detections.';
 }
 // All bounding subdivisions must complete. PostgREST can cap responses at
 // 1000 without warning; exact Content-Range totals detect truncated rows.
 async function scanRoute(route,geo,fetchRows,signal){
  if(!route||!Array.isArray(route.points)||!geo?.corridorBoxes)
   throw Error('Route geometry unavailable');
  const queue=geo.corridorBoxes(route.points,{
   span:1.5,pad:0.003,maxBoxes:64
  });
  const collected=new Map();
  let calls=0;
  while(queue.length){
   if(signal?.aborted)throw Error('Community evidence request cancelled');
   if(calls>=MAX_QUERIES)
    throw Error('Community corridor exceeds safe query budget');
   const box=queue.shift();
   const page=await fetchRows(box,signal);
   calls++;
   if(!page||!Array.isArray(page.rows)||page.rows.length>PAGE_LIMIT||
      !Number.isSafeInteger(page.total)||page.total<page.rows.length)
    throw Error('Community source exact-count proof missing or invalid');
   if(page.total>page.rows.length){
    // Divide the entire region; do NOT discard or count the truncated page.
    queue.unshift(...splitBox(box));
    if(queue.length>MAX_QUERIES)
     throw Error('Community corridor subdivision budget exceeded');
    continue;
   }
   for(const row of page.rows){
    if(!row||typeof row.osm_key!=='string'||!Number.isFinite(Number(row.latitude))||
      !Number.isFinite(Number(row.longitude)))throw Error('Malformed community source record');
    const old=collected.get(row.osm_key);
    if(old&&(Number(old.latitude)!==Number(row.latitude)||
      Number(old.longitude)!==Number(row.longitude)))
     throw Error('Conflicting OSM source ID during corridor scan');
    collected.set(row.osm_key,row);
   }
   if(collected.size>MAX_RECORDS)
    throw Error('Community corridor exceeds safe observation budget');
  }
  return {records:[...collected.values()],queries:calls};
 }
 function install({cfg,geo,showStatus}){
  const toggle=document.getElementById('compareCommunityRoute');
  const status=document.getElementById('communityRouteStatus');
  if(!toggle||!status)return null;
  let generation=0,controller=null,selected=null;
  let routes=[],results=new Map(),officialEvidence=[],activeTasks=null;
  const notify=()=>{if(typeof showStatus==='function')showStatus()};
  function say(s){status.textContent=s}
  function cancel(){
   generation++;controller?.abort();controller=null;
   activeTasks=null;routes=[];results=new Map();officialEvidence=[];selected=null;
   say(toggle.checked?'Select a route to compare community evidence.' :
    'Off by default. OSM evidence does not alter government comparisons or synthetic detections.');
   notify();
  }
  async function fetchRows(box,signal){
   if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey)
    throw Error('Community source not configured');
   const q=new URLSearchParams({
    select:'osm_key,latitude,longitude',order:'osm_key.asc',
    limit:String(PAGE_LIMIT)
   });
   q.append('latitude','gte.'+box.south.toFixed(7));
   q.append('latitude','lte.'+box.north.toFixed(7));
   q.append('longitude','gte.'+box.west.toFixed(7));
   q.append('longitude','lte.'+box.east.toFixed(7));
   const response=await fetch(cfg.supabaseUrl.replace(/\/$/,'')+
    '/rest/v1/'+SOURCE_TABLE+'?'+q.toString(),{
     headers:{apikey:cfg.supabasePublishableKey,Prefer:'count=exact'},
     signal,cache:'no-store',referrerPolicy:'no-referrer'
   });
   if(!response.ok)throw Error('Community source HTTP '+response.status);
   const rows=await response.json();
   const contentRange=response.headers.get('content-range')||'';
   const match=/^(?:[0-9]+-[0-9]+|[*])\/([0-9]+)$/.exec(contentRange);
   if(!match||!Array.isArray(rows)||rows.length>PAGE_LIMIT)
    throw Error('Community source exact-count header unavailable; coverage UNKNOWN');
   const total=Number(match[1]);
   if(!Number.isSafeInteger(total)||total<rows.length)
    throw Error('Invalid community source completeness proof');
   return {rows,total};
  }
  function officialFor(route){
   return officialEvidence[routes.indexOf(route)]||{status:'checking'};
  }
  function summaryFor(route,entry){
   const official=officialFor(route);
   // Route geometry and its community source records are stable per scan.
   // Recalculate only when the separate official evidence result changes.
   if(entry.summary&&entry.officialSnapshot===official)return entry.summary;
   const complete=official.status==='complete';
   entry.summary=summarize(route,entry.records,
     complete?official.records:[],geo,complete);
   entry.officialSnapshot=official;
   return entry.summary;
  }
  function viewSelected(){
   if(!toggle.checked||!selected)return;
   const entry=results.get(selected);
   if(!entry){say('Checking independent OSM evidence for selected route…');return}
   if(entry.status!=='complete'){
    say(entry.status==='unavailable'
      ?'Community route evidence UNKNOWN: '+entry.error+
       '. No partial corridor may be counted as zero.'
      :'Checking separate OpenStreetMap evidence along the selected route…');
    return;
   }
   const official=officialFor(selected);
   const summary=summaryFor(selected,entry);
   const overlap=official.status==='complete'
    ?' '+summary.possibleOverlaps+' OSM observation(s) within 30m of official-source points may overlap; not proof of identical devices.'
    :' Government-source overlaps unknown because official corridor evidence is incomplete.';
   say('Selected route: '+summary.communityNearRoute+
    ' OSM community observations within an illustrative 120m band ('+
    summary.uniqueMappedCoordinates+' exact mapped coordinate positions; '+
    summary.colocatedExtraObservations+' extra observations sharing coordinates).'+overlap+
    ' These are not detected vehicles or active-device counts. Counts are not added.');
  }
  function entryFor(route){
   if(!toggle.checked)return null;
   const entry=results.get(route);
   if(!entry)return {status:'checking'};
   if(entry.status==='complete')summaryFor(route,entry);
   return entry;
  }
  function select(route){
   selected=route;
   viewSelected();
  }
  function updateOfficial(route,outcome){
   const i=routes.indexOf(route);
   if(i<0)return;
   officialEvidence[i]=outcome;
   if(selected===route)viewSelected();
   notify();
  }
  function compareAll(nextRoutes,initialEvidence){
   cancel();
   if(!toggle.checked||!Array.isArray(nextRoutes)||!nextRoutes.length)return;
   if(nextRoutes.length>MAX_ALTERNATIVES){
    say('Community comparisons UNKNOWN: too many driving alternatives.');
    return;
   }
   routes=[...nextRoutes];selected=routes[0];
   officialEvidence=routes.map((_,i)=>initialEvidence?.[i]||{status:'checking'});
   const id=++generation,signal=(controller=new AbortController()).signal;
   routes.forEach(route=>results.set(route,{status:'checking'}));
   notify();viewSelected();
   let offset=0;
   async function worker(){
    while(offset<routes.length&&generation===id&&!signal.aborted){
     const route=routes[offset++];
     try{
      const scanned=await scanRoute(route,geo,fetchRows,signal);
      if(id!==generation||signal.aborted)return;
      results.set(route,{status:'complete',records:scanned.records,queries:scanned.queries});
     }catch(error){
      if(id!==generation||signal.aborted)return;
      results.set(route,{status:'unavailable',error:String(error.message||'Original OSM source unavailable').slice(0,170)});
     }
     if(selected===route)viewSelected();
     notify();
    }
   }
   activeTasks=Promise.all(Array.from({length:Math.min(2,routes.length)},()=>worker()));
  }
  // Compatibility for the selected-route callback; comparisons are cached.
  function choose(route,official){
   if(!toggle.checked){cancel();return}
   if(!routes.includes(route))compareAll([route],[official]);
   else {updateOfficial(route,official);select(route)}
  }
  toggle.addEventListener('change',()=>{
   if(!toggle.checked)cancel();
   else if(routes.length){viewSelected()}
  });
  return Object.freeze({choose,select,cancel,compareAll,updateOfficial,
   entryFor,isEnabled:()=>toggle.checked});
 }
 return Object.freeze({summarize,splitBox,scanRoute,format,install});
});
