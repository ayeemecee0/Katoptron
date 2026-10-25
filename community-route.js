/* Opt-in source-separated route comparison with community OpenStreetMap points.
 * Actual plate reads, route exposure probabilities, and official counts
 * are NEVER synthesized from community observations.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronCommunityRoute=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const RADIUS_M=120,OVERLAP_M=30,MAX_PER_BOX=1000;
 const SOURCE_TABLE='flock_osm_community_points';
 function summarize(route,osm,official,geo,officialComplete){
  if(!route||!Array.isArray(route.points)||!Array.isArray(osm)||
    !geo||typeof geo.closestOnRoute!=='function'||typeof geo.haversine!=='function')
   throw Error('Cannot summarize incomplete community route data');
  const ids=new Set();
  const candidates=[];
  for(const r of osm){
   if(!r||typeof r.osm_key!=='string'||!(/^(node|way)\/[1-9][0-9]{0,17}$/).test(r.osm_key)||
      !Number.isFinite(Number(r.latitude))||!Number.isFinite(Number(r.longitude)))
    throw Error('Malformed OSM camera evidence');
   if(ids.has(r.osm_key))continue;
   ids.add(r.osm_key);
   const p=[Number(r.latitude),Number(r.longitude)];
   if(geo.closestOnRoute(p,route.points).distance<=RADIUS_M)candidates.push(p);
  }
  let possibleOverlaps=null;
  if(officialComplete&&Array.isArray(official)){
   const exact=official.filter(p=>p.location_accuracy==='exact'&&
      p.evidence_tier!=='independently_corroborated'&&
      Number.isFinite(Number(p.latitude))&&Number.isFinite(Number(p.longitude)));
   possibleOverlaps=candidates.filter(p=>exact.some(o=>
    geo.haversine(p,[Number(o.latitude),Number(o.longitude)])<=OVERLAP_M)).length;
  }
  return {communityNearRoute:candidates.length,possibleOverlaps,
    proximityMeters:RADIUS_M,overlapMeters:OVERLAP_M};
 }
 function install({cfg,geo,showStatus}){
  const toggle=document.getElementById('compareCommunityRoute');
  const status=document.getElementById('communityRouteStatus');
  if(!toggle||!status)return null;
  let sequence=0,controller=null,priorRoute=null;
  function say(s){status.textContent=s}
  function cancel(){
   sequence++;controller?.abort();controller=null;
   priorRoute=null;
   say(toggle.checked?
      'Select a route to inspect community evidence separately.' :
      'Off by default. Community points do not affect government-source comparisons.');
  }
  async function fetchRows(box,signal){
   const q=new URLSearchParams({
    select:'osm_key,latitude,longitude',
    order:'osm_key.asc',limit:String(MAX_PER_BOX+1)
   });
   q.append('latitude','gte.'+box.south.toFixed(6));
   q.append('latitude','lte.'+box.north.toFixed(6));
   q.append('longitude','gte.'+box.west.toFixed(6));
   q.append('longitude','lte.'+box.east.toFixed(6));
   if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey)
    throw Error('Community evidence source not configured');
   const response=await fetch(cfg.supabaseUrl.replace(/\/$/,'')+
    '/rest/v1/'+SOURCE_TABLE+'?'+q.toString(),{
     headers:{apikey:cfg.supabasePublishableKey},signal,cache:'no-store'
   });
   if(!response.ok)throw Error('Community evidence HTTP '+response.status);
   const rows=await response.json();
   if(!Array.isArray(rows)||rows.length>MAX_PER_BOX)
    throw Error('High-density corridor cannot be checked completely');
   return rows;
  }
  async function choose(route,officialEvidence){
   if(!toggle.checked){cancel();return}
   if(!route){cancel();return}
   const id=++sequence;
   controller?.abort();controller=new AbortController();
   priorRoute=route;
   say('Checking separate OpenStreetMap community evidence along selected route…');
   try{
    const boxes=geo.corridorBoxes(route.points,{
      span:0.16,pad:0.003,maxBoxes:64
    });
    const found=new Map();
    let offset=0;
    const signal=controller.signal;
    async function worker(){
     while(offset<boxes.length){
      if(signal.aborted)throw Error('Canceled');
      const box=boxes[offset++];
      const rows=await fetchRows(box,signal);
      for(const row of rows)found.set(row.osm_key,row);
     }
    }
    await Promise.all(Array.from({length:Math.min(3,boxes.length)},()=>worker()));
    if(id!==sequence||signal.aborted||!toggle.checked)return;
    const officialComplete=officialEvidence?.status==='complete';
    const result=summarize(route,[...found.values()],
      officialComplete?officialEvidence.records:[],geo,officialComplete);
    const overlap=officialComplete?
      ' '+result.possibleOverlaps+' OSM observation(s) lie within 30m of an official-source point and may overlap; NOT proof of identical cameras.' :
      ' Official-source corridor verification is incomplete, so possible overlaps are unknown.';
    say('Selected route: '+result.communityNearRoute+
     ' OSM community observations within an illustrative 120m band.'+overlap+
     ' These are unconfirmed locations, not detected vehicles or active-device counts. No counts are added together.');
    if(typeof showStatus==='function')showStatus(result);
   }catch(error){
    if(id!==sequence||signal.aborted)return;
    say('Community route evidence UNKNOWN: '+(error?.message||'source unavailable')+
      '. A partial corridor must never be counted as zero cameras.');
   }
  }
  toggle.addEventListener('change',()=>{
   if(!toggle.checked)cancel();
  });
  return Object.freeze({choose,cancel,isEnabled:()=>toggle.checked});
 }
 return Object.freeze({summarize,install});
});
