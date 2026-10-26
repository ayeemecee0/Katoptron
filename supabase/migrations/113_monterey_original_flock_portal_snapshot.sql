-- M2 additional ORIGINAL Flock Safety vendor disclosure, NOT camera points.
-- Direct portal: https://transparency.flocksafety.com/monterey-ca-pd
-- Portal explicitly labels Total Cameras as "LPR and other cameras".
-- Snapshot date is the portal's displayed last-updated 2026-07-24, not a
-- real-time record, device/manufacturer inventory or installed-camera count.
-- The portal also links to the City of Monterey Police's original PDF map,
-- but its georeferencing and individual camera/device provenance have not
-- been authenticated; do not publish inferred coordinates from this source.
insert into public.flock_vendor_portal_snapshots
(agency_key,agency_label,state_code,portal_url,source_date,
 reported_total_cameras,camera_count_scope,retention_days,
 reported_search_sessions_30d,reported_hotlist_hits_30d,
 reported_vehicle_detections_30d)
values
('monterey_ca_pd','Monterey CA PD','CA',
 'https://transparency.flocksafety.com/monterey-ca-pd','2026-07-24',
 37,'lpr_and_other_cameras',30,113,1752,499980)
on conflict(agency_key,source_date) do nothing;
