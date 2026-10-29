-- Source-scoped, private, actionable classification of ALL acquired government links.
-- Classification never certifies text, contracts, adoption or Flock operations.
create table if not exists public.flock_original_lead_dispositions(
 document_url text primary key references public.flock_original_document_leads(document_url) on delete cascade,
 disposition text not null check (disposition in (
   'verified_original_content','rejected_generic_navigation',
   'held_original_pdf_acquisition','held_original_pdf_content_review',
   'held_original_web_content_review','held_original_csv_authentication',
   'held_original_other_file_review','held_government_context_review')),
 reason_code text not null,
 next_action text not null,
 document_class text not null,
 classified_at timestamptz not null default now()
);
create index if not exists flock_original_lead_dispositions_status_idx
 on public.flock_original_lead_dispositions(disposition);
alter table public.flock_original_lead_dispositions enable row level security;
revoke all on public.flock_original_lead_dispositions from public,anon,authenticated;
grant select,insert,update on public.flock_original_lead_dispositions to service_role;
comment on table public.flock_original_lead_dispositions is
 'Private automated link dispositions only; not reviewed original document content or verified government facts. Hold findings for independent content review.';
