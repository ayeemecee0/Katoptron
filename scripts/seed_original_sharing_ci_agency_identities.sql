-- Disposable validation fixture ONLY: upstream licensed secondary directory is
-- imported by protected GitHub automation in production, not migrations.
-- Originals seed needs publisher identities to satisfy foreign keys.
insert into public.flock_secondary_portal_agencies(
 source_agency_id,agency_name,state_code,agency_type,is_reporting_portal,
 portal_slug,source_snapshot_at,source_url,source_tier,source_license)
values
 ('elk-grove-ca-pd','Elk Grove CA PD','CA','police',false,null,
  '2026-10-19T12:00:00Z','https://deflockdata.dontgetflocked.com/sharing-network-nodes.geojson',
  'secondary_aggregated_portal_snapshot','CC BY-SA 4.0'),
 ('woodland-ca-pd','Woodland CA PD','CA','police',false,null,
  '2026-10-19T12:00:00Z','https://deflockdata.dontgetflocked.com/sharing-network-nodes.geojson',
  'secondary_aggregated_portal_snapshot','CC BY-SA 4.0'),
 ('mill-valley-ca-pd','Mill Valley CA PD','CA','police',true,'mill-valley-ca-pd',
  '2026-10-19T12:00:00Z','https://deflockdata.dontgetflocked.com/sharing-network-nodes.geojson',
  'secondary_aggregated_portal_snapshot','CC BY-SA 4.0'),
 ('los-altos-ca-pd','Los Altos CA PD','CA','police',true,'los-altos-ca-pd',
  '2026-10-19T12:00:00Z','https://deflockdata.dontgetflocked.com/sharing-network-nodes.geojson',
  'secondary_aggregated_portal_snapshot','CC BY-SA 4.0'),
 ('snohomish-county-wa-so','Snohomish County WA SO','WA','sheriff',true,'snohomish-county-wa-so-',
  '2026-10-19T12:00:00Z','https://deflockdata.dontgetflocked.com/sharing-network-nodes.geojson',
  'secondary_aggregated_portal_snapshot','CC BY-SA 4.0'),
 ('city-of-las-vegas-nv-department-of-public-safety','City of Las Vegas NV Department of Public Safety','NV','police',false,null,
  '2026-10-19T12:00:00Z','https://deflockdata.dontgetflocked.com/sharing-network-nodes.geojson',
  'secondary_aggregated_portal_snapshot','CC BY-SA 4.0'),
 ('folsom-ca-pd','Folsom CA PD','CA','police',true,'folsom-ca-pd',
  '2026-10-19T12:00:00Z','https://deflockdata.dontgetflocked.com/sharing-network-nodes.geojson',
  'secondary_aggregated_portal_snapshot','CC BY-SA 4.0');
