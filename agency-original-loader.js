/* Load original government PDF page evidence through the existing strict validators.
 * No third-party lookups or agency-name fuzzy joins. */
(function(root,factory){'use strict';const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronOriginalLoader=api;
})(typeof window!=='undefined'?window:null,function(){
'use strict';
const SOURCES=Object.freeze({
 okc:'./data/verified-okc-2026-original-flock-contract-review.json',
 ne:'./data/verified-nebraska-original-aggregate-reports.json',
 riSd:'./data/verified-ri-sd-original-alpr-policies.json',
 kittitas:'./data/verified-wa-kittitas-scanned-draft-review.json',
 waRegistry:'./data/wa-original-agency-alpr-registrations.json',
 waHeld:'./data/wa-held-original-policy-diagnostics.json',
 national:'./data/verified-national-government-documents.json',
 flock:'./data/verified-wa-flock-policy-originals.json',
 other:'./data/verified-wa-agency-policies.json',
 receipts:'./data/wa-ago-original-policy-source-inspection.json'
});
async function load(fetcher,impl){
 if(typeof fetcher!=='function'||!impl||!impl.Core||!impl.WA||
  !impl.okc||!impl.ne||!impl.riSd||!impl.kittitas||!impl.national||
  !impl.flock||!impl.other)throw Error('Original verifier modules missing');
 const names=Object.keys(SOURCES);
 const raw={};
 await Promise.all(names.map(async name=>{
  const reply=await fetcher(SOURCES[name],{cache:'no-store',referrerPolicy:'no-referrer'});
  if(!reply.ok)throw Error('Original verified ledger unavailable: '+name);
  raw[name]=await reply.json();
 }));
 const base=impl.Core.catalog(raw,{okc:impl.okc,ne:impl.ne,riSd:impl.riSd,
  kittitas:impl.kittitas,national:impl.national});
 const wa=impl.WA.catalog({flock:raw.flock,other:raw.other,
  registry:raw.waRegistry,receipts:raw.receipts},{flock:impl.flock,other:impl.other});
 const index=impl.WA.combine(base,wa);
 return {index,raw};
}
function browserModules(w){
 return {Core:w.KatoptronVerifiedAgencyDossiers,WA:w.KatoptronWAOriginalAgencyDossiers,
  okc:w.KatoptronOKCOriginalContracts,ne:w.KatoptronNebraskaOriginalAggregate,
  riSd:w.KatoptronRISDOriginalPolicies,kittitas:w.KatoptronKittitasDraftReview,
  national:w.KatoptronNationalPrimaryDocuments,
  flock:w.KatoptronWAReviewedFlockSources,other:w.KatoptronWashingtonOriginalPolicies};
}
return Object.freeze({load,browserModules,SOURCES});
});
