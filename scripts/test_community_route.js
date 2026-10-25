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
r=community.summarize(route,[first],[],Geo,false);
assert.equal(r.communityNearRoute,1);
assert.equal(r.possibleOverlaps,null,'Unavailable official evidence must remain unknown, not zero');
r=community.summarize(route,[first],[official(38.54,-121.495)],Geo,true);
assert.equal(r.possibleOverlaps,0,'Non-proximate government point does not match community observation');
assert.throws(()=>community.summarize(route,[osm('bad',38.5,-121.495)],[],Geo,true),/Malformed/);
assert.throws(()=>community.summarize(null,[first],[],Geo,false),/incomplete/);
console.log('Community route proximity and possible-overlap isolation PASS');
