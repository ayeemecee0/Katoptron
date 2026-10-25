begin;
insert into public.flock_osm_community_points(osm_key,latitude,longitude,source_snapshot_date)
values ('node/77777881',38.50,-121.45,'2026-10-24'),
       ('node/77777882',38.70,-121.40,'2026-10-24'),
       ('node/77777883',39.50,-117.45,'2026-10-24');
do $qa$
begin
 if not exists(select 1 from pg_class
     where oid='public.flock_public_osm_community_density'::regclass
     and reloptions @> array['security_invoker=true']::text[]) then
   raise exception 'Community density view must be security-invoker';
 end if;
 if not has_table_privilege('anon','public.flock_public_osm_community_density','SELECT') then
   raise exception 'Public coarse community cells should be readable';
 end if;
 if (select count(*) from public.flock_public_osm_community_density)<>2
 or (select sum(community_report_count) from public.flock_public_osm_community_density)<>3 then
   raise exception 'Coarse community Flock density cells must count actual source observations';
 end if;
 if (select count(*) from public.flock_camera_locations
       where jurisdiction_label='Menifee, CA')<>0 then
    raise exception 'Community reports must not create official municipal GIS pins';
 end if;
 raise notice 'Nationwide community reporting-density grid PASS';
end $qa$;
rollback;
