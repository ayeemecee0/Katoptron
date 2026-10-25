-- 088: First-party vendor disclosure snapshots, independent of government and GIS records.
-- Curated from individually inspected, publicly accessible official Flock
-- Safety transparency portals. This migration never harvests an API,
-- promotes camera coordinates, or implies devices are currently active.
create table if not exists public.flock_vendor_portal_snapshots (
 agency_key text not null check (agency_key ~ '^[a-z0-9_-]{5,80}$'),
 agency_label text not null check (length(agency_label) between 6 and 150),
 state_code text not null check (state_code ~ '^[A-Z]{2}$'),
 portal_url text not null check (
   portal_url ~ '^https://transparency[.]flocksafety[.]com/[a-z0-9-]+/?$'
   and length(portal_url) <= 250),
 source_date date not null check (source_date <= current_date),
 reported_total_cameras integer check (reported_total_cameras between 0 and 100000),
 camera_count_scope text not null default 'lpr_and_other_cameras'
   check (camera_count_scope = 'lpr_and_other_cameras'),
 retention_days integer check (retention_days between 0 and 3650),
 reported_search_sessions_30d bigint check (reported_search_sessions_30d >= 0),
 reported_hotlist_hits_30d bigint check (reported_hotlist_hits_30d >= 0),
 reported_vehicle_detections_30d bigint check (reported_vehicle_detections_30d >= 0),
 disclosure_status text not null default 'verified_source_snapshot'
   check (disclosure_status in ('verified_source_snapshot','withdrawn')),
 sourced_at timestamptz not null default now(),
 primary key (agency_key,source_date),
 unique (portal_url,source_date),
 check (reported_total_cameras is not null or retention_days is not null
        or reported_search_sessions_30d is not null
        or reported_hotlist_hits_30d is not null
        or reported_vehicle_detections_30d is not null)
);
create index if not exists flock_vendor_portal_snapshots_date_idx
 on public.flock_vendor_portal_snapshots(source_date desc);
alter table public.flock_vendor_portal_snapshots enable row level security;
revoke all on public.flock_vendor_portal_snapshots from public,anon,authenticated,service_role;
grant select on public.flock_vendor_portal_snapshots to anon,authenticated,service_role;
create policy published_vendor_primary_disclosures on public.flock_vendor_portal_snapshots
 for select to anon,authenticated
 using (disclosure_status='verified_source_snapshot');
comment on table public.flock_vendor_portal_snapshots is
'Curated dated Flock Safety self-reported public agency transparency snapshots. LPR AND OTHER camera totals, not georeferenced points. Rolling prior-30-day metrics are non-additive and not proof of current operation. No public or service-role write grants.';

insert into public.flock_vendor_portal_snapshots
(agency_key,agency_label,state_code,portal_url,source_date,reported_total_cameras,
 retention_days,reported_search_sessions_30d,reported_hotlist_hits_30d,
 reported_vehicle_detections_30d)
values
('menifee_ca_pd','Menifee CA PD','CA','https://transparency.flocksafety.com/menifee-ca-pd','2026-07-09',44,30,204,8017,564433),
('west_sacramento_ca_pd','West Sacramento CA PD','CA','https://transparency.flocksafety.com/west-sacramento-ca-pd','2026-07-23',32,30,583,null,580132),
('santa_clara_ca_pd','Santa Clara CA PD','CA','https://transparency.flocksafety.com/santa-clara-ca-pd','2026-06-29',54,30,null,null,null),
('menlo_park_ca_pd','Menlo Park CA PD','CA','https://transparency.flocksafety.com/menlo-park-ca-pd','2026-07-24',35,30,127,3539,841064),
('bell_ca_pd','Bell CA PD','CA','https://transparency.flocksafety.com/bell-ca-pd','2026-07-26',11,30,31,11155,479178),
('placer_county_ca_so','Placer County CA SO','CA','https://transparency.flocksafety.com/placer-county-ca-so','2026-07-24',72,30,1333,3677,1272298),
('pasadena_ca_pd','Pasadena CA PD','CA','https://transparency.flocksafety.com/pasadena-ca-pd','2026-07-23',61,30,500,13013,1018754),
('kern_county_ca_so','Kern County CA SO','CA','https://transparency.flocksafety.com/kern-county-ca-so-','2026-07-24',66,30,1623,16494,727727),
('folsom_ca_pd','Folsom CA PD','CA','https://transparency.flocksafety.com/folsom-ca-pd','2026-07-26',null,121,226,782,392386)
on conflict (agency_key,source_date) do nothing;
