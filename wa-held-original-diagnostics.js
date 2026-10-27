/* Original WA AGO policy source structural holds. Not policy content evidence. */
(function(root,factory){'use strict';const API=factory();
 if(typeof module==='object'&&module.exports)module.exports=API;
 if(root)root.KatoptronWAHeldSourceDiagnostics=API;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const KNOWN={
  "Kelso Police Department": {
    "sha": "2e4bcf1b3d69598522b5e5c0adfd857e1c81e63c9ba6f5e04b818ede2e246e3f",
    "pages": 2,
    "bytes": 1343224,
    "diagnosis": "empty_page_content_streams",
    "intake": "held_unreadable_pdf"
  },
  "Kirkland Police Department": {
    "sha": null,
    "pages": null,
    "bytes": null,
    "diagnosis": "original_pdf_exceeds_16_mb_diagnostic_cap",
    "intake": "held_non_pdf"
  },
  "Kittitas Police Department": {
    "sha": "8b6bb93e69589f7459cb4bc5adbd7991043e59687fa1b91180c149e5fc19368f",
    "pages": 4,
    "bytes": 2987409,
    "diagnosis": "strict_parser_fails_image_pdf_lenient_only",
    "intake": "held_unreadable_pdf"
  },
  "Northwest Seaport Alliance": {
    "sha": "1ccad75475b18a9e464979a472ac09b043a439d57221bf92c890523d05110894",
    "pages": null,
    "bytes": 286691,
    "diagnosis": "pdf_reader_dependency_unresolved",
    "intake": "held_unreadable_pdf"
  },
  "Puyallup Police Department": {
    "sha": "91135363ac40afc96f27b4a06669b2df6fbf006122d1a29fca35489db8cb053a",
    "pages": 2,
    "bytes": 1266733,
    "diagnosis": "empty_page_content_streams",
    "intake": "held_unreadable_pdf"
  },
  "Wapato Police Department": {
    "sha": "84782bbcdf4df906c1ff27204cf7ba59aa34db76c7b8f7e35137a753e7162b44",
    "pages": 4,
    "bytes": 2570228,
    "diagnosis": "empty_page_content_streams",
    "intake": "held_unreadable_pdf"
  },
  "Yakima Police Department": {
    "sha": "060651f5e5fb35dee642a2caf3ba386395aed3265264c0a3c8a924ce34b1530e",
    "pages": 738,
    "bytes": 3920685,
    "diagnosis": "manual_exceeds_160_page_triage_cap",
    "intake": "held_unreadable_pdf"
  }
};
 function catalog(raw,registrations,triageRows){
  if(!raw||raw.schema_version!==1||raw.source_registry!=='https://www.atg.wa.gov/ALPR'||
     typeof raw.limits!=='string'||!raw.limits.includes('does not authenticate page policy content')||
     !Array.isArray(raw.entries)||raw.entries.length!==7||
     !Array.isArray(registrations)||!Array.isArray(triageRows))
   throw Error('Unverified WA original policy diagnostic manifest');
  const official=new Map(registrations.map(x=>[x.agency_name,x]));
  const receipts=new Map(triageRows.map(x=>[x.agency_name,x]));
  const seen=new Set();
  for(const r of raw.entries){
   const x=Object.hasOwn(KNOWN,r?.agency_name)?KNOWN[r.agency_name]:null;
   const src=official.get(r?.agency_name),t=receipts.get(r?.agency_name);
   if(!x||seen.has(r.agency_name)||r.state!=='WA'||!src||!t||
      src.policy_links_from_official_ago_page?.length!==1||
      src.policy_links_from_official_ago_page[0]!==r.source_url||
      t.policy_source_url!==r.source_url||t.inspection_status!==x.intake||
      r.original_intake_status!==x.intake||r.diagnosis!==x.diagnosis||
      r.sha256_complete_original!==x.sha||
      r.page_count_structurally_readable!==x.pages||
      r.bytes_complete_original!==x.bytes||
      r.minimum_observed_bytes!==(r.agency_name==='Kirkland Police Department'?16000001:null)||
      r.policy_page_content_verified!==false||
      r.flock_vendor_confirmed!==false||r.device_location_published!==false||
      typeof r.detail!=='string'||r.detail.length<45||r.detail.length>650||
      ['verified_camera_count','operational_status','flock_camera_coordinates','actual_data_access'].some(k=>Object.hasOwn(r,k)))
    throw Error('WA held source identity or unsupported content claim');
   seen.add(r.agency_name);
  }
  if(seen.size!==7)throw Error('Seven original source diagnostics incomplete');
  return raw.entries.slice().sort((a,b)=>a.agency_name.localeCompare(b.agency_name));
 }
 function label(x){
  const names={
   empty_page_content_streams:'Original PDF pages have no extractable content',
   original_pdf_exceeds_16_mb_diagnostic_cap:'Original PDF exceeds current bounded retrieval limit',
   strict_parser_fails_image_pdf_lenient_only:'Four-page image-based original requires visual review',
   pdf_reader_dependency_unresolved:'PDF reader dependency unresolved',
   manual_exceeds_160_page_triage_cap:'Full policy manual exceeds bounded page guard'
  };
  return names[x]||'Source review held';
 }
 return {catalog,label};
});