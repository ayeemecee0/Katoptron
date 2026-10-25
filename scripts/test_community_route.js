const assert=require('node:assert/strict');
const community=require('../community-route.js');
const Geo=require('../route-geometry.js');
const route={points:[[38.50,-121.50],[38.50,-121.49]]};
function osm(id,lat,lon){return {osm_key:'node/'+id,latitude:lat,longitude:lon}}
function official(lat,lon){return {record_key:'gov-1',latitude:lat,longitude:lon,location_accuracy:'exact'}}
const first=osm(1,38.50,-121.495);
const second=osm(2,38.50,-121.49505);
const far=osm(3,38.55,-121.495);
let r=community.summarize(route,[first,first,second,far],
 [official(38.50,-121.495)],Geo,true);
assert.equal(r.communityNearRoute,2,'OSM IDs must deduplicate across corridor boxes');
assert.equal(r.possibleOverlaps,2,'Two community observations close to government coordinate remain ambiguous');
assert.equal(r.proximityMeters,120);
assert.equal(r.overlapMeters,30);
assert.equal(r.uniqueMappedCoordinates,2);
assert.equal(r.colocatedExtraObservations,0);
const same=community.summarize(route,[first,osm(7,38.50,-121.495)],[],Geo,false);
assert.equal(same.communityNearRoute,2);
assert.equal(same.uniqueMappedCoordinates,1);
assert.equal(same.colocatedExtraObservations,1,'Same coordinate OSM IDs are observations, not two confirmed cameras');
r=community.summarize(route,[first],[],Geo,false);
assert.equal(r.communityNearRoute,1);
assert.equal(r.possibleOverlaps,null,'Unavailable official evidence must remain unknown, not zero');
r=community.summarize(route,[first],[official(38.54,-121.495)],Geo,true);
assert.equal(r.possibleOverlaps,0,'Non-proximate government point does not match community observation');
assert.throws(()=>community.summarize(route,[osm('bad',38.5,-121.495)],[],Geo,true),/Malformed/);
assert.throws(()=>community.summarize(null,[first],[],Geo,false),/incomplete/);
async function runAdaptiveTests(){
 const dense=Array.from({length:1000},()=>first);
 const visited=[];
 const filled=await community.scanRoute(route,Geo,async box=>{
  visited.push(box);
  if(visited.length===1)return {rows:dense,total:1001}; // HTTP row cap hides one original item
  return {rows:[first,second],total:2}; // Duplicate OSM IDs dedupe across adjacent boxes
 },new AbortController().signal);
 assert.ok(visited.length>=3,'Dense cell should be split into complete smaller boxes');
 assert.equal(filled.records.length,2);
 const result=community.summarize(route,filled.records,[],Geo,false);
 assert.equal(result.communityNearRoute,2);
 assert.equal(result.possibleOverlaps,null);
 assert.throws(()=>community.splitBox({
  south:38.50000,north:38.50005,west:-121.50000,east:-121.49995
 }),/too dense/);
 let calls=0;
 await assert.rejects(()=>community.scanRoute(route,Geo,async()=>{
  calls++;return {rows:dense,total:1001};
 },new AbortController().signal),/dense|budget/i);
 assert.ok(calls<250,'Dense unresolvable corridor should fail closed at budget');
 await assert.rejects(()=>community.scanRoute(route,Geo,
  async()=>({rows:[first],total:null}),new AbortController().signal),
  /exact-count proof/);
 await assert.rejects(()=>community.scanRoute(route,Geo,
  async()=>({rows:[first],total:0}),new AbortController().signal),
  /exact-count proof/);
 const controller=new AbortController();controller.abort();
 await assert.rejects(()=>community.scanRoute(route,Geo,
  async()=>{throw Error('Should never fetch when canceled')},controller.signal),/cancelled/);
 assert.equal(community.format({status:'unavailable'},
  {status:'complete'}).includes('UNKNOWN'),true);
 assert.equal(community.format({status:'complete',
  summary:{communityNearRoute:0,possibleOverlaps:null}},
  {status:'unavailable'}).includes('overlaps unknown'),true);
 console.log('Community route adaptive queries, deduplication, cancellation and fail-closed budget PASS');
}
runAdaptiveTests().catch(error=>{console.error(error);process.exitCode=1});
