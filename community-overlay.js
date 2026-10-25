/* Optional ODbL community overlay. Never enters official evidence, route
 * proximity comparison, replay, or verified-point source arrays.
 * Off by default. Sparse regional density at z<10; exact OSM observations
 * queried only at zoom 10+, bounded by 1,000 confirmed-complete results per viewport.
 */
(() => {
 'use strict';
 const MAX_POINTS=1000;
 const get=id=>document.getElementById(id);
 function install(map,cfg){
  const toggle=get('showCommunity');
  const status=get('communityOverlayStatus');
  if(!map||!toggle||!status)return;
  const L=window.L;
  const dots=L.layerGroup(),regions=L.layerGroup();
  let active=false,revision=0,abort=null,densityLoaded=false,delay=null;
  function note(message){status.textContent=message;}
  function link(key){
   return typeof key==='string'&&/^(node|way)\/[1-9][0-9]{0,17}$/.test(key)
     ?'https://www.openstreetmap.org/'+key:null;
  }
  async function query(table,params,signal,counted=false){
   if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey)
    throw Error('Public community database not configured');
   const root=cfg.supabaseUrl.replace(/\/$/,'');
   const response=await fetch(root+'/rest/v1/'+table+'?'+params.toString(),{
    headers:{apikey:cfg.supabasePublishableKey,...(counted?{Prefer:'count=exact'}:{})},
    cache:'no-store',referrerPolicy:'no-referrer',signal});
   if(!response.ok)throw Error('Community source HTTP '+response.status);
   const rows=await response.json();
   if(!Array.isArray(rows))throw Error('Invalid community source response');
   if(!counted)return rows;
   const match=/^(?:[0-9]+-[0-9]+|[*])\/([0-9]+)$/.exec(response.headers.get('content-range')||'');
   if(!match)throw Error('Community viewport completeness unknown: missing source count');
   const total=Number(match[1]);
   if(!Number.isSafeInteger(total)||total<rows.length)throw Error('Invalid exact viewport count');
   return {rows,total};
  }
  async function loadDensity(id,signal){
   const rows=await query('flock_public_osm_community_density',
    new URLSearchParams({select:'cell_latitude,cell_longitude,community_report_count',limit:'500'}),signal);
   if(id!==revision||!active)return;
   if(rows.length>=500)throw Error('Incomplete national density results');
   regions.clearLayers();
   for(const r of page.rows){
    const lat=Number(r.cell_latitude),lon=Number(r.cell_longitude),
      count=Number(r.community_report_count);
    if(!Number.isFinite(lat)||!Number.isFinite(lon)||
       !Number.isSafeInteger(count)||count<=0)continue;
    L.circleMarker([lat,lon],{
      radius:Math.min(24,Math.max(4,Math.log10(count+1)*7)),
      color:'#f3d1df',fillColor:'#9a3565',fillOpacity:.55,weight:1
    }).bindTooltip(count.toLocaleString()+
      ' community observations in this approximate 3° grid cell; not a camera location.')
      .addTo(regions);
   }
   densityLoaded=true;
   note('Showing national community-report density in 3° cells. Zoom in to see OSM camera observations.');
  }
  async function loadPoints(id,signal){
   const b=map.getBounds();
   const south=Math.max(17,b.getSouth()),north=Math.min(72,b.getNorth());
   const west=Math.max(-180,b.getWest()),east=Math.min(-64,b.getEast());
   if(south>north||west>east){
     note('Move to a U.S. location for community map observations.');return;
   }
   const q=new URLSearchParams({
    select:'osm_key,latitude,longitude,source_timestamp,source_snapshot_date,last_seen_sync_at',
    order:'osm_key.asc',limit:String(MAX_POINTS)});
   q.append('latitude','gte.'+south.toFixed(7));
   q.append('latitude','lte.'+north.toFixed(7));
   q.append('longitude','gte.'+west.toFixed(7));
   q.append('longitude','lte.'+east.toFixed(7));
   const page=await query('flock_osm_community_points',q,signal,true);
   if(id!==revision||!active)return;
   if(page.total>page.rows.length){
    dots.clearLayers();
    note(page.total.toLocaleString()+' OSM observations in view. Zoom closer; no truncated camera sample is displayed.');
    return;
   }
   dots.clearLayers();
   for(const r of page.rows){
    const lat=Number(r.latitude),lon=Number(r.longitude);
    if(!Number.isFinite(lat)||!Number.isFinite(lon))continue;
    const marker=L.circleMarker([lat,lon],{
      radius:4.5,color:'#6d204c',fillColor:'#b94b83',
      fillOpacity:.8,weight:1.2
    });
    const popup=document.createElement('div');
    const heading=document.createElement('strong');
    heading.textContent='Community-reported Flock camera (OSM)';
    popup.append(heading);
    const p=document.createElement('p');
    p.textContent='Unconfirmed OpenStreetMap observation. Not part of the verified camera count or route encounter simulation.';
    popup.append(p);
    const url=link(r.osm_key);
    if(url){
     const a=document.createElement('a');a.href=url;a.target='_blank';
     a.rel='noopener noreferrer';a.textContent='Original OSM record';
     popup.append(a);
    }
    if(r.source_timestamp){
      const edited=document.createElement('small');
      edited.textContent='OSM record last edited: '+String(r.source_timestamp).slice(0,10)+'. This is not a device inspection date.';
      popup.append(edited);
    }
    if(r.source_snapshot_date){
      const receipt=document.createElement('p');
      receipt.textContent='Last included in imported OSM dataset: '+String(r.source_snapshot_date).slice(0,10)+'. Not a physical camera inspection.';
      popup.append(receipt);
    }
    marker.bindPopup(popup).addTo(dots);
   }
   note(page.total.toLocaleString()+' community-reported camera observations shown in view (complete query). Not confirmed active cameras.');
  }
  async function refresh(){
   const id=++revision;
   if(abort)abort.abort();
   abort=new AbortController();
   dots.clearLayers();
   if(!active)return;
   if(map.getZoom()<10){
    if(map.hasLayer(dots))map.removeLayer(dots);
    if(!map.hasLayer(regions))regions.addTo(map);
    if(densityLoaded){
     note('National community-report density shown. Grid-cell markers are not camera locations.');
     return;
    }
    note('Loading approximate national community density…');
    try{await loadDensity(id,abort.signal)}
    catch(e){if(e.name!=='AbortError'&&id===revision)note('Community density unavailable: '+e.message)}
    return;
   }
   if(map.hasLayer(regions))map.removeLayer(regions);
   if(!map.hasLayer(dots))dots.addTo(map);
   note('Loading community source observations for this map view…');
   try{await loadPoints(id,abort.signal)}
   catch(e){if(e.name!=='AbortError'&&id===revision)note('Community locations unavailable: '+e.message)}
  }
  toggle.addEventListener('change',()=>{
   active=toggle.checked;
   if(!active){
     revision++;if(abort)abort.abort();
     if(map.hasLayer(dots))map.removeLayer(dots);
     if(map.hasLayer(regions))map.removeLayer(regions);
     note('Community OpenStreetMap overlay off. Official and route-simulation evidence unchanged.');
   }else{refresh()}
  });
  map.on('moveend',()=>{
   if(!active)return;
   clearTimeout(delay);delay=setTimeout(refresh,250);
  });
  note('Off by default. Community locations are unconfirmed and excluded from official route simulation and plate-detection modeling.');
 }
 window.KatoptronCommunityOverlay={install};
})();
