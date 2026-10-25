-- 088 vendor-primary data is public as historical claims, not coordinate data.
do $$
declare n integer;
begin
 select count(*) into n from public.flock_vendor_portal_snapshots
 where disclosure_status='verified_source_snapshot';
 if n<>9 then raise exception 'Expected exactly nine reviewed vendor snapshots'; end if;
 if not exists (
 select 1 from public.flock_vendor_portal_snapshots
 where agency_key='menifee_ca_pd' and source_date='2026-07-09'
   and reported_total_cameras=44
   and camera_count_scope='lpr_and_other_cameras'
   and reported_search_sessions_30d=204
   and portal_url='https://transparency.flocksafety.com/menifee-ca-pd'
 ) then raise exception 'Menifee vendor snapshot missing or misclassified'; end if;
 if not exists (
 select 1 from public.flock_vendor_portal_snapshots
 where agency_key='folsom_ca_pd' and reported_total_cameras is null
   and retention_days=121
 ) then raise exception 'Missing count must remain NULL, not zero'; end if;
 if exists (select 1 from public.flock_camera_locations
   where jurisdiction_label='Menifee, CA')
 then raise exception 'Vendor agency counts must not create any map pins'; end if;
 if not (select relrowsecurity from pg_class
   where oid='public.flock_vendor_portal_snapshots'::regclass)
 then raise exception 'Vendor snapshots missing row-level security'; end if;
 if has_table_privilege('anon','public.flock_vendor_portal_snapshots','INSERT')
    or has_table_privilege('authenticated','public.flock_vendor_portal_snapshots','INSERT')
    or has_table_privilege('service_role','public.flock_vendor_portal_snapshots','INSERT')
    or has_table_privilege('service_role','public.flock_vendor_portal_snapshots','UPDATE')
 then raise exception 'Unreviewed roles must not change published vendor claims'; end if;
 if not has_table_privilege('anon','public.flock_vendor_portal_snapshots','SELECT')
 then raise exception 'Vendor-primary snapshots must be publicly readable'; end if;
 raise notice 'Vendor-primary dated snapshot and no-coordinate boundary PASS';
end $$;
