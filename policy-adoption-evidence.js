/* Independently status-typed government HTML evidence.
 * Not part of individually PDF-page-reviewed dossier counts, and not evidence
 * of policy implementation or live Flock operating configurations.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronPolicyAdoptionEvidence=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const ANCHORS=Object.freeze({
  'apache-junction-az-ordinance-1579-adopted-2026-10-06':Object.freeze({
   jurisdiction:'Apache Junction, AZ',state:'AZ',
   decision_type:'municipal_ordinance_adoption',
   status:'adopted_government_original_notice',
   event_date:'2026-10-06',
   source_url:'https://www.apachejunctionaz.gov/999/Public-Notices',
   corroboration_url:'https://www.apachejunctionaz.gov/1241/Public-Safety-Technology'
  }),
  'green-bay-wi-policy-424-draft-still-listed-2026-10-27':Object.freeze({
   jurisdiction:'Green Bay, WI',state:'WI',
   decision_type:'department_policy_publication',
   status:'draft_published_no_adoption_verified',
   event_date:null,
   source_url:'https://www.greenbaywi.gov/1223/Policy-Manual',
   corroboration_url:'https://www.greenbaywi.gov/DocumentCenter/View/19136/DRAFTED-REVISION---Policy-424-Automated-License-Plate-Readers-ALPR-September-2026'
  })
 });
 function exactSource(url,want){
  if(url!==want)return false;
  try{const u=new URL(url);
   return u.protocol==='https:'&&!u.username&&!u.password&&!u.hash;
  }catch{return false;}
 }
 function validate(data){
  if(!data||data.schema_version!==1||
     data.reviewed_on!=='2026-10-27'||
     data.scope!=='selectively_authenticated_government_html_publication_and_ordinance_adoption_status_not_pdf_page_review'||
     !Array.isArray(data.records)||data.records.length!==Object.keys(ANCHORS).length)
   throw Error('Government publication/adoption ledger incomplete or date unverified');
  const ids=new Set();
  const rows=data.records.map(row=>{
   const anchor=ANCHORS[row?.id];
   if(!anchor||ids.has(row.id))throw Error('Unknown or duplicate original government source identity');
   ids.add(row.id);
   for(const field of ['jurisdiction','state','decision_type','status','event_date'])
    if(row[field]!==anchor[field])throw Error('Government action status or source event date was altered');
   if(row.effective_date!==null ||
      !exactSource(row.source_url,anchor.source_url)||
      !exactSource(row.corroboration_url,anchor.corroboration_url)||
      !['city_clerk_adopted_by_council_entry','source_listing_reviewed_on_only'].includes(row.event_date_basis)||
      typeof row.title!=='string'||row.title.length<20||
      typeof row.summary!=='string'||row.summary.length<190||
      typeof row.proof!=='string'||row.proof.length<100||
      typeof row.limits!=='string'||row.limits.length<190)
    throw Error('Government-source action lacks original authority, limits or date basis');
   if(row.status==='adopted_government_original_notice'&&
      (row.event_date_basis!=='city_clerk_adopted_by_council_entry'||
       !/adopted by Council on October 6, 2026/i.test(row.summary)||
       !/effective.date cell blank/i.test(row.limits)))
    throw Error('Ordinance adoption proof/effective date boundary missing');
   if(row.status==='draft_published_no_adoption_verified'&&
      (row.event_date_basis!=='source_listing_reviewed_on_only'||
       !/DRAFTED REVISION/.test(row.proof)||
       !/not of enacted seven.day retention/i.test(row.summary)||
       !/No adopted policy/.test(row.limits)))
    throw Error('Proposed policy must not be promoted to adoption');
   return Object.freeze({...row,
    evidence_category:'official_government_HTML_source_listing_or_clerk_notice',
    reviewed_on:data.reviewed_on,
    source_document_page_reviewed:false});
  });
  if(new Set(rows.map(x=>x.state)).size!==2)
   throw Error('Expected independent state government evidence only');
  return Object.freeze({
   records:rows,
   government_actions_adopted:rows.filter(x=>x.status==='adopted_government_original_notice').length,
   published_unadopted_drafts:rows.filter(x=>x.status==='draft_published_no_adoption_verified').length,
   caveat:'These are exact source-linked government HTML findings, NOT additional individually source-page-reviewed policy PDFs or live system configuration.'
  });
 }
 return Object.freeze({validate,ANCHORS});
});
