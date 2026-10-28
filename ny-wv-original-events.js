/* Verified original NY historical program/termination and WV legislative event sources */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronNYWVOriginalEvents=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const LOOKUP={
 'ny-tompkins-sheriff-july2025-flock-disclosure':{
  state:'NY',kind:'agency_authored_historical_flock_use_and_sharing_policy_self_report',
  status:'2025_government_original_page_7_flock_use_no_live_status',
  date:'2025-07-31',
  url:'https://www.tompkinscountyny.gov/files/assets/county/v/1/sheriffs-office/documents/public-safety-meeting-reports/public-safety-meeting-report-july-2025.pdf',
  sha:'a44d7a11f61c62508936cbc43ff1233cad2849929e81afd482046e6f47f94988',bytes:1162207,
  page:7,png:'c6ff5f1eb968dcad8ae4e602ec41b7229ad8074fba38030fd2ab2ff7718c8a2a'},
 'ny-tompkins-county-april2026-termination-resolution':{
  state:'NY',kind:'county_legislature_approved_flock_contract_termination_resolution',
  status:'approved_12_to_1_termination_decision_actual_deactivation_not_independently_proven',
  date:'2026-04-14',
  url:'https://www.tompkinscountyny.gov/News-articles/Highlights-of-the-4726-regular-and-41426-special-Tompkins-County-Legislature-meetings',
  sha:'ed1d19e3f788785ea3da740340e4309693aa0aced711b6f4ae79ef86d9c590e1',bytes:139111},
 'wv-joint-government-organization-flock-agenda-2026':{
  state:'WV',kind:'official_proposed_public_hearing_agenda',
  status:'meeting_agenda_not_enacted_flock_regulation',date:'2026-08-09',
  url:'https://www.wvlegislature.gov/Committees/Interims/agenda.cfm?abb=GOVORG&recordid=5649',
  sha:'c013382be5fec14882c056e0316246fae5615519fd3983666b273cf9b2d5fec3',bytes:30028},
 'wv-joint-government-organization-august2026-hearing-report':{
  state:'WV',kind:'state_legislature_retrospective_public_hearing_report',
  status:'committee_discussion_reported_no_enacted_bill_or_deployment_inferred',
  date:'2026-08-10',
  url:'https://blog.wvlegislature.gov/headline/2026/08/10/interim-report-joint-committee-on-government-organization/',
  sha:'b95e81371586fe272ed4d77b1e99712a2210ed47533ce17f23d75959ddf88e57',bytes:244510}
 };
 function catalog(data){
  if(!data||data.schema_version!==1||data.source_count!==4||
   data.scope!=='historical_first_party_ny_flock_usage_termination_and_wv_legislative_hearing_not_live_surveillance'||
   !Array.isArray(data.records)||data.records.length!==4||
   typeof data.limits!=='string'||!data.limits.includes('No new camera coordinates'))
   throw Error('Incomplete original New York and West Virginia source history');
  const seen=new Set();
  for(const r of data.records){
   const v=LOOKUP[r?.id];
   if(!v||seen.has(r.id)||r.state!==v.state||r.kind!==v.kind||
    r.status!==v.status||r.source_date!==v.date||r.source_url!==v.url||
    r.content_sha256!==v.sha||r.original_bytes!==v.bytes||
    r.source_type!==(v.page?'pdf':'html')||
    typeof r.publisher_role!=='string'||r.publisher_role.length<10||
    typeof r.agency!=='string'||r.agency.length<12||
    !Array.isArray(r.findings)||r.findings.length<1||
    r.findings.some(f=>typeof f.statement!=='string'||f.statement.length<125||f.statement.length>750||
      typeof f.kind!=='string'||(v.page?f.page!==7:Object.hasOwn(f,'page')))||
    ['camera_coordinates','operational_camera_count','live_partner_edges',
     'finished_camera_removal_verified','enacted_wv_flock_statute'].some(k=>Object.hasOwn(r,k)))
    throw Error('Unverified source, legislative action or agency network promoted');
   if(v.page&&(r.page_count!==8||r.visually_reviewed_page!==7||
    r.source_page_png_sha256!==v.png||typeof r.source_date_note!=='string'||
    !r.source_date_note.includes('not verified issue date')))
    throw Error('Original historical program report page source altered');
   seen.add(r.id);
  }
  if(seen.size!==4)throw Error('Original government event corpus incomplete');
  return data.records;
 }
 return {catalog};
});