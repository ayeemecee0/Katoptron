-- 145: Machine-generated, private fingerprints of public Minnesota ALPR audit PDFs.
-- Data is ingestion diagnostics only. No extracted people, addresses, plate reads,
-- legality/compliance conclusions, vendor authorization, or published claims.
create table if not exists public.flock_private_mn_flock_audit_pdf_receipts (
 source_url text primary key references public.flock_public_mn_alpr_audit_registry(source_url) on delete restrict,
 source_sha256 text not null check (source_sha256 ~ '^[0-9a-f]{64}$'),
 file_bytes integer not null check (file_bytes between 150 and 2500000),
 pages integer not null check (pages between 1 and 20),
 state_archive_title text not null check (length(state_archive_title) between 18 and 400),
 machine_flags jsonb not null default '{}'::jsonb
   check (jsonb_typeof(machine_flags) = 'object'),
 examination_status text not null default 'machine_receipt_only_needs_independent_review'
   check (examination_status = 'machine_receipt_only_needs_independent_review'),
 first_seen_at timestamptz not null default now(),
 last_observed_at timestamptz not null default now()
);
alter table public.flock_private_mn_flock_audit_pdf_receipts enable row level security;
revoke all on public.flock_private_mn_flock_audit_pdf_receipts from public,anon,authenticated,service_role;
grant select,insert,update on public.flock_private_mn_flock_audit_pdf_receipts to service_role;
comment on table public.flock_private_mn_flock_audit_pdf_receipts is
'PRIVATE machine-source SHA-256 and page-count receipts for official Minnesota registry Flock-named PDFs. A machine receipt is NOT human PDF content review, not an executed contract, and not evidence of current manufacturer or camera activity.';
create index if not exists mn_flock_receipts_updated on
 public.flock_private_mn_flock_audit_pdf_receipts(last_observed_at desc);
