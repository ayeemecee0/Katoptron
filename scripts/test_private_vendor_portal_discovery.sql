do $$
begin
 if not (select relrowsecurity from pg_class
    where oid='public.flock_vendor_portal_source_leads'::regclass) then
  raise exception 'Original agency portal lead queue must use RLS';
 end if;
 if has_table_privilege('anon','public.flock_vendor_portal_source_leads','SELECT')
 or has_table_privilege('authenticated','public.flock_vendor_portal_source_leads','SELECT')
 or has_table_privilege('anon','public.flock_vendor_portal_source_leads','INSERT')
 or has_table_privilege('authenticated','public.flock_vendor_portal_source_leads','INSERT') then
  raise exception 'Unreviewed source leads cannot be publicly accessible';
 end if;
 if not has_table_privilege('service_role','public.flock_vendor_portal_source_leads','SELECT')
 or not has_column_privilege('service_role','public.flock_vendor_portal_source_leads','portal_url','INSERT')
 or has_column_privilege('service_role','public.flock_vendor_portal_source_leads','review_status','UPDATE')
 or has_column_privilege('service_role','public.flock_vendor_portal_source_leads','review_status','INSERT') then
  raise exception 'Private worker cannot approve its own discovered portal leads';
 end if;
 if (select count(*) from public.flock_vendor_portal_source_leads)<>0 then
  raise exception 'Migration created unapproved research leads';
 end if;
 raise notice 'Private agency hyperlink discovery queue permissions PASS';
end $$;
