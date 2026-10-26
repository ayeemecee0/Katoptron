const assert=require('node:assert/strict');
const q=require('../route-evidence-query.js');
const geo=require('../route-geometry.js');
const compare=require('../route-comparison.js');

const path={points:[[38.8,-104.82],[38.8,-104.75]],distance:8000,duration:500};
const camera=(id,lon,kind='source_flock_identified')=>({
 record_key:id,latitude:38.8,longitude:lon,location_accuracy:'exact',
 source_url:'https://agency.gov/gis/FeatureServer/0',
 source_flock_label_status:kind,evidence_tier:null,
 last_source_recheck_at:new Date().toISOString()
});
function empty(){return {rows:[],total:0};}
function page(rows,total=rows.length){return {rows,total};}
async function run(){
 assert.equal(q.exactCount('0-999/1203',Array(1000).fill({})),1203);
 assert.equal(q.exactCount('*/0',[]),0);
 assert.equal(q.exactCount('0-1/2',[{},{}]),2);
 for(const h of ['0-1/*','0-2/2','1-2/2','','*/4']){
  assert.throws(()=>q.exactCount(h,[{},{}]),/exact|range|completeness|invalid/i);
 }
 assert.throws(()=>q.exactCount('0-1000/1001',Array(1001).fill({})),/proof/);

 const strong=camera('flock-on-route',-104.79);
 const generic=camera('generic',-104.79,'generic_lpr');
 const unknown=camera('unknown',-104.79,'unconfirmed');
 const alternate={...camera('tier-1',-104.79),
   source_flock_label_status:undefined,evidence_tier:'government_verified'};
 let calls=0;
 let splitReads=0;
 async function dense(box){
  calls++;
  if(box.east-box.west>0.06){
   splitReads++;
   return {official:page([strong],1001),tiered:empty()};
  }
  return {official:page([strong,generic,unknown]),tiered:page([alternate])};
 }
 const scanned=await q.collect(path,geo,dense,compare.eligibleForFlockRoute);
 assert.ok(splitReads>0);
 assert.ok(calls>splitReads);
 assert.equal(scanned.records.length,1,'Overlapping query regions deduplicated');
 assert.equal(scanned.records[0].record_key,'flock-on-route');
 assert.ok(scanned.splitRegions>0);
 assert.equal(compare.summarize(path,scanned.records,geo).nearby,1);

 let emptyQueries=0;
 const zero=await q.collect(path,geo,async()=>{
  emptyQueries++;return {official:empty(),tiered:empty()};
 },compare.eligibleForFlockRoute);
 assert.equal(zero.records.length,0);
 assert.ok(zero.checkedRegions>0);
 assert.ok(emptyQueries>0);
 await assert.rejects(()=>q.collect(path,geo,async()=>({
   official:page([],17),tiered:empty()
 }),compare.eligibleForFlockRoute,{aborted:false},{maxQueries:1}),
 /completeness|empty|source|budget/i);
 await assert.rejects(()=>q.collect(path,geo,async()=>({
   official:page([],0),tiered:page([alternate],10)
 }),compare.eligibleForFlockRoute,{aborted:false},{maxQueries:2}),
 /budget/i);
 await assert.rejects(()=>q.collect(path,geo,async()=>({
   official:page([strong],1),tiered:page([alternate],0)
 }),compare.eligibleForFlockRoute),/row counts/);
 await assert.rejects(()=>q.collect(path,geo,async()=>({
   official:page([{...strong,latitude:'not a coordinate'}]),tiered:empty()
 }),compare.eligibleForFlockRoute),/malformed/);
 await assert.rejects(()=>q.collect(path,geo,async()=>({
   official:page([strong]),tiered:empty()
 }),compare.eligibleForFlockRoute,{aborted:true}),/canceled/);
 // An initial underreported exact count never becomes a successful result.
 await assert.rejects(()=>q.collect(path,geo,async()=>({
   official:page([strong],0),tiered:empty()
 }),compare.eligibleForFlockRoute),/row counts/);
 // Conflicting source identity for same record key across query boxes is held.
 const trip={points:[[38.8,-104.8],[38.8,-95]],distance:950000,duration:36000};
 let i=0;
 await assert.rejects(()=>q.collect(trip,geo,async()=>{
  i++;
  return {official:page([{...strong,longitude:i===1?-104.79:-103}]),tiered:empty()};
 },compare.eligibleForFlockRoute),/Conflicting/);
 console.log('M4 exact-count route scan passes density subdivision, all-or-unknown semantics, abort, dedup, and positive manufacturer tier guard');
}
run().catch(e=>{console.error(e);process.exitCode=1});
