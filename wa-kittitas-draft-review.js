/* Four-page Kittitas government-listed DRAFT, visually reviewed; not adopted policy. */
(function(root,factory){'use strict';const API=factory();if(typeof module==='object'&&module.exports)module.exports=API;if(root)root.KatoptronKittitasDraftReview=API;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const ORIGINAL='https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Kittitas%20PD%20Policy.pdf?VersionId=kFMGZo4zqUbzsCu9cSrAdpkD1Ij.PutG';
 const SHA='8b6bb93e69589f7459cb4bc5adbd7991043e59687fa1b91180c149e5fc19368f';
 const PNGS=["f6bb7be5fa56fa23867b642e838b242b4d8c0e83bfc0294648821c437348eb89","1c1616914aea9641d7d4cc538d6c3426a027fe96dccffe35b068ab15942f9b1d","f6ce5574d6ef7556aa7838b0e319130971cfb2831feec00ddc422e987faeb407","1a91463fe3c239b4e62d54407988d7ff40a01efb1eed3e2b3ed288f94fc93065"];
 const CATEGORIES=['draft_not_adopted_and_flock_training_reference','draft_default_retention_and_prohibited_uses','draft_internal_audit_and_access_rules','draft_data_release_request_approval'];
 function review(d,registry,held){
  const ago=registry.find(r=>r.agency_name==='Kittitas Police Department');
  const h=held.find(r=>r.agency_name==='Kittitas Police Department');
  if(!d||d.schema_version!==1||d.agency_name!=='Kittitas Police Department'||d.state!=='WA'||
   d.source_registry_url!=='https://www.atg.wa.gov/ALPR'||
   d.source_url!==ORIGINAL||ago?.policy_links_from_official_ago_page?.length!==1||
   ago.policy_links_from_official_ago_page[0]!==ORIGINAL||h?.source_url!==ORIGINAL||
   h.sha256_complete_original!==SHA||d.original_sha256!==SHA||
   d.document_lifecycle!=='draft_not_proven_adopted'||d.manual_imprint_date!=='2026-06-30'||
   d.original_page_count!==4||d.original_page_review_method!=='visually_inspected_original_sha256_pinned_raster_render'||
   !Array.isArray(d.reviewed_pages)||d.reviewed_pages.join(',')!=='1,2,3,4'||
   !Array.isArray(d.page_png_sha256)||d.page_png_sha256.length!==4||
   d.page_png_sha256.some((hash,i)=>hash!==PNGS[i])||
   !Array.isArray(d.findings)||d.findings.length!==4||
   d.findings.some((f,i)=>f.page!==i+1||f.category!==CATEGORIES[i]||
      typeof f.statement!=='string'||f.statement.length<100||f.statement.length>800)||
   typeof d.limits!=='string'||!d.limits.includes('Every original page is labeled DRAFT')||
   ['adopted','confirmed_vendor','camera_coordinates','operational_status','camera_count'].some(k=>Object.hasOwn(d,k)))
   throw Error('Unverified or improperly promoted Kittitas draft policy evidence');
  return d;
 }
 return {review};
});