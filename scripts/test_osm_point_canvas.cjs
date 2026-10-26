const assert=require('node:assert/strict');
const O=require('../osm-point-canvas.js');
const MIN=90000;
function fixture(coords){
 const bytes=Buffer.alloc(coords.length*8);
 coords.forEach(([lat,lon],i)=>{
  bytes.writeInt32BE(Math.round(lat*1e7),i*8);
  bytes.writeInt32BE(Math.round(lon*1e7),i*8+4);
 });
 return {point_count:coords.length,source_snapshot_date:'2026-10-25',
   coordinates_base64:bytes.toString('base64')};
}
const many=Array.from({length:MIN},(_,i)=>[38.5816+(i%50)*0.00001,-121.4944+Math.floor(i/50)*0.00001]);
const data=O.decode(fixture(many));
assert.equal(data.count,MIN);
for(const index of [0,51,89000]){
 const actual=O.coordinates(data,index),expected=many[index];
 assert.ok(Math.abs(actual[0]-expected[0])<=0.00000011&&
           Math.abs(actual[1]-expected[1])<=0.00000011,
           'Coordinate must retain at least 1e-7 degree source precision');
}
const origin={x:0,y:0},z=4;
const p=O.mercator(many[0][0],many[0][1],z,origin);
const selected=O.nearest(data,p.x,p.y,z,origin,
 {south:38,north:40,west:-122,east:-120});
assert.ok(selected);
assert.ok(selected.distancePixels<6,'Point must be at ACTUAL OSM source coordinate');
assert.ok(selected.point[0]>=38.5&&selected.point[1]< -120,'Offshore grid center not allowed');

// Leaflet mapPane translate separates layer pixels from viewport pixels.
// Canvas is pinned at container origin (-mapPanePos) while original map
// projection and getPixelOrigin() produce layer coordinates. An uncorrected
// 200px pan used to leave OSM dots roughly 200px off the map and make
// source clicks miss.
const shift={x:230,y:-140},previousOrigin={x:1200,y:840};
const corrected=O.containerPixelOrigin(previousOrigin,shift);
assert.deepEqual(corrected,{x:1430,y:700});
const sourceLat=many[0][0],sourceLon=many[0][1];
const layerPixel=O.mercator(sourceLat,sourceLon,z,previousOrigin);
const correctContainerPixel=O.mercator(sourceLat,sourceLon,z,corrected);
assert.ok(Math.abs(layerPixel.x-correctContainerPixel.x-230)<1e-7);
assert.ok(Math.abs(layerPixel.y-correctContainerPixel.y+140)<1e-7);
assert.throws(()=>O.containerPixelOrigin({x:NaN,y:0},shift),/Invalid/);
const postPan=O.nearest(data,correctContainerPixel.x,correctContainerPixel.y,
 z,corrected,{south:38,north:40,west:-122,east:-120});
assert.ok(postPan&&postPan.distancePixels<6,
 'Nearest OSM dot must use the same viewport origin as canvas drawing');
assert.equal(O.nearest(data,-100,-100,z,origin,{south:38,north:40,west:-122,east:-120}),null);
assert.throws(()=>O.decode({...fixture(many),point_count:MIN+1}),/reconcile/);
const corrupt=fixture(many); corrupt.coordinates_base64='@@';
assert.throws(()=>O.decode(corrupt),/Incomplete/);
console.log('ALL-ZOOM ORIGINAL OSM POINT CANVAS PASS, no aggregate or fictitious coordinates');
