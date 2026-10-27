/* Strict reviewed document identities; source-date findings are not current-camera facts. */
(function(root,factory){'use strict';const API=factory();
 if(typeof module==='object'&&module.exports)module.exports=API;
 if(root)root.KatoptronWAReviewedFlockSources=API;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const EXPECTED={
  "arlington-wa-fleet-policy-2026": {
    "agency": "Arlington Police Department",
    "kind": "agency_alpr_policy",
    "imprint": "2026-03-30",
    "sha": "bb2a0bfb0f4423ed19c23f6adf882b0d7263901fb937e638241c1bb4e1606d79",
    "pages": 9,
    "reviewed": [
      1
    ],
    "categories": [
      "policy_scope_multiple_system_types"
    ],
    "findingPages": [1]
  },
  "des-moines-wa-flock-search-policy-2026": {
    "agency": "Des Moines Police Department",
    "kind": "agency_alpr_policy",
    "imprint": "2026-07-08",
    "sha": "222f7d012e07248f298b611611e8acec3ca07d368e2dcaefae59054c26e527cb",
    "pages": 6,
    "reviewed": [
      3
    ],
    "categories": [
      "policy_flock_search_accountability"
    ],
    "findingPages": [3]
  },
  "federal-way-wa-bulletin-2026": {
    "agency": "Federal Way Police Department",
    "kind": "agency_training_bulletin",
    "imprint": "2026-05-15",
    "sha": "7dfed7573cb481965d3381d6886222c8b8701ad824dad64135a544cee5261df5",
    "pages": 4,
    "reviewed": [
      2
    ],
    "categories": [
      "agency_reported_historical_installed_inventory",
      "agency_proposal_distinct_from_installation"
    ],
    "findingPages": [2,2]
  },
  "mukilteo-wa-flock-retention-policy-2026": {
    "agency": "Mukilteo Police Department",
    "kind": "agency_alpr_policy",
    "imprint": null,
    "sha": "9889a6a207843c67cdabc62db674892e55de58cb5418dde27eb9de25c458a68b",
    "pages": 7,
    "reviewed": [
      6
    ],
    "categories": [
      "policy_vendor_hosting_and_retention"
    ],
    "findingPages": [6]
  },
  "prosser-wa-flock-transparency-policy-2026": {
    "agency": "Prosser Police Department",
    "kind": "agency_alpr_policy",
    "imprint": "2026-05-13",
    "sha": "c597c9edeeb78ffca4c737be2c475ca0f697a37dd72805414144e3bd5e88347e",
    "pages": 2,
    "reviewed": [
      2
    ],
    "categories": [
      "policy_future_transparency_portal"
    ],
    "findingPages": [2]
  },
  "sedro-woolley-wa-flock-policy-2026": {
    "agency": "Sedro-Woolley Police Department",
    "kind": "agency_alpr_policy",
    "imprint": "2026-06-18",
    "sha": "4778f1f07f139658be0306edbb5049b1036e2a91ae22175bbcbd18c31c82c3b6",
    "pages": 10,
    "reviewed": [
      4,
      5
    ],
    "categories": [
      "policy_flock_query_requirements",
      "policy_internal_retention_language_conflict"
    ],
    "findingPages": [4,5]
  },
  "walla-walla-wa-flock-policy-2026": {
    "agency": "Walla Walla Police Department",
    "kind": "agency_alpr_policy",
    "imprint": "2026-09-16",
    "sha": "6a64c055386a085c667e17d5003c0b51247911a27d2bbc9802a3649ff6b61ca5",
    "pages": 6,
    "reviewed": [
      3
    ],
    "categories": [
      "policy_transparency_reporting_plan"
    ],
    "findingPages": [3]
  },
  "whitman-wa-flock-system-policy-2026": {
    "agency": "Whitman County Sheriff's Office",
    "kind": "agency_alpr_policy",
    "imprint": null,
    "sha": "7c826c6f2dfaf2c0fe754e01f2329e9754a39d3583a1898e0c1aa093699e5465",
    "pages": 6,
    "reviewed": [
      1,
      4
    ],
    "categories": [
      "policy_explicit_flock_system_title_and_fixed_only",
      "policy_retention_and_sharing_limits"
    ],
    "findingPages": [1,4]
  }
};
 const HELD_AGENCY="Sultan Police Department";
 function catalog(data,registry,receipts){
  if(!data||data.schema_version!==1||!Array.isArray(data.documents)||
     data.documents.length!==8||!Array.isArray(registry)||!Array.isArray(receipts)||
     typeof data.scope_limits!=='string'||!data.scope_limits.includes('not vendor or field-audited')||
     !Array.isArray(data.held_review_candidates)||data.held_review_candidates.length!==1)
    throw Error('Unverified AGO original source review catalog');
  const hold=data.held_review_candidates[0];
  if(hold.registry_agency!==HELD_AGENCY||
     hold.status!=='held_original_document_publisher_identity_mismatch'||
     hold.publish_document_page_links!==false||
     hold.observed_document_heading!=="Snohomish County Sheriff's Office ALPR Training")
    throw Error('Original agency mismatch cannot be auto-promoted');
  const byReg=new Map(registry.map(r=>[r.agency_name,r]));
  const byReceipt=new Map(receipts.map(r=>[r.agency_name,r]));
  const seen=new Set();
  for(const r of data.documents){
   const x=r&&Object.prototype.hasOwnProperty.call(EXPECTED,r.id)?EXPECTED[r.id]:null;
   const reg=byReg.get(r?.agency_name),source=byReceipt.get(r?.agency_name);
   if(!x||seen.has(r.id)||!reg||!source||r.agency_name!==x.agency||
      r.state!=='WA'||r.policy_kind!==x.kind||r.document_imprint_date!==x.imprint||
      r.page_count!==x.pages||r.content_sha256!==x.sha||
      r.source_tier!=='individual_page_review_of_agency_submitted_original_policy_or_bulletin'||
      r.ago_registration_date!==reg.submitted_on||
      !Array.isArray(reg.policy_links_from_official_ago_page)||
      reg.policy_links_from_official_ago_page.length!==1||
      reg.policy_links_from_official_ago_page[0]!==r.source_url||
      source.policy_source_url!==r.source_url||source.sha256!==r.content_sha256||
      source.page_count!==r.page_count||source.inspection_status!=='exact_pdf_text_detected'||
      !Array.isArray(r.pages_reviewed)||r.pages_reviewed.length!==x.reviewed.length||
      !r.pages_reviewed.every((p,i)=>p===x.reviewed[i])||
      !Array.isArray(r.findings)||r.findings.length!==x.categories.length||
      !r.findings.every((f,i)=>f.page===x.findingPages[i]&&
        x.reviewed.includes(f.page)&&f.category===x.categories[i]&&
        typeof f.statement==='string'&&f.statement.length>=95&&f.statement.length<=650)||
      ['operational_status','camera_coordinates','verified_deployed_camera_count','sharing_edges'].some(k=>Object.hasOwn(r,k)))
    throw Error('Original reviewed policy publisher, page, source receipt or claim type mismatch');
   seen.add(r.id);
  }
  if(seen.size!==8)throw Error('Missing page-reviewed Flock policy original');
  return {documents:data.documents.slice().sort((a,b)=>a.agency_name.localeCompare(b.agency_name)),
   held:data.held_review_candidates[0]};
 }
 return {catalog};
});
