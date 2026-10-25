-- 096: Compact source-quality snapshots. Each row is a dated measurement of
-- the community OSM feed, not proof of current hardware placement or activity.
-- Read-only for browser clients; appended only after a full validated sync.
create table if not exists public.flock_osm_quality_snapshots (
 sync_at timestamptz primary key,
 source_snapshot_date date not null,
 osm_observations integer not null check (osm_observations between 90000 and 200000),
 distinct_coordinates integer not null check (distinct_coordinates between 1 and osm_observations),
 colocated_extra_observations integer not null check (colocated_extra_observations=osm_observations-distinct_coordinates),
 colocated_coordinate_groups integer not null check (colocated_coordinate_groups between 0 and distinct_coordinates),
 osm_edits_older_365d integer not null check(osm_edits_older_365d between 0 and osm_observations),
 osm_edit_timestamp_missing integer not null check(osm_edit_timestamp_missing between 0 and osm_observations),
 measurement_receipt_sha256 text not null check(measurement_receipt_sha256 ~ '^[0-9a-f]{64}$'),
 source_label text not null default 'OSM-derived DeFlock open ALPR feed'
   check(source_label='OSM-derived DeFlock open ALPR feed'),
 source_license text not null default 'ODbL 1.0' check(source_license='ODbL 1.0')
);
alter table public.flock_osm_quality_snapshots enable row level security;
revoke all on public.flock_osm_quality_snapshots from public,anon,authenticated,service_role;
grant select on public.flock_osm_quality_snapshots to anon,authenticated,service_role;
grant insert(sync_at,source_snapshot_date,osm_observations,
 distinct_coordinates,colocated_extra_observations,colocated_coordinate_groups,
 osm_edits_older_365d,osm_edit_timestamp_missing,measurement_receipt_sha256)
 on public.flock_osm_quality_snapshots to service_role;
create policy public_reviewed_osm_quality_snapshots
 on public.flock_osm_quality_snapshots for select to anon,authenticated
 using (source_label='OSM-derived DeFlock open ALPR feed' and source_license='ODbL 1.0');

create or replace view public.flock_public_osm_latest_quality
 with (security_invoker=true) as
select sync_at,source_snapshot_date,osm_observations,distinct_coordinates,
 colocated_extra_observations,colocated_coordinate_groups,osm_edits_older_365d,
 osm_edit_timestamp_missing,source_label,source_license
from public.flock_osm_quality_snapshots
order by sync_at desc limit 1;
revoke all on public.flock_public_osm_latest_quality from public,anon,authenticated,service_role;
grant select on public.flock_public_osm_latest_quality to anon,authenticated,service_role;

-- Backfill exactly one historical measurement from the existing synchronized
-- source. Future snapshot writes are performed by the bounded importer.
insert into public.flock_osm_quality_snapshots (
 sync_at,source_snapshot_date,osm_observations,distinct_coordinates,
 colocated_extra_observations,colocated_coordinate_groups,osm_edits_older_365d,
 osm_edit_timestamp_missing,measurement_receipt_sha256
)
with grouped as (
 select latitude,longitude,count(*) as n
 from public.flock_osm_community_points group by latitude,longitude
), current_source as (
 select max(last_seen_sync_at) sync_at,max(source_snapshot_date) source_snapshot_date,
   count(*)::integer osm_observations,
   count(*) filter(where source_timestamp < now()-interval '365 days')::integer osm_edits_older_365d,
   count(*) filter(where source_timestamp is null)::integer osm_edit_timestamp_missing
 from public.flock_osm_community_points
), clusters as (
 select count(*)::integer distinct_coordinates,
  coalesce(sum(n-1),0)::integer colocated_extra_observations,
  count(*) filter(where n>1)::integer colocated_coordinate_groups from grouped
)
select s.sync_at,s.source_snapshot_date,s.osm_observations,c.distinct_coordinates,
 c.colocated_extra_observations,c.colocated_coordinate_groups,
 s.osm_edits_older_365d,s.osm_edit_timestamp_missing,
 encode(extensions.digest(s.sync_at::text||':'||s.osm_observations::text||':'||c.distinct_coordinates::text,
   'sha256'),'hex')
from current_source s cross join clusters c
where s.osm_observations between 90000 and 200000 and s.sync_at is not null
on conflict (sync_at) do nothing;

comment on table public.flock_osm_quality_snapshots is
'Historical OSM community source measurements after full successful imports: same-coordinate observations are potential overlaps, not confirmed duplicate devices. Old OSM edit dates do not imply inactive cameras. Not a government-source camera count.';
