begin;
do $$
begin
 if to_regclass('public.flock_government_vendor_directory') is null
 then raise exception 'Government vendor directory table missing';end if;
 if to_regclass('public.flock_public_government_vendor_directory') is null
 then raise exception 'Public government vendor directory view missing';end if;
 if not (select relrowsecurity from pg_class where oid='public.flock_government_vendor_directory'::regclass)
 then raise exception 'Government vendor directory RLS disabled';end if;
 if has_table_privilege('anon','public.flock_government_vendor_directory','INSERT')
    or has_table_privilege('authenticated','public.flock_government_vendor_directory','UPDATE')
 then raise exception 'Anonymous writes to government source links';end if;
 if not has_table_privilege('anon','public.flock_public_government_vendor_directory','SELECT')
 then raise exception 'Public direct-link directory not queryable';end if;
 if not exists(select 1 from pg_class where oid='public.flock_public_government_vendor_directory'::regclass
 and 'security_invoker=true'=any(reloptions))
 then raise exception 'Vendor source directory view bypasses caller RLS';end if;
end $$;
rollback;
