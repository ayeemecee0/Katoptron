const assert=require('node:assert/strict');
const D=require('../osm-viewport-density.js');

(async()=>{
 const cfg={supabaseUrl:'https://example.supabase.co',
   supabasePublishableKey:'sb_publishable_testing_only'};
 const box={south:33.7,north:34,west:-84.5,east:-84.2};
 const original={cell_latitude:33.725,cell_longitude:-84.475,
   community_report_count:3,example_latitude:33.7227682,
   example_longitude:-84.4643306};
 let endpoint;
 const request=async(url)=>{
  endpoint=url;
  return {ok:true,json:async()=>[original]};
 };
 const got=await D.fetchCells(cfg,box,12,3,null,request);
 assert.equal(got.total,3);
 assert.equal(got.cell,0.05);
 assert.equal(got.rows[0].example_latitude,33.7227682,
   'Cluster anchor is original-source geometry, not artificial cell center');
 assert.ok(endpoint.includes('/flock_public_osm_viewport_density_with_anchor?'),
   'Client must use source-anchored RPC rather than geometric center-only RPC');
 async function mustFail(row,regex){
  await assert.rejects(D.fetchCells(cfg,box,12,3,null,async()=>({
   ok:true,json:async()=>[row]
  })),regex);
 }
 await mustFail({...original,example_latitude:33.6},/source-anchor/);
 await mustFail({...original,example_longitude:-84.40},/source-anchor/);
 await mustFail({...original,community_report_count:2},/reconcile/);
 await mustFail({...original,example_latitude:null},/source-anchor/);
 assert.throws(()=>D.cellForZoom(9),/zoom invalid/);
 console.log('COMMUNITY DENSITY ANCHOR PASS: actual OSM source positions, no invented center pins');
})().catch(e=>{console.error(e);process.exitCode=1});
