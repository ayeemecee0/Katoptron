/* Licensed EyesOnFlock directional sharing-network data, courtesy of
 * flockhopper3/deflock-data's independently validated public R2 exports.
 * Outbound A->[B] means agency A's own portal reportedly lists B as an
 * eligible search recipient. NOT proof that B accessed A, and never a
 * reciprocal edge unless B independently declares A.
 * CC BY-SA 4.0, see https://github.com/flockhopper3/deflock-data
 */
(function(root,factory){const api=factory();if(typeof module!=='undefined'&&module.exports)module.exports=api;if(root)root.KatoptronNetwork=api;})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const BASE='https://deflockdata.dontgetflocked.com/';
 const MAX_NODES=30000,MAX_EDGES=2500000;
 function validate(nodes,adj,meta){
  if(!nodes||nodes.type!=='FeatureCollection'||!Array.isArray(nodes.features)||
    nodes.features.length<5000||nodes.features.length>MAX_NODES||
    !adj||typeof adj!=='object'||Array.isArray(adj)||!meta||
    !Number.isInteger(meta.directedEdges)||meta.directedEdges<100000||
    meta.directedEdges>MAX_EDGES||meta.featureCount!==nodes.features.length||
    !/^20\d\d-\d\d-\d\dT/.test(meta.generatedAt||''))throw Error('External network source incomplete or missing provenance');
  const ids=new Map(),bySlug=new Map();
  for(const feature of nodes.features){
   const x=feature?.properties;
   if(!x||typeof x.id!=='string'||x.id.length>150||!x.id||ids.has(x.id)||
       typeof x.name!=='string'||typeof x.state!=='string')
    throw Error('Invalid or ambiguous external agency identity');
   ids.set(x.id,x);
   if(x.portalSlug&&x.isPortal)bySlug.set(x.portalSlug,x.id);
  }
  const inbound=new Map();let directed=0;
  for(const [src,targets] of Object.entries(adj)){
   if(!ids.has(src)||!Array.isArray(targets))throw Error('Sharing reference to unknown source');
   const seen=new Set();
   for(const dst of targets){
    if(!ids.has(dst)||dst===src||seen.has(dst))
     throw Error('Invalid directional sharing relationship');
    seen.add(dst);
    if(!inbound.has(dst))inbound.set(dst,[]);
    inbound.get(dst).push(src);directed++;
   }
  }
  if(directed!==meta.directedEdges)throw Error('Incomplete external source sharing list');
  const entry=Object.freeze({byId:ids,bySlug,adj,inbound,meta});
  return entry;
 }
 async function load(fetcher){
  const f=fetcher||(typeof fetch==='function'?fetch:null);
  if(!f)throw Error('No source fetch available');
  // Source is mirrored only AFTER server-side integrity and license checks.
  // Same-origin avoids blocking all agency data on third-party CORS/CDN.
  const local=typeof document!=='undefined'&&document.baseURI;
  const origin=local?new URL('./data/agency-intelligence/',document.baseURI).href:BASE;
  async function get(path){
   const r=await f(origin+path,{
    credentials:'omit',cache:'no-store',referrerPolicy:'no-referrer'});
   if(!r.ok)throw Error('Source-qualified agency network not yet published (HTTP '+r.status+')');
   return r.json();
  }
  const paths=local?['manifest.json','nodes.json','adjacency.json']:
    ['sharing-network-meta.json','sharing-network-nodes.geojson',
     'sharing-network-adjacency.json'];
  const [meta,nodes,adj]=await Promise.all(paths.map(get));
  return validate(nodes,adj,meta);
 }
 function details(network,id){
  if(!network?.byId?.has(id))return null;
  const outgoing=network.adj[id]||[],incoming=network.inbound.get(id)||[];
  const map=ids=>ids.map(x=>network.byId.get(x)).filter(Boolean);
  return {agency:network.byId.get(id),outgoing:map(outgoing),incoming:map(incoming),
    outboundCount:outgoing.length,inboundCount:incoming.length,
    snapshot:network.meta.generatedAt};
 }
 function matches(network,search,limit=80){
  if(!network||typeof search!=='string')return [];
  const term=search.trim().toLowerCase();
  if(term.length<2)return [];
  const arr=[];
  for(const node of network.byId.values()){
   if(node.isJunk||node.isInactive)continue;
   if([node.name,node.city,node.state,...(node.aliases||[])].some(x=>typeof x==='string'&&x.toLowerCase().includes(term))){
    arr.push(node);if(arr.length>=limit)break;
   }
  }
  return arr;
 }
 function municipality(network,key){
  // Strictest available locality match: canonical city/state, but the
  // source's node may refer to a distinct government/police operator.
  if(!network||!/^[-a-z0-9 ]+\|[A-Z]{2}$/.test(key||''))return [];
  const [name,state]=key.split('|');
  return [...network.byId.values()].filter(x=>
   x.isPortal===true&&!x.isJunk&&!x.isInactive&&x.state===state&&
   typeof x.city==='string'&&x.city.toLowerCase().trim()===name).slice(0,25);
 }
 return Object.freeze({BASE,validate,load,details,matches,municipality});
});
