/* All-zoom original-coordinate OSM point layer. Does NOT turn community
 * observations into installed, manufacturer-certified or active Flock cameras.
 * A single 8-byte/point public Postgres snapshot replaces misleading grid
 * centroid clusters. Leaflet SVG/CircleMarker objects for all 100k+ source
 * rows would be too heavy; Canvas keeps the exact reported coordinates.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronOsmCanvas=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCALE=10000000,MIN_POINTS=90000,MAX_POINTS=200000,EARTH=Math.PI/180;
 function decode(snapshot){
  if(!snapshot||!Number.isSafeInteger(snapshot.point_count)||
     snapshot.point_count<MIN_POINTS||snapshot.point_count>MAX_POINTS||
     typeof snapshot.source_snapshot_date!=='string'||
     !/^\d{4}-\d{2}-\d{2}$/.test(snapshot.source_snapshot_date)||
     typeof snapshot.coordinates_base64!=='string'||
     snapshot.coordinates_base64.length>2600000||
     !/^[A-Za-z0-9+\/=\r\n]+$/.test(snapshot.coordinates_base64))
    throw Error('Incomplete OSM original-coordinate snapshot');
  const base64=snapshot.coordinates_base64.replace(/\s/g,'');
  const raw=(typeof atob==='function'?atob(base64):
      Buffer.from(base64,'base64').toString('latin1'));
  if(raw.length!==snapshot.point_count*8)
    throw Error('OSM coordinate snapshot size does not reconcile');
  const bytes=new Uint8Array(raw.length);
  for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
  const view=new DataView(bytes.buffer);
  for(let i=0;i<snapshot.point_count;i++){
   const lat=view.getInt32(i*8)/SCALE;
   const lon=view.getInt32(i*8+4)/SCALE;
   if(lat<17||lat>72||lon< -180||lon> -64)
     throw Error('OSM coordinate snapshot outside source bounds');
  }
  return Object.freeze({view,count:snapshot.point_count,
    date:snapshot.source_snapshot_date});
 }
 function coordinates(data,index){
  if(!data||!Number.isSafeInteger(index)||index<0||index>=data.count)
    throw Error('Invalid OSM source index');
  return [data.view.getInt32(index*8)/SCALE,
          data.view.getInt32(index*8+4)/SCALE];
 }
 function mercator(lat,lon,zoom,origin){
  const scale=256*Math.pow(2,zoom);
  const radians=lat*EARTH;
  const sin=Math.max(-0.9999,Math.min(0.9999,Math.sin(radians)));
  return {x:(lon+180)/360*scale-origin.x,
    y:(0.5-Math.log((1+sin)/(1-sin))/(4*Math.PI))*scale-origin.y};
 }
 // Leaflet's overlay pane is translated with the map pane while the
 // canvas is anchored to containerPoint [0,0]. Canvas pixel coordinates and
 // click events are therefore CONTAINER points, not Leaflet LAYER points.
 // getPixelOrigin() alone yields layer points and creates a growing offset
 // from coastlines as the user pans (the reported offshore/camera drift bug).
 function containerPixelOrigin(pixelOrigin,canvasLayerOffset){
  if(!pixelOrigin||!canvasLayerOffset||
     !Number.isFinite(pixelOrigin.x)||!Number.isFinite(pixelOrigin.y)||
     !Number.isFinite(canvasLayerOffset.x)||!Number.isFinite(canvasLayerOffset.y))
   throw Error('Invalid Leaflet canvas origin');
  return {x:pixelOrigin.x+canvasLayerOffset.x,
          y:pixelOrigin.y+canvasLayerOffset.y};
 }
 function nearest(data,px,py,zoom,origin,bounds,radius=9){
  if(!data||!Number.isFinite(px)||!Number.isFinite(py)||
     !Number.isFinite(zoom)||!origin||!bounds)return null;
  let best=radius*radius,index=-1,point=null;
  for(let i=0;i<data.count;i++){
   const [lat,lon]=coordinates(data,i);
   if(lat<bounds.south||lat>bounds.north||
      lon<bounds.west||lon>bounds.east)continue;
   const p=mercator(lat,lon,zoom,origin);
   const d=(px-p.x)**2+(py-p.y)**2;
   if(d<best){best=d;index=i;point=[lat,lon]}
  }
  return index<0?null:{index,point,distancePixels:Math.sqrt(best)};
 }
 function install(map,data,onPick){
  if(!map||!data||typeof onPick!=='function'||typeof L==='undefined')
    throw Error('OSM canvas map unavailable');
  const Layer=L.Layer.extend({
   onAdd(m){
    this._map=m;
    this._canvas=L.DomUtil.create('canvas','katoptron-osm-exact-canvas');
    this._canvas.style.pointerEvents='none';
    this._canvas.style.position='absolute';
    m.getPanes().overlayPane.appendChild(this._canvas);
    m.on('moveend zoomend resize',this.redraw,this);
    m.on('click',this.handleClick,this);
    this.redraw();
   },
   onRemove(m){
    m.off('moveend zoomend resize',this.redraw,this);
    m.off('click',this.handleClick,this);
    if(this._canvas)this._canvas.remove();
   },
   getBounds(){
    const b=this._map.getBounds();
    return {south:b.getSouth(),north:b.getNorth(),
      west:b.getWest(),east:b.getEast()};
   },
   redraw(){
    if(!this._canvas)return;
    const m=this._map,sz=m.getSize();
    const ratio=Math.min(2,Math.max(1,window.devicePixelRatio||1));
    this._canvas.width=Math.ceil(sz.x*ratio);
    this._canvas.height=Math.ceil(sz.y*ratio);
    this._canvas.style.width=sz.x+'px';
    this._canvas.style.height=sz.y+'px';
    const canvasLayerOffset=m.containerPointToLayerPoint([0,0]);
    L.DomUtil.setPosition(this._canvas,canvasLayerOffset);
    const ctx=this._canvas.getContext('2d',{alpha:true});
    ctx.setTransform(ratio,0,0,ratio,0,0);
    const z=m.getZoom(),
          origin=containerPixelOrigin(m.getPixelOrigin(),canvasLayerOffset),
          b=this.getBounds();
    const radius=z<6?1:z<10?1.5:2.8;
    ctx.fillStyle='rgba(179,64,109,0.76)';
    // One actual underlying reported position per drawn dot. Close points
    // may overlap visually on a low-resolution display, not aggregate.
    for(let i=0;i<data.count;i++){
      const lat=data.view.getInt32(i*8)/SCALE;
      const lon=data.view.getInt32(i*8+4)/SCALE;
      if(lat<b.south||lat>b.north||lon<b.west||lon>b.east)continue;
      const p=mercator(lat,lon,z,origin);
      if(p.x< -5||p.x>sz.x+5||p.y< -5||p.y>sz.y+5)continue;
      ctx.fillRect(p.x-radius,p.y-radius,2*radius,2*radius);
    }
   },
   handleClick(event){
    const m=this._map,p=event.containerPoint;
    const origin=containerPixelOrigin(m.getPixelOrigin(),
      m.containerPointToLayerPoint([0,0]));
    const hit=nearest(data,p.x,p.y,m.getZoom(),origin,
      this.getBounds(),m.getZoom()<8?6:9);
    if(hit)onPick(hit.point,hit.distancePixels);
   }
  });
  return new Layer().addTo(map);
 }
 return Object.freeze({decode,coordinates,mercator,nearest,containerPixelOrigin,install});
});
