-- M2 source discovery liveness is NOT document content verification.
do $permissions$
begin
 if not (select relrowsecurity from pg_class
    where oid='public.flock_original_document_link_observations'::regclass)
 or not (select relrowsecurity from pg_class
    where oid='public.flock_original_pdf_content_triage'::regclass)
 then raise exception 'Private discovery evidence RLS must be enabled';end if;
 if has_table_privilege('anon','public.flock_original_document_link_observations','SELECT')
 or has_table_privilege('authenticated','public.flock_original_pdf_content_triage','SELECT')
 or has_table_privilege('anon','public.flock_original_pdf_content_triage','INSERT')
 or has_function_privilege('anon','public.record_original_document_link_scan(text,jsonb,text)','EXECUTE')
 or has_function_privilege('authenticated','public.record_original_document_link_scan(text,jsonb,text)','EXECUTE')
 then raise exception 'Private M2 source lifecycle exposed to public';end if;
 if not has_function_privilege('service_role','public.record_original_document_link_scan(text,jsonb,text)','EXECUTE')
 then raise exception 'Source lifecycle cannot be maintained by service';end if;
 if not exists(select 1 from information_schema.columns
   where table_schema='public' and table_name='flock_original_acquisition_public_metrics'
   and column_name='pdf_content_triaged_documents')
 then raise exception 'PDF metadata conversion coverage absent';end if;
end $permissions$;
begin;
insert into public.flock_original_document_leads
 (document_url,government_page_url,jurisdiction_label,document_class,link_label,
 source_page_sha256)
values('https://testing.gov/synthetic-m2-policy.pdf','https://testing.gov/alpr',
'Synthetic City, CA','policy','Flock test policy PDF',repeat('a',64));
set local role service_role;
select public.record_original_document_link_scan('https://testing.gov/alpr',
 '["https://testing.gov/synthetic-m2-policy.pdf"]'::jsonb,repeat('b',64));
select public.record_original_document_link_scan('https://testing.gov/alpr',
 '[]'::jsonb,repeat('c',64));
do $check$
begin
 if not exists(select 1 from public.flock_original_document_link_observations
 where document_url='https://testing.gov/synthetic-m2-policy.pdf'
 and link_status='missing_once_after_successful_scan' and successful_absence_streak=1)
 then raise exception 'First successful publisher scan absence was not recorded';end if;
end $check$;
select public.record_original_document_link_scan('https://testing.gov/alpr',
 '[]'::jsonb,repeat('d',64));
do $check$
begin
 if not exists(select 1 from public.flock_original_document_link_observations
 where document_url='https://testing.gov/synthetic-m2-policy.pdf'
 and link_status='not_linked_after_two_successful_scans' and successful_absence_streak=2)
 then raise exception 'Two independent successful fetches not required';end if;
 if not exists(select 1 from public.flock_original_document_leads
 where document_url='https://testing.gov/synthetic-m2-policy.pdf'
 and review_status='requires_document_review')
 then raise exception 'Original document has been falsely promoted or revoked';end if;
end $check$;
select public.record_original_document_link_scan('https://testing.gov/alpr',
 '["https://testing.gov/synthetic-m2-policy.pdf"]'::jsonb,repeat('e',64));
do $check$
begin
 if not exists(select 1 from public.flock_original_document_link_observations
 where document_url='https://testing.gov/synthetic-m2-policy.pdf'
 and link_status='linked_on_last_successful_scan' and successful_absence_streak=0)
 then raise exception 'Original source reappearance was not reconciled';end if;
end $check$;
reset role;
rollback;
