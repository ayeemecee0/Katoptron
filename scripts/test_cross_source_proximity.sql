do $test$
declare a int;b int;
begin
 if not exists (select 1 from pg_class
   where oid='public.flock_public_cross_source_proximity'::regclass
   and reloptions @> array['security_invoker=true']::text[]) then
  raise exception 'Cross-source proximity view must enforce invoker RLS';
 end if;
 if not has_table_privilege('anon','public.flock_public_cross_source_proximity','SELECT') then
  raise exception 'Proximity classifications must be publicly readable';
 end if;
 if has_table_privilege('anon','public.flock_public_cross_source_proximity','UPDATE') then
  raise exception 'Anonymous visitors must not be able to edit cross-source matches';
 end if;
 select count(*) into a from public.flock_public_cross_source_proximity;
 select count(*) into b from public.flock_camera_locations
  where verification_status='verified' and location_accuracy='exact';
 if a<>b then
  raise exception 'Cross-source join duplicated or dropped original-government pins';
 end if;
 if exists (select 1 from public.flock_public_cross_source_proximity
   where matching_status not in
    ('no_nearby_osm','possible_spatial_overlap','ambiguous_nearby_osm')
   or (matching_status='possible_spatial_overlap' and osm_observations_within_30m<>1)
   or (matching_status='ambiguous_nearby_osm' and osm_observations_within_30m<2)
   or (matching_status='no_nearby_osm' and osm_observations_within_30m<>0)
   or (nearest_osm_key is not null and separation_m>30.0)) then
  raise exception 'Ambiguous OSM proximity cannot become confirmed matching';
 end if;
 raise notice 'Independent OSM/community 30m possible-overlap classifications PASS';
end $test$;
