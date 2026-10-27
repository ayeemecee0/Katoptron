/* AGO-linked immutable original PDF triage metadata; NOT publication of vendor,
 * camera, installed location, current sharing, or legal compliance assertions. */
(function(root,factory){'use strict';const API=factory();if(typeof module==='object'&&module.exports)module.exports=API;
 if(root)root.KatoptronWAOriginalSourceTriage=API;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const PREFIX='https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/';
 const STATES=new Set(['exact_pdf_text_detected','exact_pdf_scan_only',
  'held_non_pdf','held_unreadable_pdf','held_unreachable','held_redirect']);
 function exact(url){
  if(typeof url!=='string'||url.length>950||!url.startsWith(PREFIX)||/[\\#]/.test(url))return false;
  const m=/^https:\/\/agportal-s3bucket\.s3\.us-west-2\.amazonaws\.com\/ALPR\/[^?#]+\.pdf\?VersionId=[A-Za-z0-9._-]{12,120}$/.exec(url);
  return !!m&&!/(?:%2e|\.\.)/i.test(url.slice(PREFIX.length,url.indexOf('?')));
 }
 function catalog(data,registrations){
  if(!data||data.schema_version!==1||data.source_registry_url!=='https://www.atg.wa.gov/ALPR'||
     data.scope!=='source_metadata_only_no_automatic_fact_publication'||
     !Array.isArray(data.receipts)||!Array.isArray(registrations)||
     typeof data.warning!=='string'||!data.warning.includes('not independent agency findings'))
   throw Error('Washington AGO source triage provenance invalid');
  const target=[];
  for(const entry of registrations){
   for(const url of entry.policy_links_from_official_ago_page||[]){
    if(exact(url))target.push({agency_name:entry.agency_name,submitted_on:entry.submitted_on,url});
   }
  }
  target.sort((a,b)=>a.agency_name.localeCompare(b.agency_name));
  if(data.receipts.length!==target.length||target.length<1)
   throw Error('Source triage and state-original registry mismatch');
  const byAgency=new Map(),counts={parsed:0,held:0,candidates:0};
  for(let i=0;i<target.length;i++){
   const r=data.receipts[i],t=target[i];
   if(!r||r.agency_name!==t.agency_name||r.policy_source_url!==t.url||r.submitted_on!==t.submitted_on||
      !STATES.has(r.inspection_status)||r.manufacturer_identity_assertion!==false||
      r.camera_coordinates_asserted!==false||byAgency.has(r.agency_name)||
      !Array.isArray(r.potential_flock_term_pages)||r.potential_flock_term_pages.length>160||
      !Number.isInteger(r.searchable_text_pages)||!Number.isInteger(r.scanned_image_pages))
    throw Error('AGO source identity, state or evidence scope tampering detected');
   const parsed=r.inspection_status.startsWith('exact_pdf');
   if(parsed){
    if(!/^[0-9a-f]{64}$/.test(r.sha256||'')||
       !Number.isInteger(r.bytes)||r.bytes<100||r.bytes>8000000||
       !Number.isInteger(r.page_count)||r.page_count<1||r.page_count>160||
       r.searchable_text_pages<0||r.searchable_text_pages>r.page_count||
       r.scanned_image_pages<0||r.scanned_image_pages>r.page_count||
       new Set(r.potential_flock_term_pages).size!==r.potential_flock_term_pages.length||
       r.potential_flock_term_pages.some(p=>!Number.isInteger(p)||p<1||p>r.page_count))
     throw Error('Invalid original PDF source receipt');
    counts.parsed++;
    if(r.potential_flock_term_pages.length)counts.candidates++;
   }else{
    if(r.sha256!==null||r.bytes!==null||r.page_count!==null||
       r.potential_flock_term_pages.length||r.searchable_text_pages!==0||r.scanned_image_pages!==0)
     throw Error('Held source cannot be source-verified');
    counts.held++;
   }
   byAgency.set(r.agency_name,r);
  }
  return {byAgency,counts,total:target.length,receipts:data.receipts.slice()};
 }
 function receiptLabel(r){
  if(!r)return 'Non-versioned or external original policy link; not in the AGO PDF batch';
  if(r.inspection_status==='exact_pdf_text_detected')return 'Original PDF retrieved and searchable; policy statements not automatically verified';
  if(r.inspection_status==='exact_pdf_scan_only')return 'Original PDF retrieved; scanned page review needed';
  return 'Source retrieval held; no extracted findings published';
 }
 return {exact,catalog,receiptLabel};
});
