/* Public Washington Attorney General ALPR self-certification snapshot.
   The AGO has NOT independently verified its registration attestations.
   No Flock vendor claim, installation, GPS point, sharing edge or compliance
   conclusion can be produced from this state index.
*/
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronWashingtonALPR=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const AGO='https://www.atg.wa.gov/ALPR';
 const HOSTS=new Set(['agportal-s3bucket.s3.us-west-2.amazonaws.com','blackdiamondwa.gov','www.cwu.edu','www.cpwa.us',
 'www.douglascountysheriff.org','www.eastwenatcheewa.gov','inside.ewu.edu','www.ellensburgwa.gov',
 'www.cityofenumclaw.net','www.everettwa.gov','www.grandview.wa.us','public.powerdms.com',
 'www.co.kittitas.wa.us','www.libertylakewa.gov','www.cityofmontesano.com','www.pasco-wa.gov',
 'selahwa.gov','www.soundtransit.org','uniongapwa.gov','www.washington.edu',
 'transportation.wsu.edu','transportation.wwu.edu']);
 function safe(url){
  try{
   if(typeof url!=='string'||url.length>950)return null;
   const u=new URL(url);
   if(u.protocol!=='https:'||!HOSTS.has(u.hostname)||u.host!==u.hostname||
     u.username||u.password||u.hash||u.pathname.includes('..'))return null;
   if(u.search){
    const s3=u.hostname==='agportal-s3bucket.s3.us-west-2.amazonaws.com'&&
     /^\?VersionId=[a-zA-Z0-9_.-]{1,100}$/.test(u.search);
    const municipal=new Set(['www.eastwenatcheewa.gov','www.everettwa.gov','www.libertylakewa.gov']).has(u.hostname)&&
     /^\/DocumentCenter\/View\/[0-9]+\//.test(u.pathname)&&u.search==='?bidId=';
    if(!s3&&!municipal)return null;
   }
   return u.href;
  }catch(_){return null;}
 }
 function valid(r){
  return r&&typeof r==='object'&&
   /^[a-f0-9]{20}$/.test(r.id||'')&&
   typeof r.agency_name==='string'&&r.agency_name.length>=4&&r.agency_name.length<=160&&
   typeof r.submitted_date_as_published==='string'&&r.submitted_date_as_published.length<=80&&
   (r.submitted_on===null||
    (typeof r.submitted_on==='string'&&/^20\d{2}-\d{2}-\d{2}$/.test(r.submitted_on)&&
     !Number.isNaN(Date.parse(r.submitted_on))&&
     new Date(r.submitted_on+'T00:00:00Z').toISOString().slice(0,10)===r.submitted_on))&&
   r.registry_status==='agency_self_certification_listed_by_state_AG_not_independently_verified'&&
   typeof r.policy_link_label==='string'&&r.policy_link_label.length<=180&&
   Array.isArray(r.policy_links_from_official_ago_page)&&
   r.policy_links_from_official_ago_page.length<=3&&
   r.policy_links_from_official_ago_page.every(u=>!!safe(u));
 }
 function catalog(d){
  if(!d||d.schema_version!==1||d.source_url!==AGO||
   !/^[a-f0-9]{64}$/.test(d.source_sha256||'')||
   !/^20\d{2}-\d{2}-\d{2}$/.test(d.captured_on||'')||
   !Array.isArray(d.registrations)||d.registrations.length<20||d.registrations.length>500||
   !d.registrations.every(valid)||
   new Set(d.registrations.map(x=>x.agency_name.toLowerCase())).size!==d.registrations.length||
   d.camera_points_published!==0||d.flock_vendor_assertions_published!==0||d.sharing_network_edges_published!==0||
   typeof d.warning!=='string'||!d.warning.includes('has not independently verified'))
   throw Error('Unverified state Attorney General registration snapshot');
  return d.registrations.slice().sort((a,b)=>a.agency_name.localeCompare(b.agency_name));
 }
 return {catalog,safe,source:AGO};
});
