-- Separate ODbL community mapping from canonical official-government camera claims.
begin;
do $qa$
begin
 if not (select relrowsecurity from pg_class
              where oid='public.flock_osm_community_points'::regclass) then
   raise exception 'Community Flock exact-point table requires RLS';
 end if;
 if not has_table_privilege('anon','public.flock_osm_community_points','SELECT')
    or has_table_privilege('anon','public.flock_osm_community_points','INSERT')
    or has_column_privilege('service_role','public.flock_osm_community_points','evidence_tier','INSERT')
    or has_column_privilege('service_role','public.flock_osm_community_points','evidence_tier','UPDATE')
    or has_column_privilege('service_role','public.flock_osm_community_points','claimed_manufacturer','UPDATE') then
  raise exception 'Unreviewed community workflow must not publish official/GIS status';
 end if;
 if not exists(select 1 from pg_class
   where oid='public.flock_public_osm_community_stats'::regclass
   and reloptions @> array['security_invoker=true']::text[]) then
   raise exception 'Community coverage stats view must respect caller RLS';
 end if;
end $qa$;
insert into public.flock_osm_community_points(osm_key,latitude,longitude,source_snapshot_date)
 values('node/998877665',38.5,-121.5,'2026-10-24');
do $qa$
begin
 if (select reported_flock_points from public.flock_public_osm_community_stats)<>1 then
   raise exception 'Public community count omits separately labeled point';
 end if;
 if exists (select 1 from public.flock_camera_locations
   where record_key='node/998877665') then
   raise exception 'Community OSM point became canonical government GIS point';
 end if;
end $qa$;
rollback;
