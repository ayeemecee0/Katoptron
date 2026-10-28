/* Secondary FBI-derived ORI agency roster state aggregation. This is NOT
 * a verified, current roster of operating police agencies or Flock programs.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronORICoverage=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const STATES='AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split(' ');
 const SHA='66e2bbe4e78b92c929a615b8be0f713d3ea8d780c25be541c3ddadeb0ebc792a';
 function validate(data){
  if(!data||data.schema_version!==1||data.reviewed_on!=='2026-10-27'||
     data.scope!=='51_US_state_FBI_CDE_derived_ori_agency_research_entries_secondary_not_current_law_enforcement_authority'||
     data.source_url!=='https://iropo.org/data/agencies.csv'||
     data.original_csv_sha256!==SHA||
     data.federal_source_reference!=='FBI Crime Data Explorer /agency/byStateAbbr/{state}'||
     !Array.isArray(data.state_counts)||data.state_counts.length!==51||
     data.research_agency_entries!==19636||
     data.statewide_agency_roster_currently_operating_verified!==0||
     data.original_FBI_agency_source_directly_reviewed!==false||
     data.verified_flock_deployments_added!==0||
     data.current_ALPR_policies_added!==0||
     data.live_camera_coordinates_added!==0||
     typeof data.limitations!=='string'||data.limitations.length<160)
   throw Error('Secondary ORI directory claims or original checksum unverified');
  const counts=new Map();
  for(const item of data.state_counts){
   if(!STATES.includes(item.state)||counts.has(item.state)||
      !Number.isInteger(item.count)||item.count<1||item.count>1700)
    throw Error('FBI-derived state ORI count invalid or duplicated');
   counts.set(item.state,item.count);
  }
  if(counts.size!==51||[...counts.values()].reduce((a,b)=>a+b,0)!==19636)
   throw Error('51-state ORI directory total does not reconcile');
  return Object.freeze({states:51,count:19636,byState:counts,
   census_match_verified:false,flock_deployments_verified:0,
   warning:'FBI-derived CC0 secondary ORI research records, not a current police agency census, not government verification of each identity, and NOT Flock installations or current policies.',
   source_run_url:data.source_run_url});
 }
 return Object.freeze({validate,STATES});
});
