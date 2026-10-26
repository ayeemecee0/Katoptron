/* Katoptron Agency X-Ray and Local Government Watch.
 * Read-only published evidence only. No inferred camera/device attribution.
 * An agency-name match is a locality grouping, not proof of agency identity.
 * Follows are stored locally in the browser, never transmitted to Katoptron.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.KatoptronIntelligence=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const MAX=10,STORAGE='katoptron-city-watch-v1';
 function locality(label){
  if(typeof label!=='string'||label.length>190)return null;
  const x=label.trim().replace(/\s+/g,' ');
  let m=/^(.+?),\s*([A-Z]{2})$/.exec(x);
  if(!m)m=/^(.+?)\s+([A-Z]{2})\s+(?:PD|SO)$/.exec(x);
  if(!m)return null;
  const area=m[1].trim().toLowerCase().replace(/[^a-z0-9 ]/g,'').replace(/\s+/g,' ');
  return area&&/^[A-Z]{2}$/.test(m[2])?area+'|'+m[2]:null;
 }
 function labelForKey(key){
  if(!/^[a-z0-9 ]+\|[A-Z]{2}$/.test(key||''))return 'Unknown locality';
  const [area,state]=key.split('|');
  return area.replace(/\b[a-z]/g,m=>m.toUpperCase())+', '+state;
 }
 function normalize(row,source){
  if(!row||typeof row!=='object')return null;
  const name=source==='portal'?row.agency_label:source==='secondary'?row.agency_name:row.jurisdiction_label;
  const key=locality(name);
  if(!key)return null;
  return {key,source,row};
 }
 function build(events,portals,cameras,programs,secondary=[]){
  if(![events,portals,cameras,programs,secondary].every(Array.isArray))
   throw Error('Incomplete published agency evidence');
  const map=new Map();
  function include(source,rows){
   for(const row of rows){
    const rec=normalize(row,source);
    if(!rec)continue;
    if(!map.has(rec.key))map.set(rec.key,{
      key:rec.key,label:labelForKey(rec.key),
      events:[],portals:[],cameras:[],programs:[],secondary:[],matchedLabels:new Set()});
    const entry=map.get(rec.key);
    entry[source==='event'?'events':source==='portal'?'portals':source==='camera'?'cameras':source==='secondary'?'secondary':'programs'].push(row);
    entry.matchedLabels.add(source+':'+(row.jurisdiction_label||row.agency_label||row.agency_name));
   }
  }
  include('event',events);
  include('portal',portals.filter(x=>x.disclosure_status==='verified_source_snapshot'));
  include('camera',cameras.filter(x=>x.verification_status==='verified'&&x.location_accuracy==='exact'));
  include('program',programs.filter(x=>x.record_status==='verified'));
  include('secondary',secondary.filter(x=>x.is_reporting_portal===true&&x.source_tier==='secondary_aggregated_portal_snapshot'))
  return [...map.values()].sort((a,b)=>a.label.localeCompare(b.label));
 }
 function sourceDate(row){return String(row.event_date||row.source_date||'').slice(0,10)}
 function updateItems(group){
  if(!group)return [];
  return [
   ...group.events.filter(r=>r.event_date&&r.event_key).map(r=>({
     id:'gov:'+r.event_key+':'+r.event_date,date:r.event_date,
     type:'Government record',title:r.title,source_url:r.source_url,
     confidence:'Government record; event date basis: '+(r.date_basis||'source-dated')
   })),
   ...group.portals.filter(r=>r.source_date&&r.portal_url).map(r=>({
     id:'vendor:'+r.agency_key+':'+r.source_date,date:r.source_date,
     type:'Vendor disclosure',title:r.agency_label+' source snapshot',
     source_url:r.portal_url,
     confidence:'Source-dated Flock vendor claims; not verified active camera inventory'
   }))
  ].sort((a,b)=>b.date.localeCompare(a.date)||a.id.localeCompare(b.id));
 }
 function safeRead(){
  if(typeof localStorage==='undefined')return {follows:[],seen:{}};
  try{
   const v=JSON.parse(localStorage.getItem(STORAGE)||'{}');
   return {follows:Array.isArray(v.follows)?v.follows.filter(x=>/^[a-z0-9 ]+\|[A-Z]{2}$/.test(x)).slice(0,50):[],
      seen:v.seen&&typeof v.seen==='object'&&!Array.isArray(v.seen)?v.seen:{}};
  }catch{return {follows:[],seen:{}}}
 }
 function safeWrite(data){
  if(typeof localStorage==='undefined')return false;
  try{localStorage.setItem(STORAGE,JSON.stringify(data));return true}catch{return false}
 }
 function follow(key){
  if(!/^[a-z0-9 ]+\|[A-Z]{2}$/.test(key||''))throw Error('Invalid locality key');
  const s=safeRead();
  if(!s.follows.includes(key)){s.follows.push(key);s.follows=s.follows.slice(-50)}
  return safeWrite(s);
 }
 function unfollow(key){
  const s=safeRead();s.follows=s.follows.filter(x=>x!==key);
  delete s.seen[key];return safeWrite(s);
 }
 function changes(group,state){
  const seen=new Set(Array.isArray(state?.seen?.[group.key])?state.seen[group.key]:[]);
  return updateItems(group).filter(x=>!seen.has(x.id));
 }
 function markSeen(group){
  const s=safeRead();
  s.seen[group.key]=updateItems(group).map(x=>x.id).slice(0,350);
  return safeWrite(s);
 }
 function safeUrl(url){
  try{
   const u=new URL(url);
   return u.protocol==='https:'&&!u.username&&!u.password?u.href:null;
  }catch{return null}
 }
 async function published(table,select,where='',limit=500){
  const cfg=typeof window!=='undefined'?window.KATOPTRON_CONFIG:null;
  if(!cfg?.supabaseUrl||!cfg?.supabasePublishableKey)throw Error('Public evidence service unavailable');
  const rows=[];
  for(let offset=0;offset<10000;offset+=limit){
    const q=new URLSearchParams({select,limit:String(limit),offset:String(offset)});
    if(where){const pairs=where.split('&');for(const part of pairs){
       const at=part.indexOf('=');if(at!==-1)q.append(part.slice(0,at),part.slice(at+1))
    }}
    const r=await fetch(cfg.supabaseUrl+'/rest/v1/'+table+'?'+q,{
     headers:{apikey:cfg.supabasePublishableKey},cache:'no-store',referrerPolicy:'no-referrer'});
    if(!r.ok)throw Error('Published evidence endpoint '+table+' HTTP '+r.status);
    const batch=await r.json();
    if(!Array.isArray(batch))throw Error('Invalid public evidence response '+table);
    rows.push(...batch);
    if(batch.length<limit)return rows;
  }
  throw Error('Public evidence pagination truncated; cannot claim complete inventory');
 }
 async function load(){
  const [events,portals,cameras,programs,secondary]=await Promise.all([
    published('flock_accountability_events','event_key,event_type,jurisdiction_label,event_date,date_basis,title,summary,source_url,amount_usd,camera_count'),
    published('flock_vendor_portal_snapshots','agency_key,agency_label,state_code,portal_url,source_date,reported_total_cameras,camera_count_scope,retention_days,reported_search_sessions_30d,reported_hotlist_hits_30d,disclosure_status','disclosure_status=eq.verified_source_snapshot'),
    published('flock_camera_locations','record_key,jurisdiction_label,verification_status,location_accuracy,source_url,evidence_summary','verification_status=eq.verified&location_accuracy=eq.exact'),
    published('flock_documented_programs','program_key,jurisdiction_label,record_status,source_date,program_status,official_evidence_url,official_camera_map_url','record_status=eq.verified'),
    published('flock_secondary_portal_agencies','source_agency_id,agency_name,state_code,agency_type,is_reporting_portal,portal_slug,source_reported_mixed_cameras,source_reported_network_links,source_snapshot_at,source_url,source_tier','is_reporting_portal=eq.true')
  ]);
  return build(events,portals,cameras,programs,secondary);
 }
 return Object.freeze({locality,labelForKey,build,updateItems,safeRead,follow,
   unfollow,changes,markSeen,load,safeUrl,sourceDate});
});
