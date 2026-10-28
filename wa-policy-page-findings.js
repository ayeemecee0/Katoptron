(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronWAPolicyPages=api;})(typeof window!=='undefined'?window:null,function(){
const KNOWN={
'bonney-lake-wa-flock-transparency-policy':'9951c52f152cad5dc55ab1c1de1c48ebd7326aece40a16ff62845a7b43a4ea97',
'enumclaw-wa-flock-transparency-policy':'9fd0b96b4ada99898bd600fca753a18f90e8c5b34a26ca038411bd38662a9806',
'sultan-wa-sheriff-policy-identity-exception':'b9b84eae00fed2b3f175a880fa2e0be1a17a7d79918ffc4936b991c57da18123'};
function validate(x,receipts){
if(x.schema_version!==1||!Array.isArray(x.documents)||x.documents.length!==3||
 x.agency_policies_with_original_page_claims_verified!==2||x.agency_identity_crosswalk_held!==1||
 x.new_independently_verified_camera_coordinates!==0||x.new_legal_adoptions_verified!==0)
 throw Error('WA policy-page original evidence incomplete');
const known=new Map(receipts.receipts.map(r=>[r.sha256,r])),seen=new Set();
for(const d of x.documents){
 if(!KNOWN[d.id]||KNOWN[d.id]!==d.sha256||seen.has(d.id)||!known.has(d.sha256)||
  known.get(d.sha256).source_url!==d.source_url||d.actual_flock_equipment_verified!==false||
  d.legal_effective_date_verified!==false||!Array.isArray(d.reviewed_pages)||
  !d.reviewed_pages.every(p=>Number.isInteger(p)&&p>=1&&p<=d.original_pdf_pages))
 throw Error('State AGO page review or agency attribution mismatch');
 seen.add(d.id);
}
if(x.documents.filter(d=>d.agency_identity_issue).length!==1||
 x.documents.find(d=>d.agency_identity_issue)?.publisher_actor!=="Snohomish County Sheriff's Office")
 throw Error('Contract sheriff operating identity not reconciled');
return {documents:x.documents,verified_original_page_statements:2,identity_hold:1,new_flock_deployment_claims:0};
}
return {validate};});
