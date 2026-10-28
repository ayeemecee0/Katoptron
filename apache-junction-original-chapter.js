/* Original Apache Junction legal/policy source receipts.
 * Council agenda PDFs do not establish enacted chapter text. The distinct
 * signed City Clerk original has been visually page-reviewed and SHA-pinned.
 * Official schematic never creates exact lat/long camera coordinates.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronApacheOriginalChapter=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const KNOWN=Object.freeze({
  'apache-junction-2026-alpr-chapter-17-legistar-attachment':{
   sha:'ed2411b178181c2bca37e71fcb7c5678ba77f51e7363a6d9f155dc266ac5d724',
   url:'https://apachejunction.legistar.com/View.ashx?GUID=97D4D861-6CFF-42D3-AC9D-B716D9367148&ID=15953709&M=F',
   status:'council_agenda_code_attachment_not_independently_verified_final_enacted_text',
   categories:['alpr_operation','written_retention','sharing_prior_approval','audit_review']
  },
  'apache-junction-2026-ordinance-1579-agenda-unsigned':{
   sha:'11cbba99aafd376b194c112368988c4073acebbd0726abb218d806b27eb11244',
   url:'https://apachejunction.legistar.com/View.ashx?GUID=19063BC4-C37B-4D4C-AE22-194276761219&ID=15974740&M=F',
   status:'unsigned_agenda_ordinance_version_not_proof_of_executed_instrument',
   categories:['adoption_by_reference_proposed','unsigned_template_not_execution']
  }
 });
 const HELD=Object.freeze({
  id:'apache-junction-clerk-ordinance-1579-scanned',
  url:'https://www.apachejunctionaz.gov/DocumentCenter/View/33565/ORD1579',
  sha:'9d4f0ff58b906c65112abd3cf725b00d95e3418a843cd5df0c9e30e9ea9a7e93'
 });
 const SELF=Object.freeze({
  url:'https://apachejunctionaz.gov/1241/Public-Safety-Technology',
  map:'https://apachejunctionaz.gov/DocumentCenter/View/33429',
  cameras:30,retention:30,mapDate:'2026-08-24'
 });
 function pdfPage(url,page){
  if(!Number.isInteger(page)||page<1||page>10)return null;
  try{const u=new URL(url);
   if(u.protocol!=='https:'||u.username||u.password||u.hash)return null;
   u.hash='page='+page;return u.href;
  }catch{return null;}
 }
 function verify(record){
  if(!record||record.schema_version!==1||record.verified_on!=='2026-10-27'||
     record.scope!=='city_original_pdf_page_anchors_and_clerk_visually_reviewed_signed_ordinance_separate_from_source_claims'||
     !Array.isArray(record.source_page_reviewed)||
     record.source_page_reviewed.length!==2||
     !record.signed_original_visually_reviewed||typeof record.signed_original_visually_reviewed!=='object')
    throw Error('Government original-source ledger incomplete');
  const docs=[];const found=new Set();
  for(const d of record.source_page_reviewed){
   const a=KNOWN[d?.id];
   if(!a||found.has(d.id)||d.source_url!==a.url||
      d.pdf_sha256!==a.sha||d.publication_status!==a.status||
      d.document_date!==null||d.effective_date!==null||
      d.page_count!==3||!Array.isArray(d.reviewed_pages)||
      d.reviewed_pages.join(',')!=='1,2,3'||
      !Array.isArray(d.findings)||d.findings.length!==a.categories.length||
      typeof d.limitations!=='string'||d.limitations.length<140)
    throw Error('Original agenda attachment identity or status changed');
   found.add(d.id);
   const findings=d.findings.map((f,i)=>{
    if(f.category!==a.categories[i]||!d.reviewed_pages.includes(f.page)||
       typeof f.statement!=='string'||f.statement.length<120||
       !pdfPage(d.source_url,f.page))
     throw Error('Source PDF page or finding unverified');
    return {...f,original_page:pdfPage(d.source_url,f.page)};
   });
   if(d.id.includes('chapter')&&
      !(findings.some(f=>f.page===3&&/30 consecutive calendar days/.test(f.statement))&&
        findings.some(f=>/sharing/.test(f.category)&&/supervisor preapproval/.test(f.statement))&&
        findings.some(f=>/audit/.test(f.category)&&/outside the police department/.test(f.statement))))
    throw Error('Original chapter text anchors absent');
   if(d.id.includes('ordinance')&&!findings.some(f=>/unfilled adoption.date and mayoral signature placeholders/.test(f.statement)))
    throw Error('Unsigned ordinance template cannot appear executed');
   docs.push({...d,findings});
  }
  const h=record.signed_original_visually_reviewed;
  if(h.id!==HELD.id||h.source_url!==HELD.url||
     h.original_sha256!==HELD.sha||h.page_count!==3||
     h.pages_reviewed?.join(',')!=='1,2,3'||
     h.status!=='signed_city_clerk_adopted_ordinance_visual_page_review_sha256_pinned'||
     h.verification_method!=='visual_page_review_sha256_pinned_scanned_pdf'||
     h.adoption_date!=='2026-10-06'||h.legal_effective_date!==null||
     h.ordinance_number!==1579||
     !Array.isArray(h.findings)||h.findings.length!==3||
     h.findings.some((f,i)=>f.page!==i+1||
       typeof f.statement!=='string'||f.statement.length<170||
       !pdfPage(h.source_url,f.page))||
     h.findings[1].category!=='chapter_17_adopted_by_reference'||
     !/Resolution 26-43/.test(h.findings[1].statement)||
     h.findings[2].category!=='signed_adoption_and_misdemeanor_penalties'||
     !/mayoral signature and City Clerk's attestation/.test(h.findings[2].statement)||
     typeof h.limitations!=='string'||h.limitations.length<150)
   throw Error('Independently visually verified signed City Clerk original identity/date/limitations altered');
  const signed={...h,findings:h.findings.map(f=>({...f,
   original_page:pdfPage(h.source_url,f.page)}))};
  const p=record.agency_self_disclosure;
  if(!p||p.agency!=='Apache Junction Police Department'||
     p.jurisdiction!=='Apache Junction, AZ'||
     p.source_url!==SELF.url||p.official_map_url!==SELF.map||
     p.map_marked_date!==SELF.mapDate||p.checked_on!=='2026-10-27'||
     p.claimed_cameras!==SELF.cameras||
     p.claimed_retention_days!==SELF.retention||
     p.agency_claimed_sharing_scope!=='state_county_and_local_law_enforcement_within_arizona_only'||
     p.source_status!=='agency_authored_live_website_disclosure_not_independently_validated_live_fleet_or_access_settings'||
     p.exact_gis_coordinate_count!==0||!p.map_evidence.includes('offline_devices')||
     !p.map_evidence.includes('proposed_locations')||
     typeof p.limitations!=='string'||p.limitations.length<160)
    throw Error('Source-provided camera diagram improperly upgraded to exact coordinates or live truth');
  return Object.freeze({
   original_agenda_documents:docs,
   signed_city_clerk_original:signed,
   agency_self_disclosure:p,
   individually_verified_exact_camera_coordinates:0,
   city_clerk_adopted_copy_visually_reviewed:true,
   scope_note:'Unsigned Council agenda attachments do not prove final enacted chapter text. The separate visually verified, signed City Clerk Ordinance 1579 adopts Chapter 17 by reference, but the final filed chapter has not been authenticated against the agenda attachment. City schematic map symbols cannot become GIS coordinate pins.'
  });
 }
 return Object.freeze({verify,pdfPage,KNOWN,HELD});
});
