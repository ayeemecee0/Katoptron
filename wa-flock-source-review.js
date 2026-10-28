/* Source-pinned PDF page lead index. Keyword hits are NOT Flock deployment claims. */
(function(root,factory){'use strict';const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.KatoptronWAFlockSourceReview=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  function build(triage){
    if(!triage||triage.total!==71||triage.counts?.candidates!==10||
       !Array.isArray(triage.receipts))throw Error('AGO baseline changed; re-review required');
    const matches=triage.receipts.filter(x=>x.potential_flock_term_pages.length>0);
    if(matches.length!==10||new Set(matches.map(x=>x.agency_name)).size!==10)
      throw Error('Duplicate or missing source candidate');
    return matches.map(x=>{
      if(x.inspection_status!=='exact_pdf_text_detected'||
         !/^[0-9a-f]{64}$/.test(x.sha256||'')||
         x.manufacturer_identity_assertion!==false||x.camera_coordinates_asserted!==false)
        throw Error('Source candidate overclassified');
      return Object.freeze({agency:x.agency_name,source:x.policy_source_url,
        hash:x.sha256,pages:x.potential_flock_term_pages.slice(),
        submitted:x.submitted_on,status:'Original PDF contains a Flock Safety text-match candidate; independent adoption and operation unverified'});
    });
  }
  return {build};
});
