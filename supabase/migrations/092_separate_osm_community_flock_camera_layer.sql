-- 092: Separate OpenStreetMap community Flock camera observations.
-- This is an ODbL-derived, publicly readable dataset. Community records are
-- NOT manufacturer/government-verified GIS points and must never be counted
-- in the canonical flock_camera_locations inventory.
create table if not exists public.flock_osm_community_points (
 osm_key text primary key check (osm_key ~ '^(node|way)/[1-9][0-9]{0,17}$'),
 latitude double precision not null check (latitude between 17 and 72),
 longitude double precision not null check (longitude between -180 and -64),
 source_timestamp timestamptz,
 source_snapshot_date date not null check (source_snapshot_date<=current_date),
 claimed_manufacturer text not null default 'Flock Safety'
   check (claimed_manufacturer='Flock Safety'),
 evidence_tier text not null default 'community_osm'
   check (evidence_tier='community_osm'),
 source_license text not null default 'ODbL 1.0'
   check (source_license='ODbL 1.0'),
 imported_at timestamptz not null default now()
);
create index if not exists flock_osm_community_lat_lon_idx
 on public.flock_osm_community_points(latitude,longitude);
create index if not exists flock_osm_community_lon_lat_idx
 on public.flock_osm_community_points(longitude,latitude);
alter table public.flock_osm_community_points enable row level security;
revoke all on public.flock_osm_community_points from
 public,anon,authenticated,service_role;
grant select on public.flock_osm_community_points to anon,authenticated,service_role;
grant insert (osm_key,latitude,longitude,source_timestamp,source_snapshot_date)
 on public.flock_osm_community_points to service_role;
grant update (latitude,longitude,source_timestamp,source_snapshot_date,imported_at)
 on public.flock_osm_community_points to service_role;
create policy published_separately_labeled_osm_community_points
 on public.flock_osm_community_points for select to anon,authenticated
 using (evidence_tier='community_osm' and claimed_manufacturer='Flock Safety');
comment on table public.flock_osm_community_points is
'OpenStreetMap community-reported manufacturer-tagged Flock ALPR camera coordinates, © OSM contributors ODbL 1.0. Not official-source GIS, vendor affirmation, observed actual operation or detection. Consumers must keep this tier distinct from canonical government-verified points.';

create or replace view public.flock_public_osm_community_stats
with (security_invoker=true) as
select count(*)::integer as reported_flock_points,
       count(distinct source_snapshot_date)::integer as source_snapshot_dates,
       max(source_snapshot_date) as last_dataset_snapshot_date
from public.flock_osm_community_points;
revoke all on public.flock_public_osm_community_stats
 from public,anon,authenticated,service_role;
grant select on public.flock_public_osm_community_stats
 to anon,authenticated,service_role;
comment on view public.flock_public_osm_community_stats is
'OpenStreetMap community-labeled Flock exact coordinates, not canonical official GIS. Counts may overlap official and must not be added to verified government point counts.';
