/* Katoptron original-audit cross-period comparisons.
 * Only matched original-source, content-pinned, page-reviewed, agency-specific
 * snapshots. Never convert a report into a current camera count or legal score.
 */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.KatoptronAuditHistory=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const DATE=/^\d{4}-\d{2}-\d{2}$/;
 const SHA=/^[0-9a-f]{64}$/;
 const ID=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
 function date(s){
  if(typeof s!=='string'||!DATE.test(s))return null;
  const d=new Date(s+'T00:00:00Z');
  return !Number.isNaN(d.getTime())&&d.toISOString().slice(0,10)===s?s:null;
 }
 function originalUrl(url){
  try{const u=new URL(url);
   return u.protocol==='https:'&&u.host==='www.lrl.mn.gov'&&
    /^\/docs\/20\d\d\/mandated\/\d{6}\.pdf$/.test(u.pathname)&&
    !u.username&&!u.password&&!u.search&&!u.hash?u.href:null;
  }catch{return null;}
 }
 function source(r){
  return r&&typeof r==='object'&&
   r.source_tier==='original_government_archive_independent_audit_report'&&
   originalUrl(r.source_url)&&SHA.test(r.content_sha256||'')&&
   typeof r.id==='string'&&ID.test(r.id)&&
   typeof r.agency_name==='string'&&r.agency_name.trim().length>=8&&
   typeof r.jurisdiction_key==='string'&&
   date(r.report_date)&&date(r.period_start)&&date(r.period_end)&&
   r.period_start<=r.period_end&&
   Array.isArray(r.pages_reviewed)&&r.pages_reviewed.length>=1&&
   r.pages_reviewed.every(p=>Number.isInteger(p)&&p>=1&&p<=30)&&
   r.cross_period&&ID.test(r.cross_period.agency_id||'');
 }
 function checkedPage(report,page){
  return Number.isInteger(page)&&report.pages_reviewed.includes(page);
 }
 function metric(report,m){
  return m&&typeof m==='object'&&
   m.key==='stationary_flock_alpr_units'&&
   m.vendor==='Flock Safety'&&m.deployment==='stationary'&&
   m.unit==='units'&&m.measurement==='auditor_snapshot'&&
   Number.isSafeInteger(m.value)&&m.value>=0&&m.value<=100000&&
   checkedPage(report,m.page);
 }
 function systems(report){
  const a=report.cross_period.systems;
  if(!Array.isArray(a)||a.length===0||a.length>8)return [];
  const seen=new Set(),out=[];
  for(const x of a){
   if(!x||!['Flock Safety','Elsag','Axon'].includes(x.vendor)||
      !['stationary','patrol_vehicle'].includes(x.deployment)||
      !checkedPage(report,x.page))return [];
   const k=x.vendor+':'+x.deployment;
   if(seen.has(k))return [];
   seen.add(k);out.push({vendor:x.vendor,deployment:x.deployment,key:k});
  }
  return out;
 }
 function compare(catalog,jurisdictionKey){
  if(!Array.isArray(catalog)||typeof jurisdictionKey!=='string')return [];
  const unique=new Set(),groups=new Map(),events=[];
  for(const r of catalog){
   if(!source(r)||r.jurisdiction_key!==jurisdictionKey)continue;
   const identity=r.cross_period.agency_id;
   if(unique.has(r.source_url))continue;
   unique.add(r.source_url);
   if(!groups.has(identity))groups.set(identity,[]);
   groups.get(identity).push(r);
  }
  for(const [agencyId,items] of groups){
   items.sort((a,b)=>a.report_date.localeCompare(b.report_date));
   for(let i=1;i<items.length;i++){
    const old=items[i-1],newer=items[i];
    if(old.agency_name!==newer.agency_name||
       old.report_date>=newer.report_date||
       old.period_end>=newer.period_start)continue;
    const before=Array.isArray(old.cross_period.metrics)?old.cross_period.metrics.filter(m=>metric(old,m)):[];
    const after=Array.isArray(newer.cross_period.metrics)?newer.cross_period.metrics.filter(m=>metric(newer,m)):[];
    for(const a of before){
     const b=after.find(x=>metric(newer,x)&&
      x.key===a.key&&x.vendor===a.vendor&&
      x.deployment===a.deployment&&x.unit===a.unit&&
      x.measurement===a.measurement);
     if(!b)continue;
     const delta=b.value-a.value;
     events.push({
      type:'reported_stationary_count_comparison',
      agency_id:agencyId,agency_name:old.agency_name,
      title:'Stationary Flock units reported: '+a.value+' → '+b.value+
        (delta===0?' (no numerical difference)':delta>0?' (+'+delta+')':' ('+delta+')'),
      detail:'Two original audits of the same agency describe consecutive periods. This is a difference between historical auditor-reported device counts, not verified additions, removals, live status, or individual camera coordinates.',
      previous_value:a.value,current_value:b.value,reported_delta:delta,
      earlier_date:old.report_date,later_date:newer.report_date,
      earlier_period:[old.period_start,old.period_end],
      later_period:[newer.period_start,newer.period_end],
      citations:[old.source_url+'#page='+a.page,newer.source_url+'#page='+b.page]
     });
    }
    const prevSystems=systems(old),nextSystems=systems(newer);
    if(prevSystems.length&&nextSystems.length){
     const p=prevSystems.map(x=>x.key).sort().join('|'),n=nextSystems.map(x=>x.key).sort().join('|');
     if(p!==n){
      const transition_note=typeof newer.cross_period.transition_note==='string'&&
       newer.cross_period.transition_note.length<=450&&
       checkedPage(newer,newer.cross_period.transition_page)?newer.cross_period.transition_note:'';
      events.push({
       type:'historical_platform_difference',agency_id:agencyId,agency_name:old.agency_name,
       title:'Different ALPR technologies documented across audits',
       detail:'Earlier: '+prevSystems.map(x=>x.vendor+' ('+x.deployment.replace('_',' ')+')').join(', ')+
         '. Later: '+nextSystems.map(x=>x.vendor+' ('+x.deployment.replace('_',' ')+')').join(', ')+
         '. '+transition_note+
         ' These are historical descriptions of different hardware categories. Do not subtract patrol units from fixed locations or infer the current deployment.',
       earlier_date:old.report_date,later_date:newer.report_date,
       earlier_period:[old.period_start,old.period_end],
       later_period:[newer.period_start,newer.period_end],
       citations:[old.source_url+'#page='+prevSystems.map(x=>old.cross_period.systems.find(y=>y.vendor===x.vendor&&y.deployment===x.deployment).page)[0],
        newer.source_url+'#page='+(newer.cross_period.transition_page&&checkedPage(newer,newer.cross_period.transition_page)?newer.cross_period.transition_page:newer.cross_period.systems[0].page)]
      });
     }
    }
   }
  }
  return events.sort((a,b)=>a.later_date.localeCompare(b.later_date)||a.type.localeCompare(b.type));
 }
 return {compare,source,originalUrl,metric};
});
