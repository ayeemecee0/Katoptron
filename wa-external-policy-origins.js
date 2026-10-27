/* Original AGO-linked external sources: source acquisition only, no policy facts. */
(function(root,factory){'use strict';const API=factory();if(typeof module==='object'&&module.exports)module.exports=API;if(root)root.KatoptronWAExternalOrigins=API;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const STATES=new Set(['original_pdf_text_detected','original_pdf_image_only','original_html_text_detected',
 'held_redirect','held_http_error','held_unreachable','held_oversized','held_empty_or_unusable','held_invalid_pdf','held_unsupported_content']);
 const HOSTS=new Set(["blackdiamondwa.gov","www.cwu.edu","www.cpwa.us","www.douglascountysheriff.org","www.eastwenatcheewa.gov","inside.ewu.edu","www.ellensburgwa.gov","www.cityofenumclaw.net","www.everettwa.gov","www.grandview.wa.us","public.powerdms.com","www.co.kittitas.wa.us","www.libertylakewa.gov","www.cityofmontesano.com","www.pasco-wa.gov","selahwa.gov","www.soundtransit.org","uniongapwa.gov","www.washington.edu","transportation.wsu.edu","transportation.wwu.edu"]);
 function exact(url){
  if(typeof url!=='string'||url.length>1200)return false;
  try{const p=new URL(url);
   return p.protocol==='https:'&&HOSTS.has(p.hostname)&&p.host===p.hostname&&
    !p.username&&!p.password&&!p.hash&&!p.pathname.includes('..')&&
    !/%2e|\\/i.test(p.pathname)&&p.search.length<142;
  }catch{return false;}
 }
 function catalog(data,registrations){
  if(!data||data.schema_version!==1||data.source_registry_url!=='https://www.atg.wa.gov/ALPR'||
   data.scope!=='external_source_metadata_only_no_policy_facts'||
   typeof data.notes!=='string'||!data.notes.includes('does not establish')||
   !Array.isArray(registrations)||!Array.isArray(data.receipts))throw Error('Unreviewed external source index');
  const expected=[];
  for(const reg of registrations){
   for(const url of reg.policy_links_from_official_ago_page||[]){
    if(url.startsWith('https://agportal-s3bucket.s3.us-west-2.amazonaws.com/'))continue;
    if(!exact(url))throw Error('Untrusted external URL in state registry');
    expected.push({agency:reg.agency_name,url,date:reg.submitted_on});
   }
  }
  expected.sort((a,b)=>a.agency.localeCompare(b.agency));
  if(data.receipts.length!==expected.length||expected.length!==25)throw Error('AGO external linked source count changed');
  const rows=[],counts={retrieved:0,held:0,pdf:0,html:0};
  for(let i=0;i<expected.length;i++){
   const x=data.receipts[i],want=expected[i];
   if(!x||x.agency_name!==want.agency||x.policy_source_url!==want.url||
    x.submitted_on!==want.date||!STATES.has(x.inspection_status)||
    ['manufacturer_identity_assertion','installed_equipment_assertion','agency_compliance_assertion','camera_coordinates_assertion'].some(k=>x[k]!==false)||
    !Array.isArray(x.page_mentions_flock))throw Error('External provenance or unsupported published fact');
   const retrieved=x.inspection_status.startsWith('original_');
   if(retrieved){
    if(!/^[a-f0-9]{64}$/.test(x.content_sha256||'')||
     !Number.isInteger(x.bytes)||x.bytes<100||x.bytes>8000000)throw Error('Original source byte provenance invalid');
    if(x.inspection_status.startsWith('original_pdf')){
     if(!Number.isInteger(x.page_count)||x.page_count<1||x.page_count>160||
      x.page_mentions_flock.some(n=>!Number.isInteger(n)||n<1||n>x.page_count))throw Error('Source PDF page provenance invalid');
     counts.pdf++;
    }else{
     if(x.page_count!==null||x.page_mentions_flock.some(n=>n!==0))throw Error('HTML cannot imply PDF pages');
     counts.html++;
    }
    counts.retrieved++;
   }else{
    if(x.content_sha256!==null||x.bytes!==null||x.page_count!==null||x.page_mentions_flock.length)throw Error('Held original cannot be source verified');
    counts.held++;
   }
   rows.push(x);
  }
  return {rows,counts,total:rows.length,uniqueLinks:new Set(rows.map(x=>x.policy_source_url)).size};
 }
 function label(status){
  const labels={
   original_pdf_text_detected:'Exact linked PDF retrieved, with readable text; policy not individually reviewed',
   original_pdf_image_only:'Exact linked scanned PDF retrieved; page review remains separate',
   original_html_text_detected:'Linked web page retrieved; policy text not individually verified',
   held_redirect:'Government-linked page redirects; original destination not qualified',
   held_http_error:'Source server refused the original request',
   held_unreachable:'Source unavailable to strict retrieval',
   held_oversized:'Source exceeds bounded retrieval or extraction cap',
   held_empty_or_unusable:'Page retrieved but usable content not established',
   held_invalid_pdf:'PDF cannot be safely or completely parsed',
   held_unsupported_content:'Original returned unsupported content'
  };
  return labels[status]||'Unverified source status';
 }
 return {exact,catalog,label};
});