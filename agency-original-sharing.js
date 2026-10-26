/* Publisher-cited sharing disclosures, distinct from secondary network links. */
(function(root,factory){const a=factory();if(typeof module!=='undefined'&&module.exports)module.exports=a;if(root)root.KatoptronOriginalSharing=a;})(typeof window!=='undefined'?window:null,function(){
'use strict';
function validate(rows){
 if(!Array.isArray(rows)||rows.length>15000)throw Error('Invalid publisher records');
 const outward=new Map(),inward=new Map(),sources=new Map(),seen=new Set();
 for(const r of rows){
  if(!r||!['original_government','original_flock_vendor_portal'].includes(r.source_kind)
   ||!r.source_key||!r.source_agency_id||!r.recipient_label
   ||!r.source_url?.startsWith('https://')
   ||!r.recipient_observed_on
   ||!['publisher_named_as_of_observation','no_longer_listed','source_unavailable'].includes(r.source_status))
   throw Error('Missing publisher evidence');
  if(Boolean(r.recipient_source_agency_id)!==(r.identity_basis==='exact_source_agency_name'))
   throw Error('Unqualified recipient identity');
  const pair=JSON.stringify([r.source_key,r.recipient_label]);
  if(seen.has(pair))throw Error('Duplicate publisher edge');
  seen.add(pair);
  if(!outward.has(r.source_agency_id))outward.set(r.source_agency_id,[]);
  outward.get(r.source_agency_id).push(r);
  if(r.recipient_source_agency_id){
   if(!inward.has(r.recipient_source_agency_id))inward.set(r.recipient_source_agency_id,[]);
   inward.get(r.recipient_source_agency_id).push(r);
  }
  sources.set(r.source_key,{source_url:r.source_url,source_kind:r.source_kind,captured_scope:r.captured_scope});
 }
 return {outward,inward,sources,records:rows};
}
async function load(){
 const cfg=window.KATOPTRON_CONFIG,rows=[];
 if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey)throw Error('Publisher data unavailable');
 for(let offset=0;offset<15000;offset+=500){
  const q=new URLSearchParams({select:'source_key,source_agency_id,publisher_name,source_url,source_kind,source_section,captured_scope,published_at,source_observed_on,last_successfully_rechecked_at,recipient_label,recipient_source_agency_id,identity_basis,source_status,recipient_observed_on',limit:'500',offset:String(offset)});
  const res=await fetch(cfg.supabaseUrl+'/rest/v1/flock_public_original_sharing_evidence?'+q,
     {headers:{apikey:cfg.supabasePublishableKey},cache:'no-store'});
  if(!res.ok)throw Error('Publisher records HTTP '+res.status);
  const batch=await res.json();
  if(!Array.isArray(batch))throw Error('Invalid publisher response');
  rows.push(...batch);
  if(batch.length<500)return validate(rows);
 }
 throw Error('Publisher list exceeded page limit');
}
function forAgency(catalog,id,secondary){
 const outbound=catalog?.outward.get(id)||[],inbound=catalog?.inward.get(id)||[];
 const expected=new Set(secondary?.adj?.[id]||[]);
 return {outbound:outbound.map(r=>({...r,alsoSecondary:r.recipient_source_agency_id?
   expected.has(r.recipient_source_agency_id):null})),inbound};
}
return Object.freeze({validate,load,forAgency});
});