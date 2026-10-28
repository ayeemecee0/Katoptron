/* Source-pinned 2026 Providence and Brookings government-authored ALPR policies */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronRISDOriginalPolicies=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SOURCES={
 'providence-ri-general-order-35005-sept2026':{
  state:'RI',agency:'Providence Police Department',
  url:'https://ppd.providenceri.gov/wp-content/uploads/2026/10/350.05-Automated-License-Plate-Readers-ALPR.pdf',
  index:'https://ppd.providenceri.gov/policies-and-procedures/',
  sha:'74b04c3c5b3f7c6fba013ea205e23279213efd20247be9039acb8cd8e7716f46',
  bytes:235578,pages:10,issued:'2026-09-04',effective:'2026-09-04',
  type:'department_published_effective_general_order',
  png:['1a3debe282cdc8128c473c3cf3ab43c4303f7456cff7cc30d12d46032cf0ede7',
   '31a5a1342b59c5ce87686dce4bae0ee690511794517ccd0aef541e92c4f894c1',
   '05792cd61271a5f02f575d6793212cf950ac482bf55b7e5a1f88e4f41f658cae',
   'f1e3874b5acb4e8329c27f9204734498a256263958ce9443e815ea0f3e068687'],
  reviewed:[1,7,8,9]},
 'brookings-sd-policy-13d1-revised-sept2026':{
  state:'SD',agency:'Brookings Police Department',
  url:'https://www.cityofbrookings-sd.gov/DocumentCenter/View/20501/Policy-13D1---Automated-License-Plate-Recognition-System',
  index:'https://www.cityofbrookings-sd.gov/941/Automated-License-Plate-Readers-ALPRs',
  sha:'2c47881c232c5cb46dd110bf687770371982821798bcb47feebbcb5fc3553df2',
  bytes:330030,pages:6,issued:'2024-04-24',effective:'2026-09-22',
  type:'department_published_chief_signed_policy_revision',
  png:['3eea1e1369c28cb9418148e3bdd0fe8576062fbbfb9cea61145c0ab02ce0bf14',
   '1717481cdd2d3ea4fa678153a8f3a937a455c50db907ed5d1e195502862d1c30',
   'c07437fdc865a4f2299978ccb3c8698cf8d8cac2dd160aa8875003eb0b9fcbc5'],
  reviewed:[1,5,6]}
 };
 function catalog(d){
  if(!d||d.schema_version!==1||d.source_count!==2||
   d.scope!=='two_original_page_reviewed_department_published_policy_versions_not_telemetry_or_external_audits'||
   !Array.isArray(d.documents)||d.documents.length!==2||
   typeof d.limits!=='string'||!d.limits.includes('Neither document independently verifies'))
    throw Error('Original RI and SD government policy evidence missing');
  const seen=new Set();
  for(const r of d.documents){
   const x=SOURCES[r?.id];
   if(!x||seen.has(r.id)||r.state!==x.state||r.agency!==x.agency||
    r.source_url!==x.url||r.official_policies_index!==x.index||
    r.original_sha256!==x.sha||r.original_bytes!==x.bytes||
    r.page_count!==x.pages||r.source_issue_date!==x.issued||
    r.source_effective_date!==x.effective||r.kind!==x.type||
    JSON.stringify(r.pages_visually_reviewed)!==JSON.stringify(x.reviewed)||
    JSON.stringify(Object.values(r.original_png_sha256||{}))!==JSON.stringify(x.png)||
    !Array.isArray(r.findings)||r.findings.length<3||
    r.findings.some(f=>!x.reviewed.includes(f.page)||!f.kind||
      typeof f.statement!=='string'||f.statement.length<=110||f.statement.length>700)||
    ['camera_coordinates','camera_count','actual_data_sharing_verified',
      'independent_audit_completed','live_retention_verified'].some(k=>Object.hasOwn(r,k)))
    throw Error('Unverified state policy original or camera claim');
   seen.add(r.id);
  }
  if(seen.size!==2)throw Error('Original state policy corpus incomplete');
  return d.documents;
 }
 return {catalog};
});