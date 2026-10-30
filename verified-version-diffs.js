/* Strict claim-level, source-reviewed contract and policy comparison.
   Input is ONLY the existing independently validated change tracker output.
   Differences are between reviewed findings, not full PDF redlines or live system state. */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.KatoptronVerifiedDiffs=api;})(typeof window!=='undefined'?window:null,function(){
'use strict';
const TYPES=new Set(['executed_contract_status_change','signed_contract_amendment','unadopted_policy_proposal','authenticated_signed_resolution_attachment']);
function validSource(s){
 try{const u=new URL(s.url);return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&/^#page=\d{1,3}$/.test(u.hash)&&/^[a-f0-9]{64}$/.test(s.sha||'');}catch{return false;}
}
function words(t){return t.match(/\S+/g)||[];}
function wordsDiff(before,after){
 const left=words(before),right=words(after);
 if(!left.length||!right.length||left.length>400||right.length>400)throw Error('Reviewed claim text outside bounds');
 let prefix=0;while(prefix<left.length&&prefix<right.length&&left[prefix]===right[prefix])prefix++;
 let suffix=0;while(suffix<left.length-prefix&&suffix<right.length-prefix&&left[left.length-suffix-1]===right[right.length-suffix-1])suffix++;
 return {shared_prefix:left.slice(0,prefix).join(' '),removed:left.slice(prefix,left.length-suffix).join(' '),added:right.slice(prefix,right.length-suffix).join(' '),shared_suffix:suffix?left.slice(-suffix).join(' '):'',same:before===after};
}
function fromEvents(events){
 if(!Array.isArray(events)||!events.length||events.length>200)throw Error('Verified source transition set unavailable');
 const ids=new Set();
 return events.map(e=>{
  if(!e||ids.has(e.id)||!TYPES.has(e.kind)||!e.id||typeof e.title!=='string'||typeof e.before!=='string'||typeof e.after!=='string'||
   !['boolean'].includes(typeof e.substantive)||e.verified_policy_effectiveness!==false||
   e.actual_device_or_platform_configuration_verified!==false||!Array.isArray(e.sources)||!e.sources.length||
   !e.sources.every(validSource))throw Error('Unsafe or unverified comparison input');
  ids.add(e.id);
  const proposal=e.kind==='unadopted_policy_proposal';
  if(proposal&&e.substantive)throw Error('Unadopted proposal must not become enacted change');
  return Object.freeze({id:e.id,agency:e.agency_name||e.agency_key,state:e.state,title:e.title,
   category:proposal?'policy_proposal':e.kind==='authenticated_signed_resolution_attachment'?'government_document':'contract_document',
   status:e.status,substantive:e.substantive,
   interpretation:proposal?'Proposal compared with published record; not adopted policy or operational change.':
     'Source-qualified document-level comparison; no actual deployment or system operation inferred.',
   before:e.before,after:e.after,delta:wordsDiff(e.before,e.after),
   evidence:e.sources.map(s=>({label:s.label,url:s.url,sha:s.sha}))});
 });
}
return Object.freeze({fromEvents,wordsDiff,validSource});
});
