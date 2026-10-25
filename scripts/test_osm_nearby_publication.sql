begin;
do $verify$
begin
 if not (select relrowsecurity from pg_class
   where oid='public.flock_osm_nearby_candidates'::regclass) or
    not (select relrowsecurity from pg_class
   where oid='public.flock_osm_nearby_snapshots'::regclass) then
   raise exception 'Nearby candidate source tables must enforce RLS';
 end if;
 if has_table_privilege('anon','public.flock_osm_nearby_candidates','INSERT')
 or has_table_privilege('anon','public.flock_osm_nearby_snapshots','UPDATE')
 or has_table_privilege('service_role','public.flock_osm_nearby_candidates','DELETE')
 or has_table_privilege('service_role','public.flock_osm_nearby_candidates','UPDATE')
 or has_column_privilege('service_role','public.flock_osm_nearby_snapshots','pair_count','UPDATE')
 then raise exception 'Candidate source grants are not append-only';
 end if;
 if not has_column_privilege('service_role','public.flock_osm_nearby_snapshots','published_at','UPDATE')
 then raise exception 'Worker must be able to finalize staged source';
 end if;
 if not exists(select 1 from pg_class
     where oid='public.flock_public_osm_nearby_search'::regclass
     and reloptions @> array['security_invoker=true']::text[]) then
    raise exception 'Public nearby view must use security_invoker';
 end if;
end $verify$;
insert into public.flock_osm_nearby_snapshots
(snapshot_id,source_snapshot_date,source_observations,pair_count,
 source_records_in_pairs,pairs_within_5m,pairs_5_to_15m)
values (repeat('a',64),'2026-10-25',116128,2,3,1,1);
insert into public.flock_osm_nearby_candidates
(snapshot_id,osm_key_a,osm_key_b,distance_m)
values (repeat('a',64),'node/10','node/11',4.20),
       (repeat('a',64),'node/11','node/12',12.50);
set local role anon;
do $test$
begin
 if exists(select 1 from public.flock_osm_nearby_snapshots)
 or exists(select 1 from public.flock_osm_nearby_candidates)
 or exists(select 1 from public.flock_public_osm_nearby_latest)
 or exists(select 1 from public.flock_public_osm_nearby_search) then
   raise exception 'Unpublished candidate snapshot leaked to public';
 end if;
end $test$;
reset role;
update public.flock_osm_nearby_snapshots set published_at='2026-10-25T14:00:00Z'
where snapshot_id=repeat('a',64);
set local role anon;
do $test$
declare info record;
begin
 select * into info from public.flock_public_osm_nearby_latest;
 if info.pair_count<>2 or info.pairs_within_5m<>1 or
    (select count(*) from public.flock_public_osm_nearby_search)<>2 or
    (select count(*) from public.flock_public_osm_nearby_search
      where osm_key_b='node/12' and distance_m>5)<>1 then
   raise exception 'Published OSM proximity candidate search incomplete';
 end if;
end $test$;
reset role;
rollback;
