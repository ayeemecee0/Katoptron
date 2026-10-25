-- Only server-owned original government camera-map leads can be written.
begin;
do $$
begin
 if not (select relrowsecurity from pg_class
  where oid='public.flock_government_camera_map_app_leads'::regclass)
 then raise exception 'Government map leads must be private RLS';end if;
 if not (select relrowsecurity from pg_class
  where oid='public.flock_government_camera_map_app_receipts'::regclass)
 then raise exception 'Government map source receipts must be private RLS';end if;
 if has_table_privilege('anon','public.flock_government_camera_map_app_leads','SELECT')
    or has_table_privilege('authenticated','public.flock_government_camera_map_app_leads','SELECT')
    or has_table_privilege('anon','public.flock_government_camera_map_app_receipts','SELECT')
    or has_table_privilege('authenticated','public.flock_government_camera_map_app_receipts','INSERT')
 then raise exception 'Original government camera-map private leads exposed';end if;
 if not has_table_privilege('service_role','public.flock_government_camera_map_app_leads','SELECT')
    or not has_table_privilege('service_role','public.flock_government_camera_map_app_receipts','SELECT')
 then raise exception 'Private source-staging role lacks read permissions';end if;
end $$;
rollback;
