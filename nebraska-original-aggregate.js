/* State-filed Nebraska ALPR aggregate is agency-authored, not independent. */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronNebraskaOriginalAggregate=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const URL='https://ncc.nebraska.gov/sites/default/files/Dakota%20County%20FLOCK%20REPORT%202025%20TO%20STATE.pdf';
 const SHA='441961503a77e7838717713448426df07cd59aec4146f92af01830d4e3817eae';
 const PNG='02686973bfb2c942e98624048bdee0f9a3d54b241b2af432211c69506495fb27';
 const METRICS={ncic_confirmed_matches:43,ncic_noncorrelated_matches:0,
  manual_plate_numbers_entered:126,manual_entry_confirmed_matches:19,manual_entry_noncorrelated_matches:1};
 function catalog(raw){
  if(!raw||raw.schema_version!==1||
   raw.scope!=='visually_reviewed_agency_authored_original_aggregate_not_independent_audit_or_flock_device_verification'||
   !Array.isArray(raw.documents)||raw.documents.length!==1||
   !Array.isArray(raw.held_unverified_originals)||raw.held_unverified_originals.length!==1)
   throw Error('Original state aggregate evidence invalid');
  const row=raw.documents[0],held=raw.held_unverified_originals[0];
  if(row.id!=='ne-dakota-county-sheriff-2025-state-alpr-aggregate'||
   row.agency_name!=="Dakota County Sheriff's Office"||
   row.state!=='NE'||row.source_url!==URL||row.source_sha256!==SHA||
   row.source_render_png_sha256!==PNG||row.page_count!==1||row.source_bytes!==136060||
   row.pages_reviewed?.length!==1||row.pages_reviewed[0]!==1||
   row.report_start!=='2025-01-01'||row.report_end!=='2025-12-31'||
   row.original_report_type!=='agency_authored_state_filed_alpr_aggregate'||
   row.vendor_status!=='filename_mentions_flock_actual_equipment_manufacturer_not_proven_by_form'||
   !row.metrics||Object.keys(row.metrics).length!==5||
   Object.entries(METRICS).some(([k,v])=>row.metrics[k]!==v)||
   held.agency_name!=="Buffalo County Sheriff's Office"||
   held.issue!=='source_filename_2025_but_visually_rendered_page_empty_no_numeric_data'||
   held.can_publish_numeric_findings!==false||
   ['verified_flock_hardware','operational_camera_count','camera_coordinates','live_sharing_relationship'].some(k=>Object.hasOwn(row,k)))
   throw Error('Unverified aggregate government report or original page boundary');
  return {document:row,held:held};
 }
 return {catalog};
});