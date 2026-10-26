-- 132: Byte-level provenance for original government PDF documents.
-- PDF retrieval is NOT a content review, executed contract, policy
-- effective date, grant of data access or camera manufacturer attestation.
-- Never persist or publish downloaded document bytes or extracts.
create table if not exists public.flock_original_document_pdf_receipts (
  document_url text not null
    references public.flock_original_document_leads(document_url) on delete cascade,
  content_sha256 text not null check(content_sha256 ~ '^[0-9a-f]{64}$'),
  byte_length integer not null check(byte_length between 32 and 6000000),
  observed_media_type text not null check(observed_media_type = 'application/pdf'),
  evidence_tier text not null default 'downloaded_pdf_bytes_only'
    check(evidence_tier = 'downloaded_pdf_bytes_only'),
  first_observed_at timestamptz not null default now(),
  last_observed_at timestamptz not null default now(),
  primary key(document_url,content_sha256)
);
create index if not exists original_pdf_receipts_recent_idx
  on public.flock_original_document_pdf_receipts(last_observed_at desc);
alter table public.flock_original_document_pdf_receipts enable row level security;
revoke all on public.flock_original_document_pdf_receipts from public,anon,authenticated;
grant select,insert,update on public.flock_original_document_pdf_receipts to service_role;
comment on table public.flock_original_document_pdf_receipts is
'PRIVATE original government-hosted PDF SHA/byte receipts, with no raw document retained. Historical downloaded bytes only; no confirmation of any legal, financial, sharing or hardware fact.';

-- Private fair-scheduling ledger: outages are not revocation or evidence.
create table if not exists public.flock_original_pdf_attempts (
  document_url text primary key
    references public.flock_original_document_leads(document_url) on delete cascade,
  last_checked_at timestamptz not null,
  next_retry_at timestamptz not null,
  last_outcome text not null check(last_outcome in (
    'pdf_bytes_observed','held_fetch_error','held_non_pdf_or_invalid_bytes')),
  check(next_retry_at > last_checked_at)
);
alter table public.flock_original_pdf_attempts enable row level security;
revoke all on public.flock_original_pdf_attempts from public,anon,authenticated;
grant select,insert,update on public.flock_original_pdf_attempts to service_role;
comment on table public.flock_original_pdf_attempts is
'PRIVATE bounded original PDF byte rechecks; outages do not revoke historical provenance or source status.';

create table if not exists public.flock_original_pdf_scan_runs (
  scan_id uuid primary key default gen_random_uuid(),
  scanned_at timestamptz not null default now(),
  documents_attempted integer not null check(documents_attempted between 0 and 20),
  pdf_bytes_observed integer not null check(pdf_bytes_observed between 0 and 20),
  documents_held integer not null check(documents_held between 0 and 20),
  check(documents_attempted = pdf_bytes_observed + documents_held)
);
alter table public.flock_original_pdf_scan_runs enable row level security;
revoke all on public.flock_original_pdf_scan_runs from public,anon,authenticated;
grant select,insert on public.flock_original_pdf_scan_runs to service_role;

alter table public.flock_original_acquisition_public_metrics
  add column if not exists pdf_downloaded_unreviewed_documents integer not null
    default 0 check(pdf_downloaded_unreviewed_documents >= 0);
comment on column public.flock_original_acquisition_public_metrics.pdf_downloaded_unreviewed_documents is
'Count of distinct government original PDF URLs with historically retrieved bytes only, NOT independently content-reviewed or verified legal facts.';
