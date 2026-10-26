-- Source acquisition must remain private until independently verified.
do $evidence$
begin
 if not (select relrowsecurity from pg_class where oid='public.flock_original_document_leads'::regclass)
 or not (select relrowsecurity from pg_class where oid='public.flock_original_sharing_extraction_candidates'::regclass)
 or not (select relrowsecurity from pg_class where oid='public.flock_original_document_scan_runs'::regclass)
 then raise exception 'Private government source intake RLS absent';end if;
 if has_table_privilege('anon','public.flock_original_document_leads','SELECT')
 or has_table_privilege('authenticated','public.flock_original_document_leads','SELECT')
 or has_table_privilege('anon','public.flock_original_sharing_extraction_candidates','SELECT')
 or has_table_privilege('authenticated','public.flock_original_sharing_extraction_candidates','INSERT')
 or has_table_privilege('anon','public.flock_original_document_scan_runs','SELECT')
 then raise exception 'Unreviewed document or named-sharing extraction data exposed';end if;
 if not has_table_privilege('service_role','public.flock_original_document_leads','INSERT')
 or not has_table_privilege('service_role','public.flock_original_sharing_extraction_candidates','INSERT')
 then raise exception 'Protected acquisition cannot queue original source research';end if;
 if not has_table_privilege('anon','public.flock_original_acquisition_public_metrics','SELECT')
 or has_table_privilege('anon','public.flock_original_acquisition_public_metrics','INSERT')
 or has_table_privilege('authenticated','public.flock_original_acquisition_public_metrics','UPDATE')
 then raise exception 'Public aggregate acquisition counts may be manipulated or unavailable';end if;
 if not (select relrowsecurity from pg_class where oid='public.flock_original_acquisition_public_metrics'::regclass)
 then raise exception 'Aggregate acquisition metrics need RLS';end if;
end $evidence$;
