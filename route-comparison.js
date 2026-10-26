/* Read-only route comparison: proximity to sourced camera points, NOT a
 * predicted detection, probability, route safety score or full camera census.
 * Entire requested corridor must have passed evidence checks before calling
 * summarize; a failed API query is handled separately as "unavailable". */
(function (root, factory) {
  const api=factory();
  if(typeof module!=='undefined' && module.exports)module.exports=api;
  if(root)root.KatoptronRouteComparison=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const PROXIMITY_METERS=120;
  // City police GIS confirms these 23 map positions as generic LPR Camera,
  // not individually identifiable Flock-manufactured equipment. Still display
  // them on the official-source map but exclude from Flock-only route evidence.
  const GENERIC_CITY_LPR_LAYER='https://services9.arcgis.com/xdpiCgT89eSIEpbi/arcgis/rest/services/LiveOakCameras/FeatureServer/0';
  function eligibleForFlockRoute(record) {
    if(!record||typeof record!=='object')return false;
    if(record.evidence_tier && record.evidence_tier!=='government_verified')return false;
    // Fail closed: government-mapped generic/unknown LPR positions are not
    // Flock-labeled source observations, even if their agency uses Flock.
    if(record.source_flock_label_status!=='source_flock_identified')return false;
    if(record.source_url===GENERIC_CITY_LPR_LAYER)return false;
    if(typeof record.evidence_summary==='string' &&
       /NOT per-device manufacturer/i.test(record.evidence_summary))return false;
    return true;
  }
  function reviewFreshness(record,now=Date.now()) {
    const value=record.last_source_recheck_at||record.last_confirmed_on;
    if(!value||/^\d{4}-\d{2}-\d{2}$/.test(String(value)))return 'unknown';
    const t=Date.parse(value);
    if(!Number.isFinite(t)||t>now+15*60*1000)return 'unknown';
    return now-t>72*3600*1000?'overdue':'recent';
  }
  function summarize(route,records,geo,threshold=PROXIMITY_METERS) {
    if(!route||!Array.isArray(route.points)||!Array.isArray(records)||
       !geo||typeof geo.closestOnRoute!=='function'||
       !Number.isFinite(threshold)||threshold<=0||threshold>1000)
      throw new Error('Cannot compare incomplete sourced route evidence');
    let nearby=0,approx=0,overdue=0,unknown=0;
    const ids=new Set();
    for(const r of records){
      if(!r||!Number.isFinite(Number(r.latitude))||
         !Number.isFinite(Number(r.longitude)))throw new Error('Invalid source coordinate');
      const key=r.record_key||r.case_key;
      if(!key||ids.has(key))continue;
      ids.add(key);
      // GIS-documented generic LPR, independent provisional and
      // source-attributed-unconfirmed entries never become Flock route matches.
      if(!eligibleForFlockRoute(r))continue;
      const distance=geo.closestOnRoute(
        [Number(r.latitude),Number(r.longitude)],route.points).distance;
      if(r.location_accuracy==='exact'&&distance<=threshold){
        nearby++;
        const status=reviewFreshness(r);
        if(status==='overdue')overdue++;
        if(status==='unknown')unknown++;
      }else if(r.location_accuracy==='approximate'&&
        Number.isFinite(Number(r.uncertainty_radius_m))&&
        distance<Number(r.uncertainty_radius_m)+1000){
        approx++;
      }
    }
    return Object.freeze({nearby,approx,overdue,unknown,threshold});
  }
  return Object.freeze({summarize,reviewFreshness,eligibleForFlockRoute,PROXIMITY_METERS});
});
