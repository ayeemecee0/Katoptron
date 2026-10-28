'use strict';
/* Audit all 12 held national original URLs and 97 WA AGO registrations.
 * An agency that submitted an ALPR policy is NOT presumed to operate Flock.
 * A reviewable hold is a work status, not a verified finding.
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const statusActions={
 held_redirect:'Inspect exact original redirect destination and re-establish municipal publisher authority before fetching again',
 held_http_error:'Find the current official publisher index or archived government version; retry a bounded original request',
 held_oversized:'Retrieve a bounded original in a sandbox with size or page restrictions; reject partial-byte quote claims',
 held_wrong_format:'Determine returned document type at official publisher; resolve canonical original instead of assuming PDF',
 held_unreadable_original:'Inspect scanned or nonstandard government original by rendered page, with exact source hash and visual evidence',
 held_timeout_or_network:'Recheck government endpoint using bounded retries and authority-preserving canonical URL'
};
function build(){
 const receipts=read('data/nationwide-original-government-source-receipts.json').receipts;
 const sources=read('data/nationwide-government-jurisdiction-registry.json').official_seed_sources;
 const registrations=read('data/wa-original-agency-alpr-registrations.json').registrations;
 const reviewed=[
  ...read('data/verified-wa-flock-policy-originals.json').documents,
  ...read('data/verified-wa-agency-policies.json').documents
 ];
 const seen=new Set(),sourceById=new Map(sources.map(s=>[s.id,s]));
 const held=receipts.filter(r=>r.status.startsWith('held_')).map(r=>{
  const original=sourceById.get(r.source_id);
  if(!original||original.source_url!==r.source_url||!statusActions[r.status]||
    r.sha256_at_observation!==null||r.page_count_at_observation!==null)
   throw Error('National source hold ungrounded');
  return {id:'gov-original:'+r.source_id,state:r.state,source_url:r.source_url,
   publisher:original.publisher,kind:'official_government_original',
   original_status:r.status,
   disposition:'actionable_source_hold',
   next_action:statusActions[r.status],
   evidence_verified:false,flock_vendor_verified:false,
   contract_signed_verified:false,law_effective_verified:false,
   exact_camera_points_added:0};
 });
 if(held.length!==12)throw Error('Expected 12 national source holds');
 const reviewedMap=new Map();
 for(const p of reviewed){
  if(!/^[a-f0-9]{64}$/.test(p.content_sha256||'')||!Array.isArray(p.pages_reviewed)||!p.pages_reviewed.length)throw Error('WA reviewed source invalid');
  const key=p.agency_name.toLowerCase()+'|'+p.source_url;
  if(reviewedMap.has(key))throw Error('WA reviewed duplicated exact source identity');
  reviewedMap.set(key,p);
 }
 const reg=registrations.map(r=>{
  const links=r.policy_links_from_official_ago_page;
  if(r.registry_status!=='agency_self_certification_listed_by_state_AG_not_independently_verified'||
      seen.has(r.id)||!Array.isArray(links)||links.length>3)throw Error('AG agency source invalid');
  seen.add(r.id);
  const exact=links.flatMap(url=>{
   const p=reviewedMap.get(r.agency_name.toLowerCase()+'|'+url);return p?[p]:[];
  });
  if(exact.length>1)throw Error('Duplicated reviewed source claimed as separate policy');
  return {id:'wa-ago-registration:'+r.id,state:'WA',agency:r.agency_name,
   submitted_on:r.submitted_on,source_url:'https://www.atg.wa.gov/ALPR',
   policy_original_links:links,
   kind:'wa_ago_original_self_certification',
   original_status:r.registry_status,
   disposition:exact.length?'individual_original_policy_page_review_recorded':
    links.length?'actionable_policy_original_page_review_hold':
     'actionable_no_original_link_hold',
   reviewed_original_id:exact[0]?.id||null,
   reviewed_original_sha256:exact[0]?.content_sha256||null,
   reviewed_pages:exact[0]?.pages_reviewed||[],
   next_action:exact.length?
    'Preserve original reviewed page citations; verify Flock vendor use separately and compare revisions':
    links.length?
    'Acquire exact state-linked policy document and individually verify original pages, dates, agency and vendor identity':
    'Locate the agency original ALPR policy under the state Attorney General publisher',
   agency_registration_verified:true,
   flock_vendor_or_operational_status_verified:false,
   current_policy_effectiveness_verified:false,
   exact_camera_points_added:0};
 });
 if(reg.length!==97||reg.filter(r=>r.reviewed_original_id!==null).length!==11)throw Error('97 WA / 11 reviewed mismatch');
 const discovered=[
 {id:'gov-original-candidate:robbinsdale-mn-policy-427',state:'MN',
  publisher:'Robbinsdale Police Department',
  source_url:'https://www.robbinsdalemn.gov/DocumentCenter/View/2520/Robbinsdale-Police-Department-Policy-Manual-Policy-427',
  kind:'same_publisher_policy_pdf_candidate',
  disposition:'actionable_individual_original_pdf_page_review_hold',
  next_action:'Acquire and page-review Policy 427 original; compare policy imprints and Flock vendor terms to the separately verified municipal HTML disclosure',
  html_agency_flock_statement_reviewed:true,pdf_content_reviewed:false,flock_technology_currently_operational_verified:false,exact_camera_points_added:0},
 {id:'gov-original-candidate:brookings-sd-13d1',state:'SD',
  publisher:'Brookings Police Department',
  source_url:'https://cityofbrookings-sd.gov/DocumentCenter/View/20501/Policy-13D1---Automated-License-Plate-Recognition-System',
  kind:'same_publisher_policy_pdf_candidate',
  disposition:'duplicate_previously_reviewed_original',
  next_action:'Compare original source checksum with existing Brookings 13D1 original review before re-opening; do not double-count a reviewed policy',
  html_agency_flock_statement_reviewed:true,pdf_content_reviewed:true,flock_technology_currently_operational_verified:false,exact_camera_points_added:0}
 ];
 const out={schema_version:1,prepared_on:'2026-10-27',
  scope:'all_12_held_official_state_sources_plus_97_WA_self_certifications_plus_2_policy_candidates',
  holds:held,wa_registrations:reg,policy_link_candidates:discovered,
  counts:{national_source_holds:held.length,wa_registration_entries:reg.length,
   wa_page_reviewed_originals:reg.filter(r=>r.reviewed_original_id).length,
   wa_individual_policy_reviews_pending:reg.filter(r=>!r.reviewed_original_id).length,
   pending_new_original_policy_pdf:1,known_duplicate_original_pdf:1,
   open_source_review_items:held.length+reg.filter(r=>!r.reviewed_original_id).length+1,
   complete_wa_flock_operator_coverage:0,verified_new_exact_camera_points:0},
  limits:'WA state registration does not establish Flock use. A held source does not establish absent or present Flock equipment. Existing reviewed PDF remains distinct from an original government website publication. No candidate is auto-upgraded into executed contract, adoption, live equipment or sharing.'
 };
 return out;
}
const value=build(),out=process.argv[2]||'.katoptron-ci/nationwide-agency-evidence-backlog.json';
const abs=path.resolve(ROOT,out);
if(!abs.startsWith(ROOT+path.sep))throw Error('Unsafe destination');
fs.mkdirSync(path.dirname(abs),{recursive:true});
fs.writeFileSync(abs,JSON.stringify(value,null,2)+'\n');
console.log('EVIDENCE_BACKLOG_111',JSON.stringify(value.counts));
if(require.main===module){} // Intentionally no network or production DB writes.
module.exports={build};
