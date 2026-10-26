-- M2 exact original PDF review conversion, privacy and no false Flock claims.
do $m2$
begin
 if not (select relrowsecurity from pg_class where
 oid='public.flock_original_document_content_review_receipts'::regclass)
 or has_table_privilege('anon','public.flock_original_document_content_review_receipts','SELECT')
 or has_table_privilege('authenticated','public.flock_original_document_content_review_receipts','SELECT')
 or has_table_privilege('service_role','public.flock_original_document_content_review_receipts','INSERT')
 then raise exception 'Owner original document review receipt exposed';end if;
 if (select count(*) from public.flock_original_document_content_review_receipts
     where scope_class='original_government_general_lpr_policy_only')<1
 then raise exception 'No reviewed original general LPR policy';end if;
 if not exists(select 1 from public.flock_original_document_leads l
 join public.flock_original_document_content_review_receipts r on r.document_url=l.document_url
 join public.flock_original_document_pdf_receipts p on p.document_url=r.document_url
  and p.content_sha256=r.content_sha256
 where l.document_url='https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf'
 and l.review_status='document_content_verified'
 and l.document_class='policy'
 and r.scope_class='original_government_general_lpr_policy_only')
 then raise exception 'Document content verified without original government scope and hash';end if;
 if exists(select 1 from public.flock_original_document_content_review_receipts
 where scope_class='original_government_flock_specific_content'
 and document_url='https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf')
 then raise exception 'Generic ALPR policy was falsely promoted to Flock manufacturer evidence';end if;
end $m2$;
begin;
update public.flock_original_document_leads
 set review_status='requires_document_review'
 where document_url='https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf';
set local role service_role;
do $negative$
begin
 begin
  update public.flock_original_document_leads set review_status='document_content_verified'
   where document_url='https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf';
  raise exception 'Automated service was allowed to self-verify government document content';
 exception when others then
  if sqlerrm not like 'Only database-owner-reviewed original content can be promoted%' then raise;end if;
 end;
end $negative$;
reset role;
rollback;
