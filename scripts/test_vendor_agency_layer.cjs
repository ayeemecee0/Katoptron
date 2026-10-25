const assert=require('node:assert/strict');
const source=require('../vendor-agency-layer.js');
const now=Date.now(),iso=new Date(now).toISOString();
const meta={generatedAt:iso,portalCount:1000,featureCount:5001};
assert.equal(source.validateMeta(meta,now).portalCount,1000);
assert.throws(()=>source.validateMeta({...meta,portalCount:50},now),/incomplete or stale/);
assert.throws(()=>source.validateMeta({...meta,generatedAt:'2024-01-01T00:00:00Z'},now),/incomplete or stale/);
const features=Array.from({length:5001},(_,i)=>({
 type:'Feature',geometry:{type:'Point',coordinates:[-95+(i%15)*.001,35+(i%15)*.001]},
 properties:{name:'Demo agency '+i,isPortal:i<1000,portalSlug:i<1000?'demo-agency-'+i:null,
 isJunk:false,isInactive:false,geocodeMethod:'place',cameras:10}
}));
const dataset={type:'FeatureCollection',features};
let parsed=source.parseNodes(dataset,meta);
assert.equal(parsed.length,1000);
assert.equal(parsed[0].portal,'https://eyesonflock.com/portal/demo-agency-0');
assert.ok(!parsed[0].portal.includes('camera'));
dataset.features[1].properties.portalSlug=dataset.features[0].properties.portalSlug;
assert.throws(()=>source.parseNodes(dataset,meta),/Duplicate or invalid/);
dataset.features[1].properties.portalSlug='demo-agency-1';
dataset.features[1].geometry.coordinates=[-95,120];
assert.throws(()=>source.parseNodes(dataset,meta),/outside supported region/);
console.log('VENDOR PORTAL AGENCY MAP PASS: regional agency nodes only, no hardware location claims');
