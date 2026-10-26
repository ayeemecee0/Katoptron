/* Individual original OSM observations at every zoom. Unverified community
 * layer remains separate from government points and synthetic encounters. */
(()=>{
 'use strict';
 const get=id=>document.getElementById(id);
 function install(map,cfg){
  const toggle=get('showCommunity'),status=get('communityOverlayStatus');
  if(!map||!toggle||!status)return;
  const C=window.KatoptronOsmCanvas,L=window.L;
  let source=null,layer=null,loading=null,enabled=toggle.checked;
  const note=m=>status.textContent=m;
  async function query(table,params){
   if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey)
     throw Error('Public community data not configured');
   const root=cfg.supabaseUrl.replace(/\/$/,'');
   const r=await fetch(root+'/rest/v1/'+table+'?'+params.toString(),{
    headers:{apikey:cfg.supabasePublishableKey},cache:'no-store',referrerPolicy:'no-referrer'});
   if(!r.ok)throw Error('Public OSM HTTP '+r.status);
   const rows=await r.json();
   if(!Array.isArray(rows))throw Error('Invalid community data response');
   return rows;
  }
  async function inspect(point){
   const [lat,lon]=point;
   try{
    const q=new URLSearchParams({select:'osm_key,latitude,longitude,source_timestamp',
      latitude:'gte.'+(lat-0.00000011).toFixed(8),
      longitude:'gte.'+(lon-0.00000011).toFixed(8),
      order:'osm_key.asc',limit:'3'});
    q.append('latitude','lte.'+(lat+0.00000011).toFixed(8));
    q.append('longitude','lte.'+(lon+0.00000011).toFixed(8));
    const rows=await query('flock_osm_community_points',q);
    const r=rows.find(x=>Math.abs(Number(x.latitude)-lat)<0.00000011&&
       Math.abs(Number(x.longitude)-lon)<0.00000011);
    if(!r)throw Error('Original OSM source not found');
    const box=document.createElement('div');
    const title=document.createElement('strong');
    title.textContent='Unverified OSM community camera report';box.append(title);
    const msg=document.createElement('p');
    msg.textContent='Reported location and manufacturer are unconfirmed. Not a government-verified Flock installation or a measured detection.';
    box.append(msg);
    if(/^(node|way)\/[1-9][0-9]{0,17}$/.test(r.osm_key)){
      const a=document.createElement('a');
      a.href='https://www.openstreetmap.org/'+r.osm_key;a.target='_blank';
      a.rel='noopener noreferrer';a.textContent='Inspect original OSM record';
      box.append(a);
    }
    L.popup().setLatLng(point).setContent(box).openOn(map);
   }catch(e){note('Community source inspection unavailable: '+e.message)}
  }
  function display(){
   if(!enabled||!source)return;
   if(!layer)layer=C.install(map,source,inspect);
   note(source.count.toLocaleString()+' original OSM report coordinates visible as dots at all zooms. Unverified.');
  }
  async function load(){
   if(loading)return loading;
   loading=(async()=>{
     const rows=await query('rpc/flock_public_osm_exact_render_snapshot',
       new URLSearchParams({select:'point_count,source_snapshot_date,coordinates_base64'}));
     if(rows.length!==1)throw Error('Incomplete original national OSM map');
     source=C.decode(rows[0]);
     display();
   })();
   try{await loading}finally{loading=null}
  }
  toggle.addEventListener('change',()=>{
   enabled=toggle.checked;
   if(!enabled){
    if(layer){map.removeLayer(layer);layer=null;}
    note('Community OpenStreetMap overlay off. Official and route-simulation evidence unchanged.');
   }else if(source)display();
   else{note('Loading original OSM dots…');
    load().catch(e=>note('Community original-coordinate layer unavailable: '+e.message))}
  });
  if(enabled){note('Loading individual OSM coordinates; no approximate clusters.');
    load().catch(e=>note('Community original-coordinate layer unavailable: '+e.message))}
  else note('Community overlay off.');
 }
 window.KatoptronCommunityOverlay={install};
})();
