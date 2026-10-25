/* Independent nationwide vendor transparency-portal *agency* map.
 * EyesOnFlock public portal snapshots, geocoded by FlockHopper/deflock-data.
 * These are agency approximate jurisdiction centers, NEVER camera positions.
 * CC BY-SA 4.0 secondary research. No verified camera/route claims.
 */
(function(root,build){
 const api=build();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronVendorAgencyLayer=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const BASE='https://deflockdata.dontgetflocked.com/';
 const MAX_NODES=15000,MIN_PORTALS=700,MAX_AGE_DAYS=45;
 function validateMeta(m,now=Date.now()){
   if(!m||typeof m!=='object'||typeof m.generatedAt!=='string'||
      !Number.isInteger(m.portalCount)||m.portalCount<MIN_PORTALS||
      !Number.isInteger(m.featureCount)||m.featureCount<5000||
      !Number.isFinite(Date.parse(m.generatedAt))||
      Date.parse(m.generatedAt)>now+3600000||
      now-Date.parse(m.generatedAt)>MAX_AGE_DAYS*86400000)
      throw Error('National agency transparency source incomplete or stale');
   return m;
 }
 function parseNodes(collection,meta) {
   if(!collection||collection.type!=='FeatureCollection'||
      !Array.isArray(collection.features)||
      collection.features.length!==meta.featureCount||
      collection.features.length>MAX_NODES)
      throw Error('Transparency portal agency records incomplete');
   const result=[],seen=new Set();
   for(const f of collection.features) {
     const p=f?.properties,g=f?.geometry;
     if(!p||!p.isPortal||p.isJunk||p.isInactive)continue;
     const slug=p.portalSlug;
     if(typeof slug!=='string'||!/^[a-z0-9-]{3,110}$/.test(slug)||
        seen.has(slug))throw Error('Duplicate or invalid portal agency identity');
     seen.add(slug);
     if(g?.type!=='Point'||!Array.isArray(g.coordinates)||g.coordinates.length!==2)
       throw Error('Portal agency centroid invalid');
     const [lon,lat]=g.coordinates;
     if(!Number.isFinite(lat)||!Number.isFinite(lon)||
        lat<17||lat>72||lon< -180||lon> -64)
       throw Error('Portal agency outside supported region');
     if(!['place','place_variant','county','google','google_places','state','default','manual'].includes(p.geocodeMethod))
       continue;
     result.push({slug,lat,lon,
       label:String(p.name||'Agency').slice(0,120),
       method:p.geocodeMethod,reportedCameras:Number.isFinite(p.cameras)?p.cameras:null,
       portal:'https://eyesonflock.com/portal/'+slug});
   }
   if(result.length<MIN_PORTALS*.7)
     throw Error('Too few distinct publisher-reported portal agencies');
   return result;
 }
 function install(map,toggle,status){
   if(!map||!toggle||!status)return;
   const L=window.L,layer=L.layerGroup(),controller={abort:null},cache={rows:null,stamp:null};
   function note(message){status.textContent=message;}
   function draw(){
     layer.clearLayers();
     if(!toggle.checked||!cache.rows)return;
     const z=map.getZoom(),bounds=map.getBounds();
     const visible=cache.rows.filter(x=>bounds.contains([x.lat,x.lon])&&
       !['state','default'].includes(x.method));
     if(z<8){
       const grouped=new Map(),size=z<5?3:z<7?1:0.5;
       for(const x of visible){
         const a=Math.floor(x.lat/size),b=Math.floor(x.lon/size),key=a+':'+b;
         grouped.set(key,(grouped.get(key)||0)+1);
       }
       for(const [key,count] of grouped){
         const [a,b]=key.split(':').map(Number);
         L.circleMarker([(a+.5)*size,(b+.5)*size],{
           radius:Math.min(18,Math.max(4,4*Math.log10(count+1))),
           color:'#c49df5',weight:1.5,fillColor:'#8756ba',fillOpacity:.4
         }).bindTooltip(count+' Flock transparency-portal agencies in an approximate '+size+'° region. This circle center is NOT a camera position.')
           .addTo(layer);
       }
     }else{
       if(visible.length>1600){note('Too many vendor portal agencies here; zoom closer. Camera locations unknown.');return;}
       for(const x of visible){
         const popup=document.createElement('div');
         const title=document.createElement('strong');
         title.textContent=x.label;popup.append(title);
         const disclaimer=document.createElement('p');
         disclaimer.textContent='Independent Flock transparency PORTAL agency. Approximate agency jurisdiction center, NOT a camera position. Camera counts and device operation are not verified by Katoptron.';
         popup.append(disclaimer);
         const link=document.createElement('a');link.href=x.portal;
         link.target='_blank';link.rel='noopener noreferrer';
         link.textContent='Inspect EyesOnFlock portal snapshot';popup.append(link);
         L.circleMarker([x.lat,x.lon],{radius:5,color:'#c49df5',
           fillColor:'#8756ba',fillOpacity:.55,weight:1.5})
           .bindPopup(popup).addTo(layer);
       }
     }
     note(cache.rows.length.toLocaleString()+' independent vendor-transparency portal agencies in national snapshot; '+visible.length.toLocaleString()+' mapped agency centers in view. NONE are camera pins. Research: EyesOnFlock/FlockHopper (CC BY-SA 4.0).');
   }
   async function load(){
     if(!toggle.checked)return;
     if(cache.rows){if(!map.hasLayer(layer))layer.addTo(map);draw();return;}
     note('Retrieving independently compiled Flock portal agency disclosures…');
     controller.abort?.abort();controller.abort=new AbortController();
     try{
       const signal=controller.abort.signal;
       const metaResponse=await fetch(BASE+'sharing-network-meta.json',{signal,cache:'no-store'});
       if(!metaResponse.ok)throw Error('No current agency source metadata');
       const meta=validateMeta(await metaResponse.json());
       const nodesResponse=await fetch(BASE+'sharing-network-nodes.geojson',{signal,cache:'no-store'});
       if(!nodesResponse.ok)throw Error('No current agency source geography');
       cache.rows=parseNodes(await nodesResponse.json(),meta);
       cache.stamp=meta.generatedAt;
       if(toggle.checked){layer.addTo(map);draw();}
     }catch(error){
       if(error.name==='AbortError')return;
       note('Independent portal agency geography unavailable or outdated. No approximate agency markers shown; verified camera map unaffected.');
     }
   }
   toggle.addEventListener('change',()=>{
     if(!toggle.checked){
       controller.abort?.abort();
       if(map.hasLayer(layer))map.removeLayer(layer);
       note('Vendor portal agency locations hidden. This control never changes verified camera counts.');
     }else load();
   });
   map.on('moveend',()=>{if(toggle.checked&&cache.rows)draw();});
   note('Optional Flock vendor portal agency map (not individual camera positions). Source CC BY-SA 4.0. Enable to load.');
   if(toggle.checked)load();
   return {draw,load};
 }
 return Object.freeze({validateMeta,parseNodes,install});
});
