begin;
do $$
begin
 if not (select relrowsecurity from pg_class
  where oid='public.flock_osm_quality_snapshots'::regclass) then
   raise exception 'Quality snapshot table must use RLS';
 end if;
 if not exists(select 1 from pg_class where
   oid='public.flock_public_osm_latest_quality'::regclass
   and reloptions @> array['security_invoker=true']::text[]) then
   raise exception 'Public quality report must run as invoker';
 end if;
 if has_table_privilege('anon','public.flock_osm_quality_snapshots','INSERT') or
    has_table_privilege('authenticated','public.flock_osm_quality_snapshots','DELETE') or
    has_table_privilege('service_role','public.flock_osm_quality_snapshots','UPDATE') or
    has_table_privilege('service_role','public.flock_osm_quality_snapshots','DELETE') then
   raise exception 'Only append-only source worker rights permitted';
 end if;
 if not has_table_privilege('anon','public.flock_public_osm_latest_quality','SELECT') then
   raise exception 'Community aggregate quality information not public';
 end if;
end $$;
insert into public.flock_osm_quality_snapshots(
 sync_at,source_snapshot_date,osm_observations,distinct_coordinates,
 colocated_extra_observations,colocated_coordinate_groups,osm_edits_older_365d,
 osm_edit_timestamp_missing,measurement_receipt_sha256
) values ('2026-10-24T12:00:00Z','2026-10-24',110000,109000,1000,900,20000,10,
 repeat('a',64));
set local role anon;
do $$
declare r record;
begin
 select * into r from public.flock_public_osm_latest_quality;
 if r.osm_observations<>110000 or r.distinct_coordinates<>109000 or
    r.colocated_extra_observations<>1000 or r.osm_edits_older_365d<>20000 then
   raise exception 'Read-only anon quality report changed source semantics';
 end if;
end $$;
reset role;
rollback;
