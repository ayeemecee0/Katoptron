-- M2 engineered source pipeline closure: privacy, indexed FK paths,
-- bounded fresh source-link scans, explicit manual document verification.
do $m2$
begin
 if to_regclass('public.m2_original_link_observations_document_fk_idx') is null
 or to_regclass('public.m2_original_content_review_receipt_version_fk_idx') is null
 then raise exception 'New M2 original-document FK indexes missing';end if;
 if not (select relrowsecurity from pg_class where oid='public.flock_original_pdf_content_triage'::regclass)
 or not (select relrowsecurity from pg_class where oid='public.flock_original_document_content_review_receipts'::regclass)
 then raise exception 'Original PDF triage or reviewed receipt RLS absent';end if;
 if has_table_privilege('anon','public.flock_original_document_content_review_receipts','SELECT')
 or has_table_privilege('service_role','public.flock_original_document_content_review_receipts','INSERT')
 or has_function_privilege('anon','public.record_original_document_link_scan(text,jsonb,text)','EXECUTE')
 then raise exception 'Private original-source governance boundary violated';end if;
 if not exists(select 1 from public.flock_original_document_leads l
 join public.flock_original_document_content_review_receipts r on r.document_url=l.document_url
 where l.review_status='document_content_verified'
 and r.scope_class='original_government_general_lpr_policy_only')
 then raise exception 'No specific, source-scoped human original-content review exists';end if;
 if exists(select 1 from public.flock_original_document_leads l
 where l.review_status='document_content_verified'
 and not exists(select 1 from public.flock_original_document_content_review_receipts r
 where r.document_url=l.document_url))
 then raise exception 'Promoted document lacks independent owner-reviewed content receipt';end if;
 if exists(select 1 from public.flock_original_pdf_content_triage
  where evidence_tier <> 'automated_private_unverified_indicators')
 then raise exception 'Private machine triage falsely promoted original content';end if;
end $m2$;
