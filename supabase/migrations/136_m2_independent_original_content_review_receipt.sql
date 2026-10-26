-- 136: independent original-document CONTENT review receipt.
-- This is a narrowly verified Alexandria *general LPR* policy document.
-- It does NOT name Flock; no Flock retention, sharing grant, cameras or
-- executed contracts can be inferred from this document alone.
create table if not exists public.flock_original_document_content_review_receipts(
 document_url text primary key references public.flock_original_document_leads(document_url) on delete restrict,
 content_sha256 text not null check(content_sha256 ~ '^[0-9a-f]{64}$'),
 reviewed_on date not null default current_date,
 government_publisher text not null check(length(government_publisher) between 5 and 180),
 document_identity text not null check(length(document_identity) between 20 and 250),
 scope_class text not null check(scope_class in ('original_government_general_lpr_policy_only','original_government_flock_specific_content')),
 pages_reviewed text not null check(length(pages_reviewed) between 3 and 90),
 independently_supported_statement text not null check(length(independently_supported_statement) between 40 and 950),
 review_basis text not null default 'manual_original_government_document_pages'
  check(review_basis='manual_original_government_document_pages'),
 foreign key(document_url,content_sha256) references
  public.flock_original_document_pdf_receipts(document_url,content_sha256)
);
alter table public.flock_original_document_content_review_receipts enable row level security;
revoke all on public.flock_original_document_content_review_receipts
 from public,anon,authenticated,service_role;
comment on table public.flock_original_document_content_review_receipts is
'Owner-reviewed narrow original document contents with a version-specific PDF receipt. This is NOT a signed contract, named sharing partner, hardware manufacturer, or present permission verifier. Only database owner may write.';

-- Background source-acquisition keys must not self-certify document content.
create or replace function public.guard_original_document_content_promotion()
 returns trigger language plpgsql security invoker set search_path = ''
as $guard$
begin
 if new.review_status='document_content_verified'
    and old.review_status is distinct from new.review_status
    and current_user='service_role' then
   raise exception 'Only database-owner-reviewed original content can be promoted';
 end if;
 return new;
end;$guard$;
revoke all on function public.guard_original_document_content_promotion()
 from public,anon,authenticated,service_role;
drop trigger if exists guard_original_document_content_promotion
 on public.flock_original_document_leads;
create trigger guard_original_document_content_promotion
before update of review_status on public.flock_original_document_leads
for each row execute function public.guard_original_document_content_promotion();

-- Source document inspected visually from Alexandria PD's original 7-page
-- Directive 10.40; original pages 1, 5, 6. No Flock brand appears in this
-- document. Current webpage may separately discuss Flock but cannot
-- change this document's manufacturer-specific evidence scope.
insert into public.flock_original_document_content_review_receipts
(document_url,content_sha256,reviewed_on,government_publisher,document_identity,
 scope_class,pages_reviewed,independently_supported_statement)
select 'https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf',
       p.content_sha256,current_date,
       'Alexandria Police Department, Virginia',
       'Directive 10.40, License Plate Reader Program, effective October 28 2025',
       'original_government_general_lpr_policy_only','1,5,6',
       'The Alexandria Police Department published Directive 10.40 effective October 28, 2025. The original PDF states LPR data retention is generally no longer than 21 days and describes lawful LPR data-sharing limits. The document does not identify a Flock-branded device, establish any current recipient sharing grant, or authenticate deployed hardware.'
from public.flock_original_document_pdf_receipts p
where p.document_url='https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf'
  and p.content_sha256='83afdded0ea717a44a7969c1487e2a30bac1285c9d98c2f83622eabcfff05ea4'
  and exists(select 1 from public.flock_original_pdf_content_triage t
     where t.document_url=p.document_url and t.content_sha256=p.content_sha256
       and t.triage_status='readable_document_indicators_only')
on conflict(document_url) do nothing;

do $assert$
begin
 if not exists(select 1 from public.flock_original_document_content_review_receipts
 where document_url='https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf'
   and scope_class='original_government_general_lpr_policy_only')
 then raise exception 'Original city content/version not present; hold review';end if;
end $assert$;

update public.flock_original_document_leads l
 set review_status='document_content_verified',checked_at=now()
 where l.document_url='https://www.alexandriava.gov/sites/default/files/2025-10/10.40_license_plate_reader.pdf'
 and l.document_class='policy'
 and exists(select 1 from public.flock_original_document_content_review_receipts r
            where r.document_url=l.document_url)
 and l.review_status='requires_document_review';

comment on column public.flock_original_document_leads.review_status is
'The document_content_verified state means ORIGINAL document text checked for specifically scoped claims; NOT necessarily Flock manufacturer-specific, signed contract, active sharing, device or retention proof. Per-file owner review receipt required.';
