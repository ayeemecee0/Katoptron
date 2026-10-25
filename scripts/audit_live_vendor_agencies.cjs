/* Live source acceptance: complete, fresh vendor-portal agency geography only.
 * Never fetches camera positions or writes to the database.
 */
const data=require('../vendor-agency-layer.js');
const ROOT='https://deflockdata.dontgetflocked.com/';
(async()=>{
  const fetcher=async path=>{
    const response=await fetch(ROOT+path,{signal:AbortSignal.timeout(25000),headers:{Accept:'application/json'}});
    if(!response.ok)throw Error('Public research source unavailable '+response.status);
    return response.json();
  };
  const meta=data.validateMeta(await fetcher('sharing-network-meta.json'));
  const rows=data.parseNodes(await fetcher('sharing-network-nodes.geojson'),meta);
  if(rows.length<700)throw Error('Only partial public transparency portals available');
  const states=new Set(rows.map(p=>p.slug.match(/-([a-z]{2})(?:-|$)/)?.[1]).filter(Boolean));
  console.log('NATIONAL VENDOR PORTAL SOURCE fresh_agency_centers',rows.length);
  console.log('NATIONAL VENDOR PORTAL SOURCE original_snapshot_portals',meta.portalCount);
  console.log('NATIONAL VENDOR PORTAL SOURCE source_snapshot',meta.generatedAt);
  console.log('NATIONAL VENDOR PORTAL SOURCE source_camera_coordinates_published',0);
  console.log('NATIONAL VENDOR PORTAL SOURCE verified_cameras_added',0);
})().catch(e=>{console.error('Vendor agency source check held:',e.message);process.exitCode=1});
