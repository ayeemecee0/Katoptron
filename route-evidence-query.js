/* Exact-count, complete government GIS corridor acquisition.
 * Never certify an observation count from a truncated PostgREST response.
 * No browser persistence or location logging. */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronRouteEvidence=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const PAGE_LIMIT=1000,MAX_QUERIES=240,MAX_RECORDS=40000;
 const MIN_SPLIT_SPAN=0.00015;
 function exactCount(header,rows){
  if(!Array.isArray(rows)||rows.length>PAGE_LIMIT ||
     typeof header!=='string')throw Error('Route source completeness proof unavailable');
  const match=/^(?:(\d+)-(\d+)|\*)\/(\d+)$/.exec(header.trim());
  if(!match)throw Error('Route source exact-count header missing; evidence UNKNOWN');
  const total=Number(match[3]);
  if(!Number.isSafeInteger(total)||total<rows.length)
   throw Error('Route source invalid exact row count');
  if(rows.length){
   if(match[1]===undefined||Number(match[1])!==0||
      Number(match[2])!==rows.length-1)
    throw Error('Route source returned an incomplete range');
  }else if(total!==0){
   throw Error('Route source returned empty partial range');
  }
  return total;
 }
 function split(box){
  const lat=box.north-box.south,lon=box.east-box.west;
  if(!Number.isFinite(lat)||!Number.isFinite(lon)||lat<0||lon<0||
    (lat<=MIN_SPLIT_SPAN&&lon<=MIN_SPLIT_SPAN))
   throw Error('Camera point density exceeds a fully verifiable corridor');
  const scaledLon=lon*Math.cos((box.north+box.south)*Math.PI/360);
  if(lat>=scaledLon&&lat>MIN_SPLIT_SPAN){
   const mid=(box.north+box.south)/2;
   return [{...box,north:mid},{...box,south:mid}];
  }
  if(lon<=MIN_SPLIT_SPAN)
   throw Error('Camera point density exceeds a fully verifiable corridor');
  const mid=(box.west+box.east)/2;
  return [{...box,east:mid},{...box,west:mid}];
 }
 async function collect(route,geo,fetchPages,eligible,signal,options={}){
  if(!route||!Array.isArray(route.points)||!geo?.corridorBoxes||
     typeof fetchPages!=='function'||typeof eligible!=='function')
   throw Error('Route or source evidence scan unavailable');
  const queue=geo.corridorBoxes(route.points);
  const maxQueries=options.maxQueries||MAX_QUERIES;
  if(!Number.isInteger(maxQueries)||maxQueries<1||maxQueries>MAX_QUERIES)
   throw Error('Invalid bounded government route query budget');
  let queries=0,splitRegions=0,checkedRegions=0;
  const collected=new Map(),identities=new Map();
  while(queue.length){
   if(signal?.aborted)throw Error('Route evidence request canceled');
   if(queries>=maxQueries)throw Error('Government route scan exceeds safe evidence query budget');
   const box=queue.shift();
   const res=await fetchPages(box,signal);
   queries++;
   if(!res||!Array.isArray(res.official?.rows)||!Array.isArray(res.tiered?.rows)||
     !Number.isSafeInteger(res.official.total)||!Number.isSafeInteger(res.tiered.total)||
     res.official.total<res.official.rows.length||res.tiered.total<res.tiered.rows.length)
    throw Error('Full original source row counts unavailable');
   if(res.official.total>res.official.rows.length||
      res.tiered.total>res.tiered.rows.length){
    const more=split(box);
    queue.unshift(...more);
    splitRegions++;
    if(queue.length+queries>maxQueries)
     throw Error('Source corridor subdivision exceeds safe query budget');
    continue;
   }
   checkedRegions++;
   for(const row of [...res.official.rows,...res.tiered.rows]){
    if(!row||typeof row.record_key!=='string'||!row.record_key||
      !Number.isFinite(Number(row.latitude))||
      !Number.isFinite(Number(row.longitude)))
     throw Error('Government route scan returned malformed source location');
    // Even ineligible generic/provisional records must be checked against
    // earlier copies. A concurrent Flock-to-generic source change cannot
    // leave an earlier optimistic row in a completed comparison.
    const identity=[Number(row.latitude),Number(row.longitude),
      row.source_url||'',row.source_flock_label_status||'',
      row.evidence_tier||'',row.verification_status||''].join('|');
    const previous=identities.get(row.record_key);
    if(previous!==undefined&&previous!==identity)
     throw Error('Conflicting original source identity across route regions');
    identities.set(row.record_key,identity);
    if(!eligible(row))continue;
    collected.set(row.record_key,row);
    if(collected.size>MAX_RECORDS)
     throw Error('Government route evidence exceeds safe full-corridor capacity');
   }
  }
  if(signal?.aborted)throw Error('Route evidence request canceled');
  return {records:[...collected.values()],queries,checkedRegions,splitRegions};
 }
 return Object.freeze({exactCount,split,collect,PAGE_LIMIT,MAX_QUERIES});
});
