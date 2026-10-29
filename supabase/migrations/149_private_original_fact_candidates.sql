-- 149: machine-extracted government PDF institutional fact candidates, PRIVATE only.
-- Not signed contract evidence, payments, adopted policies or public events.
create table if not exists public.flock_original_fact_candidates (
 document_url text not null references public.flock_original_document_leads(document_url) on delete cascade,
 content_sha256 text not null check (content_sha256 ~ '^[a-f0-9]{64}$'),
 page_number integer not null check (page_number between 1 and 12),
 fact_type text not null check (fact_type in
   ('amount_candidate','retention_days_candidate','effective_date_candidate','sharing_terms_candidate')),
 normalized_value text not null check (length(normalized_value) between 1 and 35),
 verification_status text not null default 'requires_independent_page_review'
   check (verification_status in ('requires_independent_page_review','editorial_rejected','editorial_verified')),
 detected_at timestamptz not null default now(),
 primary key (document_url,content_sha256,page_number,fact_type,normalized_value)
);
create index if not exists flock_original_fact_candidates_status_idx
 on public.flock_original_fact_candidates(verification_status,detected_at);
alter table public.flock_original_fact_candidates enable row level security;
revoke all on public.flock_original_fact_candidates from public,anon,authenticated;
grant select,insert on public.flock_original_fact_candidates to service_role;
comment on table public.flock_original_fact_candidates is
 'Machine-extracted candidate numeric, term or date evidence without raw excerpts; independent original page review required, no automatic public promotion.';
