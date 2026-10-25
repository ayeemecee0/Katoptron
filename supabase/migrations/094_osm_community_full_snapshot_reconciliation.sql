-- 094: Mark exact successfully processed community source observations by
-- per-run timestamp, then permit bounded deletion of absent observations.
-- Rights apply ONLY to the separate ODbL community source table.
alter table public.flock_osm_community_points
  add column if not exists last_seen_sync_at timestamptz not null default now();
create index if not exists flock_osm_community_last_sync_idx
  on public.flock_osm_community_points(last_seen_sync_at);
grant insert(last_seen_sync_at) on public.flock_osm_community_points to service_role;
grant update(osm_key,last_seen_sync_at) on public.flock_osm_community_points to service_role;
grant delete on public.flock_osm_community_points to service_role;
comment on column public.flock_osm_community_points.last_seen_sync_at is
'UTC synchronization batch marker. After all Flock-tagged OSM IDs are upserted and an exact PostgREST count matches, records absent from that full snapshot can be retired. Community tier only; no interaction with government GIS.';
