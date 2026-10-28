/* Original federal geography counts, distinct from Flock or police agency evidence.
 * Source files are Census 2026 ZIPs. Places include CDPs, county subdivisions
 * can be statistical, and overlapping geographies are not distinct governments.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronCensusGeographyCoverage=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const ORIGINALS=Object.freeze([
  ['county','2026_Gaz_counties_national.zip',
   '6a99ca00efbc0be5112e225d4102704c51d5ce3b16e3afd6e4159460595fd12a',3144],
  ['place','2026_Gaz_place_national.zip',
   'af678e2d990827c89ee39b98c82de6e90b693c7361ff0e559ae3076670dd2863',32071],
  ['county_subdivision','2026_Gaz_cousubs_national.zip',
   '9d528b39b70a27075c863b1572f27eadaf24484d5435fac17fc3b4cdd36434c2',35442]
 ]);
 const STATES='AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split(' ');
 const BASE='https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2026_Gazetteer/';
 function validate(raw){
  if(!raw||raw.schema_version!==1||raw.source_year!==2026||
     raw.reviewed_on!=='2026-10-27'||
     raw.scope!=='2026_US_Census_50_states_DC_counties_places_county_subdivisions_not_law_enforcement_agencies'||
     !Array.isArray(raw.sources)||raw.sources.length!==3||
     !Array.isArray(raw.states)||raw.states.length!==51||
     raw.geographic_record_total!==70657||
     raw.complete_law_enforcement_agency_census!==false||
     raw.flock_agencies_verified!==0||
     raw.policy_adoption_claims_added!==0||
     raw.camera_locations_from_geography_added!==0||
     typeof raw.note!=='string'||raw.note.length<150)
    throw Error('Original Census geography research source or evidence scope changed');
  for(let i=0;i<ORIGINALS.length;i++){
   const [kind,name,sha,count]=ORIGINALS[i],s=raw.sources[i];
   if(s.geo_type!==kind||s.url!==BASE+name||
      s.sha256!==sha||s.records!==count)
    throw Error('Original federal ZIP SHA, scope or counts changed');
  }
  const known=new Set(),byState=new Map();
  for(const state of raw.states){
   if(!STATES.includes(state.state)||known.has(state.state)||
      !Number.isInteger(state.counties)||state.counties<1||
      !Number.isInteger(state.places_including_unincorporated_cdps)||
      state.places_including_unincorporated_cdps<0||
      !Number.isInteger(state.county_subdivisions_not_all_governments)||
      state.county_subdivisions_not_all_governments<0||
      state.police_agencies_verified!==0||
      state.flock_programs_verified!==0||
      state.policy_adoptions_verified!==0||
      state.municipal_government_census_complete!==false)
    throw Error('Missing or fabricated state geography census');
   known.add(state.state);byState.set(state.state,{
    state:state.state,counties:state.counties,
    places:state.places_including_unincorporated_cdps,
    subdivisions:state.county_subdivisions_not_all_governments
   });
  }
  if(known.size!==51||!STATES.every(s=>known.has(s))||
     [...byState.values()].reduce((n,x)=>n+x.counties,0)!==3144||
     [...byState.values()].reduce((n,x)=>n+x.places,0)!==32071||
     [...byState.values()].reduce((n,x)=>n+x.subdivisions,0)!==35442||
     raw.counts?.county!==3144||raw.counts?.place!==32071||
     raw.counts?.county_subdivision!==35442)
   throw Error('Original 51-state Census geographic tallies inconsistent');
  return Object.freeze({
   byState,states:51,total:70657,
   counties:3144,places:32071,subdivisions:35442,
   complete_law_enforcement_agency_census:false,
   source_workflow_run:raw.source_workflow_run,
   warning:'Federal geography counts are NOT counts of local government agencies, Flock systems, verified adopted policies, geographic camera points, or unique non-overlapping jurisdictions.'
  });
 }
 return Object.freeze({validate,STATES,ORIGINALS});
});
