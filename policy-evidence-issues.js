/* Verifiable cross-source evidence issue ledger.
 * Issues are document/provenance questions, not operational violations.
 * Do not infer live cameras, adopted drafts, legal effect, or live sharing.
 */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronPolicyEvidenceIssues=api;
})(typeof window!=='undefined'?window:null,function(){
'use strict';
const URLS=Object.freeze({
 sedro:'https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Sedro-Wooley%20PD%20Policy.pdf?VersionId=_99QC9Us9FMQqUrIRzfc8WlWlkgJCZ9F',
 apacheCouncil:'https://apachejunction.legistar.com/View.ashx?GUID=97D4D861-6CFF-42D3-AC9D-B716D9367148&ID=15953709&M=F',
 apacheSigned:'https://www.apachejunctionaz.gov/DocumentCenter/View/33565/ORD1579',
 greenIndex:'https://www.greenbaywi.gov/1223/Policy-Manual',
 greenDraft:'https://www.greenbaywi.gov/DocumentCenter/View/19136/DRAFTED-REVISION---Policy-424-Automated-License-Plate-Readers-ALPR-September-2026',
 sultanRegistry:'https://www.atg.wa.gov/ALPR',
 sultanAuthority:'https://sultanwa.gov/176/Police',
 robbinsdale2025:'https://www.lrl.mn.gov/docs/2025/mandated/251675.pdf',
 robbinsdale2026:'https://www.robbinsdalemn.gov/389/4240/Automated-License-Plate-Readers-ALPR'
});
const HASH=Object.freeze({
 sedro:'4778f1f07f139658be0306edbb5049b1036e2a91ae22175bbcbd18c31c82c3b6',
 apacheCouncil:'ed2411b178181c2bca37e71fcb7c5678ba77f51e7363a6d9f155dc266ac5d724',
 apacheSigned:'9d4f0ff58b906c65112abd3cf725b00d95e3418a843cd5df0c9e30e9ea9a7e93',
 sultan:'b9b84eae00fed2b3f175a880fa2e0be1a17a7d79918ffc4936b991c57da18123',
 robbinsdale2025:'5374d507c1853a37df377cfab5068a24f36df04935b0fd5d66c79a9e3740c010'
});
function guard(ok,reason){if(!ok)throw Error('Source-provenance check failed: '+reason);}
function exactlyOne(items,pred,reason){
 guard(Array.isArray(items),reason+' collection');
 const matches=items.filter(pred);guard(matches.length===1,reason+' identity');
 return matches[0];
}
function source(label,url,page){
 guard(Object.values(URLS).includes(url),'unexpected citation '+label);
 return Object.freeze({label,url:url+(page?'#page='+page:''),page:page||null});
}
function build(x){
 guard(x&&typeof x==='object','all source catalogs');
 const wa=exactlyOne(x.wa?.documents,d=>d.id==='sedro-woolley-wa-flock-policy-2026','Sedro original');
 const retention=exactlyOne(wa.findings,f=>f.category==='policy_internal_retention_language_conflict','Sedro retention');
 guard(wa.source_url===URLS.sedro&&wa.content_sha256===HASH.sedro&&
   wa.state==='WA'&&wa.policy_kind==='agency_alpr_policy'&&
   wa.document_imprint_date==='2026-06-18'&&wa.pages_reviewed.includes(5)&&
   retention.page===5&&retention.statement.includes('thirty (21) days')&&
   retention.statement.includes('contradictory'),'verified contradictory policy text');

 const signed=x.apache?.signed_original_visually_reviewed;
 const council=exactlyOne(x.apache?.source_page_reviewed,r=>r.id==='apache-junction-2026-alpr-chapter-17-legistar-attachment','Apache chapter');
 guard(signed?.source_url===URLS.apacheSigned&&signed.original_sha256===HASH.apacheSigned&&
   signed.status==='signed_city_clerk_adopted_ordinance_visual_page_review_sha256_pinned'&&
   signed.adoption_date==='2026-10-06'&&signed.legal_effective_date===null&&
   signed.pages_reviewed.includes(2)&&
   council.source_url===URLS.apacheCouncil&&council.pdf_sha256===HASH.apacheCouncil&&
   council.publication_status==='council_agenda_code_attachment_not_independently_verified_final_enacted_text'&&
   council.reviewed_pages.includes(3)&&council.effective_date===null&&
   signed.findings.some(f=>f.page===2&&f.statement.includes('separately authenticated')),'enacted ordinance vs chapter text boundary');

 const green=exactlyOne(x.adoptions?.records,r=>r.id==='green-bay-wi-policy-424-draft-still-listed-2026-10-27','Green Bay');
 guard(x.adoptions.reviewed_on==='2026-10-27'&&green.status==='draft_published_no_adoption_verified'&&
   green.event_date===null&&green.effective_date===null&&
   green.source_url===URLS.greenIndex&&green.corroboration_url===URLS.greenDraft&&
   green.proof.includes('DRAFTED REVISION'),'Green Bay draft not adopted');

 const sultan=exactlyOne(x.waPages?.documents,d=>d.id==='sultan-wa-sheriff-policy-identity-exception','Sultan');
 guard(sultan.submitted_agency==='Sultan Police Department'&&
   sultan.publisher_actor==="Snohomish County Sheriff's Office"&&
   sultan.sha256===HASH.sultan&&sultan.agency_identity_issue===true&&
   sultan.identity_authority_source===URLS.sultanAuthority&&
   x.waPages.agency_identity_crosswalk_held===1&&
   sultan.actual_flock_equipment_verified===false,'Sultan sheriff agency identity hold');

 const rob=x.robbinsdale;
 guard(rob?.source_url===URLS.robbinsdale2025&&rob.sha256===HASH.robbinsdale2025&&
   rob.city_2026_source_url===URLS.robbinsdale2026&&
   rob.pages_reviewed.includes(2)&&
   rob.comparison_note.includes('differing record types')&&
   rob.current_operating_equipment_verified===false,'Robbinsdale incompatible dates and record types');
 const items=[
  {id:'sedro-woolley-retention-words-numerals',state:'WA',agency:'Sedro-Woolley Police Department',
   class:'textual_inconsistency',priority:'high',status:'clarification_unresolved',
   title:'Vendor purge interval is internally inconsistent',
   detail:'A June 2026 policy uses “thirty (21) days” for vendor purging while stating a general 21-day ALPR retention rule. The original wording is inconsistent; actual vendor retention has not been measured.',
   next:'Request an agency clarification or corrected dated policy; do not substitute 30 days for 21 days.',
   observed:'2026-06-18',citations:[source('Policy 425, page 5',URLS.sedro,5)]},
  {id:'apache-junction-final-chapter-authentication',state:'AZ',agency:'Apache Junction City Council',
   class:'final_document_missing',priority:'high',status:'final_chapter_text_unverified',
   title:'Signed ordinance adopts a separate chapter whose final text is not matched',
   detail:'The signed October 6, 2026 Ordinance 1579 is authenticated, but its adopted-by-reference Chapter 17 has not been matched to the earlier three-page Council agenda attachment. An independent legal effective date is also not established.',
   next:'Obtain the City Clerk-filed final Chapter 17 and compare its exact pages to the agenda attachment; verify legal effectiveness separately.',
   observed:'2026-10-06',citations:[source('Signed Ordinance 1579, page 2',URLS.apacheSigned,2),source('Agenda Chapter 17, page 3',URLS.apacheCouncil,3)]},
  {id:'green-bay-draft-adoption-decision',state:'WI',agency:'Green Bay Police Department',
   class:'adoption_not_established',priority:'medium',status:'draft_not_verified_as_adopted',
   title:'September proposed retention change remains a draft',
   detail:'The official policy index reviewed October 27, 2026 lists the September Policy 424 revision as DRAFT, separately from the May published policy. The proposed seven-day limit is not verified as adopted.',
   next:'Look for a department issuance order, dated final policy, or formal adoption action; do not publish the draft limit as current policy.',
   observed:'2026-10-27',citations:[source('Official policy index',URLS.greenIndex),source('September draft PDF',URLS.greenDraft)]},
  {id:'sultan-sheriff-document-attribution',state:'WA',agency:'Sultan / Snohomish County Sheriff',
   class:'publisher_identity_collision',priority:'medium',status:'operator_identity_unverified',
   title:'Sultan-submitted attachment identifies the Sheriff as its publisher',
   detail:'The Washington AGO-linked policy attachment under Sultan refers to Snohomish County Sheriff training and Flock access. It does not establish a separate Sultan-administered Flock system.',
   next:'Reconcile the contracted sheriff-service identity and find a separately attributable agency-specific published policy, if one exists.',
   observed:'2026-10-27',citations:[source('AGO registration',URLS.sultanRegistry),source('Sultan police-services authority',URLS.sultanAuthority)]},
  {id:'robbinsdale-retention-record-types',state:'MN',agency:'Robbinsdale Police Department',
   class:'cross_source_interpretation_caution',priority:'context',status:'not_a_verified_conflict',
   title:'Different dates and ALPR record types must not be treated as a policy contradiction',
   detail:'The 2025 independent audit describes a default 30-day Flock vehicle-read setting. The city’s August 2026 disclosure differentiates two-year license-plate photos from 30-day hit records. This is a comparison caution, not a verified legal or operational discrepancy.',
   next:'Compare like-for-like data categories and observation periods before asserting a change or conflict.',
   observed:'2026-10-27',citations:[source('2025 auditor PDF, page 2',URLS.robbinsdale2025,2),source('August 2026 city FAQ',URLS.robbinsdale2026)]}
 ];
 guard(items.length===5&&new Set(items.map(i=>i.id)).size===5,'case counts');
 guard(items.every(i=>i.citations.every(c=>c.url.startsWith('https://'))),'approved public citations');
 return Object.freeze({
  items:Object.freeze(items.map(i=>Object.freeze({...i,citations:Object.freeze(i.citations)}))),
  open_source_questions:items.filter(i=>i.priority!=='context').length,
  interpretive_cautions:items.filter(i=>i.priority==='context').length,
  verified_current_equipment:0,new_camera_coordinates:0,
  warning:'Document status or policy wording alone cannot prove live Flock equipment, legal compliance, operational deletion, or data sharing.'
 });
}
return Object.freeze({build});
});
