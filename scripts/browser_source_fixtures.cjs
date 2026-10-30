'use strict';
/* Deterministic PostgREST response fixtures for browser interaction tests.
 * Real public-source integration is checked independently; these never
 * pretend to be actual camera positions or real government evidence.
 * Test payloads exercise ordering, exact Content-Range, filters and bounds.
 */
const pairRows=Array.from({length:1200},(_,i)=>({
 osm_key_a:'node/'+(1000000001+i),
 osm_key_b:'way/'+(2000000001+i),
 distance_m:i<800?Number((0.25+(i%40)*0.12).toFixed(2)):Number((5.25+(i%40)*0.23).toFixed(2)),
 source_snapshot_date:'2026-10-28'
})).sort((a,b)=>a.distance_m-b.distance_m||
 a.osm_key_a.localeCompare(b.osm_key_a)||a.osm_key_b.localeCompare(b.osm_key_b));
const communityPoint=Object.freeze({osm_key:'node/9988776655',latitude:38.5,longitude:-121.495});
function bounded(rows,searchParams){
 const offset=Number(searchParams.get('offset')||0),limit=Number(searchParams.get('limit')||1000);
 if(!Number.isInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>10000)throw Error('Invalid fixture pagination');
 return {rows:rows.slice(offset,offset+limit),total:rows.length,offset};
}
function narrowedBox(query){
 for(const [dimension,value] of [['latitude',communityPoint.latitude],['longitude',communityPoint.longitude]]){
  for(const clause of query.getAll(dimension)){
   const [operator,bound]=clause.split('.');
   if(operator==='gte'&&value<Number(bound)||operator==='lte'&&value>Number(bound))return false;
  }
 }
 return true;
}
async function install(page){
 const evidence=[];
 await page.route('**/rest/v1/**',async route=>{
  const u=new URL(route.request().url());
  const table=decodeURIComponent(u.pathname.split('/rest/v1/')[1]||'');
  const q=u.searchParams;
  let result=[];
  if(table==='flock_public_osm_nearby_latest'){
   result=[{snapshot_id:'a'.repeat(64),source_snapshot_date:'2026-10-28',
    source_observations:116340,pair_count:1200,source_records_in_pairs:2400,
    pairs_within_5m:800,pairs_5_to_15m:400,source_license:'ODbL-1.0',
    published_at:'2026-10-29T00:00:00Z'}];
  }else if(table==='flock_public_osm_nearby_search'){
   result=pairRows;
   const key=q.get('or')?.match(/osm_key_a\.eq\.((?:node|way)\/\d+)/)?.[1];
   if(key)result=result.filter(row=>row.osm_key_a===key||row.osm_key_b===key);
   const band=q.get('distance_m');
   if(band==='lte.5')result=result.filter(row=>row.distance_m<=5);
   if(band==='gt.5')result=result.filter(row=>row.distance_m>5);
  }else if(table==='flock_public_coverage_stats'){
   result=[{verified_camera_points:293,verified_point_jurisdictions:7,
     verified_area_polygons:0,documented_government_programs:120}];
  }else if(table==='flock_public_osm_community_stats'){
   result=[{reported_flock_points:116340,last_dataset_snapshot_date:'2026-10-28'}];
  }else if(table==='flock_public_osm_latest_quality'){
   result=[{source_snapshot_date:'2026-10-28',osm_observations:116340,
     distinct_coordinates:115000,colocated_extra_observations:1340,osm_edits_older_365d:5000}];
  }else if(table==='flock_osm_community_points'){
   result=narrowedBox(q)?[communityPoint]:[];
  }
  const out=bounded(result,q);
  const range=out.rows.length?out.offset+'-'+(out.offset+out.rows.length-1)+'/'+out.total:'*/'+out.total;
  evidence.push({table,rows:out.rows.length,total:out.total});
  await route.fulfill({status:200,contentType:'application/json',headers:{
   'access-control-allow-origin':'*','access-control-expose-headers':'content-range',
   'content-range':range
  },body:JSON.stringify(out.rows)});
 });
 return evidence;
}
module.exports={install,pairRows,communityPoint};
