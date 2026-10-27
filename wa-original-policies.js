/* Individually page-reviewed ALPR policy text from original WA AGO-listed PDFs.
 * This is not a Flock manufacturer proof, live-device inventory, compliance ruling,
 * or established sharing-network edge. S3 VersionId is preserved exactly. */
(function(root,factory){'use strict';const API=factory();
 if(typeof module==='object'&&module.exports)module.exports=API;
 if(root)root.KatoptronWashingtonOriginalPolicies=API;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SOURCES={
  'auburn-wa-policy-july-2026':{
   agency:'Auburn Police Department',pages:8,imprint:'2026-07-02',
   method:'original_pdf_sha256_page_text_anchors',
   sha:'484830933e46300a5471d3fccc4354f33ae1b683bc8401fa938b8a4d3f53863f',
   url:'https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Auburn%20PD%20ALPR%20Policy.pdf?VersionId=bPOrBG6TYUmkpHt6dVALLEcyhx2utLnH',
   reviewed:[2,5,6,7]},
  'normandy-park-wa-policy-june-2026':{
   agency:'Normandy Park Police Department',pages:5,imprint:'2026-06-30',
   method:'original_pdf_sha256_page_text_anchors',
   sha:'b4b26800bc0d3966b83df83abd8ccd9eeb7485e61b4057f724adad2352e4e935',
   url:'https://agportal-s3bucket.s3.us-west-2.amazonaws.com/ALPR/Normandy%20Park%20PD%20Policy.pdf?VersionId=18O0TMpqPRPGCuXKIAFSRKWNSwGnRuaY',
   reviewed:[1,3,4,5]},
  'black-diamond-wa-policy-june-2026':{
   agency:'Black Diamond Police Department',pages:7,imprint:'2026-06-23',
   method:'original_pdf_sha256_visually_reviewed_raster_pages',
   sha:'8ccf182125bf61bc624be72cb389f5ce218d36cf60f9db62d5ba8d58418f2446',
   url:'https://blackdiamondwa.gov/DocumentCenter/View/4324/BDPD-ALPR-Policy',
   reviewed:[1,4]}
 };
 function safeSource(row){
  if(!row||!Object.prototype.hasOwnProperty.call(SOURCES,row.id))return null;
  return row.source_url===SOURCES[row.id].url?SOURCES[row.id].url:null;
 }
 function valid(row){
  if(!row||typeof row!=='object'||!safeSource(row))return false;
  const x=SOURCES[row.id];
  return row.state==='WA'&&row.agency_name===x.agency&&
   row.policy_manual_imprint===x.imprint&&
   row.content_sha256===x.sha&&row.page_count===x.pages&&
   row.source_tier==='agency_published_policy_via_state_ag_registry'&&
   row.verification_method===x.method&&
   Array.isArray(row.pages_reviewed)&&
   row.pages_reviewed.length===x.reviewed.length&&
   row.pages_reviewed.every((p,i)=>p===x.reviewed[i])&&
   (row.ago_registration_date===(row.id==='black-diamond-wa-policy-june-2026'?'2026-07-08':'2026-07-07'))&&
   Array.isArray(row.findings)&&row.findings.length>=2&&row.findings.length<=5&&
   row.findings.every(f=>f&&x.reviewed.includes(f.page)&&
     typeof f.statement==='string'&&f.statement.length>=80&&f.statement.length<=900)&&
   !Object.hasOwn(row,'vendor')&&!Object.hasOwn(row,'flock_vendor')&&
   !Object.hasOwn(row,'camera_count')&&!Object.hasOwn(row,'operational_status')&&
   (row.id!=='black-diamond-wa-policy-june-2026'||
     (typeof row.verification_note==='string'&&row.verification_note.includes('visually')));
 }
 function catalog(obj){
  if(!obj||obj.schema_version!==1||!Array.isArray(obj.documents)||
   obj.documents.length!==3||!obj.documents.every(valid)||
   new Set(obj.documents.map(x=>x.id)).size!==2||
   typeof obj.scope_limits!=='string'||!obj.scope_limits.includes('not establish active deployment'))
   throw Error('Unverified original Washington ALPR policy evidence');
  return obj.documents.slice().sort((a,b)=>a.agency_name.localeCompare(b.agency_name));
 }
 return {catalog,valid,safeSource};
});
