/* Density fallback for crowded OpenStreetMap community-only map viewports.
 * Every marker is an aggregate CELL CENTER, never an inferred camera location.
 * Never affects government verified records, simulated detections, or routing.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronViewportDensity=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const CELL_LIMIT=500;
 function cellForZoom(zoom){
  if(!Number.isFinite(zoom)||zoom<10)throw Error('Community viewport zoom invalid');
  return zoom<11?0.25:zoom<12?0.1:zoom<13?0.05:
    zoom<14?0.02:zoom<15?0.01:0.005;
 }
 function bounded(bounds){
  if(!bounds)throw Error('Viewport missing');
  const {south,north,west,east}=bounds;
  if(![south,north,west,east].every(Number.isFinite)||
     south<17||north>72||west< -180||east> -64||
     south>=north||west>=east||north-south>4||east-west>6)
   throw Error('Community viewport exceeds safe density aggregation bounds');
  return {south,north,west,east};
 }
 async function fetchCells(cfg,bounds,zoom,total,signal,request=fetch){
  if(!Number.isSafeInteger(total)||total<0||!cfg?.supabaseUrl||
     !cfg?.supabasePublishableKey)
    throw Error('Cannot reconcile community density without source count');
  const box=bounded(bounds);
  const cell=cellForZoom(zoom);
  const p=new URLSearchParams({
   p_south:box.south.toFixed(7),p_north:box.north.toFixed(7),
   p_west:box.west.toFixed(7),p_east:box.east.toFixed(7),
   p_cell_degrees:String(cell)
  });
  const response=await request(cfg.supabaseUrl.replace(/\/$/,'')+
    '/rest/v1/rpc/flock_public_osm_viewport_density?'+p.toString(),{
    headers:{apikey:cfg.supabasePublishableKey},
    cache:'no-store',referrerPolicy:'no-referrer',signal
  });
  if(!response.ok)throw Error('Community density HTTP '+response.status);
  const rows=await response.json();
  if(!Array.isArray(rows)||rows.length>CELL_LIMIT)
   throw Error('Viewport density incomplete; zoom closer');
  let sum=0;
  for(const r of rows){
   const lat=Number(r.cell_latitude),lon=Number(r.cell_longitude);
   const count=Number(r.community_report_count);
   if(!Number.isFinite(lat)||!Number.isFinite(lon)||
      !Number.isSafeInteger(count)||count<=0||
      lat<16.5||lat>72.5||lon< -180.5||lon> -63.5)
    throw Error('Community density geometry or count invalid');
   sum+=count;
   if(!Number.isSafeInteger(sum))throw Error('Community aggregate sum overflow');
  }
  if(sum!==total)
   throw Error('Community density does not reconcile with exact source count');
  return Object.freeze({rows,total,cell});
 }
 return Object.freeze({cellForZoom,bounded,fetchCells});
});
