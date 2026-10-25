begin;
do $proof$
begin
 if not (select relrowsecurity from pg_class
  where oid='public.flock_osm_community_points'::regclass) then
  raise exception 'OSM community reconciliation must retain RLS';
 end if;
 if has_table_privilege('anon','public.flock_osm_community_points','DELETE')
    or has_table_privilege('authenticated','public.flock_osm_community_points','UPDATE')
    or has_table_privilege('anon','public.flock_osm_community_points','UPDATE') then
  raise exception 'Public roles must not mutate OSM community data';
 end if;
 if not has_table_privilege('service_role','public.flock_osm_community_points','DELETE')
 or not has_column_privilege('service_role','public.flock_osm_community_points','last_seen_sync_at','UPDATE')
 or not has_column_privilege('service_role','public.flock_osm_community_points','latitude','UPDATE')
 or has_column_privilege('service_role','public.flock_osm_community_points','evidence_tier','UPDATE') then
  raise exception 'Bounded service role reconciliation rights invalid';
 end if;
end $proof$;
insert into public.flock_osm_community_points(osm_key,latitude,longitude,source_snapshot_date)
values('node/12345601',38.1,-121.1,'2026-10-24'),
      ('node/12345602',38.2,-121.2,'2026-10-24');
set local role service_role;
update public.flock_osm_community_points
  set latitude=38.3,last_seen_sync_at='2026-10-25T04:00:00Z'
  where osm_key='node/12345601';
delete from public.flock_osm_community_points
  where osm_key='node/12345602' and last_seen_sync_at<>'2026-10-25T04:00:00Z';
do $proof$
begin
 if not exists(select 1 from public.flock_osm_community_points
   where osm_key='node/12345601' and latitude=38.3 and
    last_seen_sync_at='2026-10-25T04:00:00Z') then
   raise exception 'Community record relocation and refresh failed';
 end if;
 if exists(select 1 from public.flock_osm_community_points
   where osm_key='node/12345602') then
   raise exception 'Stale community source identity not retired';
 end if;
end $proof$;
reset role;
rollback;
