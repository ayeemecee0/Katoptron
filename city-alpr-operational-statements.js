/* Source-dated city-owned ALPR status statements; not live camera telemetry.
   Explicitly separate an announced intended shutdown from a city's retrospective
   operational disablement assertion. No current Flock equipment pins published. */
(function(root,factory){'use strict';const API=factory();
 if(typeof module==='object'&&module.exports)module.exports=API;
 if(root)root.KatoptronCityOperationalStatements=API;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const KNOWN={
  'moline-il-planned-flock-pause-2026':{
   agency:'Moline Police Department',date:'2026-09-15',effective:null,
   classification:'agency_announced_future_deactivation_not_confirmed_completed',
   sha:'7dadb1a974f8021faa4e196ffb8b0a19d6641202bf47089cff41f7dc60fc3048',
   url:'https://www.moline.il.us/1955/License-Plate-Readers',
   anchors:['september 15, 2026','fully deactivated within approximately 14 days']},
  'mill-valley-ca-city-reported-disabled-2026':{
   agency:'City of Mill Valley',date:'2026-10-19',effective:'2026-09-09',
   classification:'city_reports_flock_cameras_already_disabled_as_of_dated_statement',
   sha:'6cb358755f107c9e424ff2f352932bf22513ed0b98145d5012e7a5dff8f4c20b',
   url:'https://www.cityofmillvalley.gov/m/newsflash/home/detail/1639',
   anchors:['october 19, 2026','both the alpr and live-feed cameras have been disabled since september 9, 2026']}
 };
 function source(row){
  const known=row&&Object.prototype.hasOwnProperty.call(KNOWN,row.id)?KNOWN[row.id]:null;
  return known&&known.url===row.source_url?known.url:null;
 }
 function valid(row){
  if(!row||typeof row!=='object'||!source(row))return false;
  const x=KNOWN[row.id];
  return row.agency===x.agency&&row.statement_published_on===x.date&&
   row.effective_as_of===x.effective&&row.classification===x.classification&&
   row.original_html_sha256_at_review===x.sha&&row.evidence_as_of===x.date&&
   Array.isArray(row.source_text_anchors)&&
   row.source_text_anchors.length===2&&row.source_text_anchors.every((a,i)=>a===x.anchors[i])&&
   typeof row.summary==='string'&&row.summary.length>110&&row.summary.length<1100&&
   typeof row.evidence_limit==='string'&&row.evidence_limit.length>55&&
   !('camera_coordinates' in row)&&!('confirmed_live_telemetry' in row)&&
   !('installation_count' in row);
 }
 function catalog(data){
  if(!data||data.schema_version!==1||!Array.isArray(data.documents)||data.documents.length!==2||
   !data.documents.every(valid)||new Set(data.documents.map(d=>d.id)).size!==2||
   typeof data.scope!=='string'||!data.scope.includes('not independent technical tests'))
   throw Error('Unverified government agency operational status statement');
  return data.documents.slice().sort((a,b)=>a.statement_published_on.localeCompare(b.statement_published_on));
 }
 function label(x){
  if(x==='agency_announced_future_deactivation_not_confirmed_completed')
   return 'Planned shutdown; completion not independently established';
  if(x==='city_reports_flock_cameras_already_disabled_as_of_dated_statement')
   return 'City-reported cameras disabled at publication';
  return 'Unverified source status';
 }
 return {catalog,source,valid,label};
});
