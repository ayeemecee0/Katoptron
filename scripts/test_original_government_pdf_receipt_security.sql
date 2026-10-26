-- Acquired PDF bytes never become a public report or verified contract.
do $security$
begin
 if not (select relrowsecurity from pg_class where
   oid='public.flock_original_document_pdf_receipts'::regclass)
 or not (select relrowsecurity from pg_class where
   oid='public.flock_original_pdf_attempts'::regclass)
 or not (select relrowsecurity from pg_class where
   oid='public.flock_original_pdf_scan_runs'::regclass)
 then raise exception 'Private government PDF byte acquisition RLS absent'; end if;
 if has_table_privilege('anon','public.flock_original_document_pdf_receipts','SELECT')
 or has_table_privilege('authenticated','public.flock_original_document_pdf_receipts','SELECT')
 or has_table_privilege('anon','public.flock_original_pdf_attempts','SELECT')
 or has_table_privilege('authenticated','public.flock_original_pdf_attempts','UPDATE')
 or has_table_privilege('anon','public.flock_original_pdf_scan_runs','SELECT')
 then raise exception 'Private original PDF byte receipts accidentally exposed';end if;
 if not has_table_privilege('service_role',
   'public.flock_original_document_pdf_receipts','INSERT')
 or not has_table_privilege('service_role',
   'public.flock_original_pdf_attempts','UPDATE')
 then raise exception 'Private source-acquisition job cannot write receipts or retries';end if;
 if not exists (select 1 from information_schema.columns
  where table_schema='public'
    and table_name='flock_original_acquisition_public_metrics'
    and column_name='pdf_downloaded_unreviewed_documents')
 then raise exception 'Original PDF byte metric missing';end if;
 if has_table_privilege('anon','public.flock_original_acquisition_public_metrics','UPDATE')
 then raise exception 'Anonymous users must not overwrite public acquisition metrics';end if;
end;
$security$;
