-- 089: Four additional manually reviewed Flock-hosted portal snapshots.
-- One original first-party vendor portal per agency, not a scrape or a
-- camera-location authority. Keep historical metrics by their exact dates.
insert into public.flock_vendor_portal_snapshots
(agency_key,agency_label,state_code,portal_url,source_date,reported_total_cameras,
 retention_days,reported_search_sessions_30d,reported_hotlist_hits_30d,
 reported_vehicle_detections_30d)
values
('trophy_club_tx_pd','Trophy Club TX PD','TX','https://transparency.flocksafety.com/trophy-club-tx-pd','2026-07-24',10,30,32,852,180028),
('college_place_wa_pd','College Place WA PD','WA','https://transparency.flocksafety.com/college-place-wa-pd','2026-07-26',8,30,20,2,72960),
('indialantic_fl_pd','Indialantic FL PD','FL','https://transparency.flocksafety.com/indialantic-fl-pd','2026-07-23',14,30,21,null,181907),
('university_of_arizona_az_pd','University of Arizona Campus AZ PD','AZ','https://transparency.flocksafety.com/university-of-arizona-campus-az-pd','2026-07-23',59,30,36,null,153085)
on conflict (agency_key,source_date) do nothing;
