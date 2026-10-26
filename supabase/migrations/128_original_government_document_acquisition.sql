-- 128: source-qualified original government document acquisition.
-- A government page linking to a PDF/CSV is NOT proof of its contents,
-- executed contract, permitted recipient, deployment, or current policy.
create table if not exists public.flock_original_document_leads (
 document_url text primary key check(length(document_url) between 15 and 1500 and document_url like 'https://%'),
 government_page_url text not null check(government_page_url like 'https://%'),
 jurisdiction_label text not null check(length(jurisdiction_label) between 5 and 150),
 document_class text not null check(document_class in
 ('contract','policy','sharing_export','audit','meeting_record','general_document')),
 link_label text not null check(length(link_label) between 3 and 400),
 source_page_sha256 text not null check(source_page_sha256 ~ '^[0-9a-f]{64}$'),
 confidence text not null default 'original_government_link_only'
 check(confidence='original_government_link_only'),
 review_status text not null default 'requires_document_review'
 check(review_status in ('requires_document_review','extracted_recipient_candidate',
 'document_content_verified','rejected','source_unavailable')),
 first_seen_at timestamptz not null default now(),
 last_seen_at timestamptz not null default now(),
 checked_at timestamptz,
 last_error text
);
create index if not exists flock_original_document_leads_review_idx on
 public.flock_original_document_leads(review_status,document_class);
alter table public.flock_original_document_leads enable row level security;
revoke all on public.flock_original_document_leads from public,anon,authenticated;
grant all on public.flock_original_document_leads to service_role;
comment on table public.flock_original_document_leads is
'Private source-qualified original GOVERNMENT hyperlink leads only; never verified contract terms, executed spending, policy changes or sharing grants until independently corroborated.';

create table if not exists public.flock_original_sharing_extraction_candidates (
 document_url text not null references public.flock_original_document_leads(document_url) on delete cascade,
 recipient_label text not null check(length(recipient_label) between 3 and 180),
 publisher_agency_id text,
 extraction_basis text not null check(extraction_basis in ('csv_named_recipient_column_unreviewed')),
 review_status text not null default 'review_required'
 check(review_status in ('review_required','independently_verified','rejected')),
 first_seen_at timestamptz not null default now(),
 primary key(document_url,recipient_label)
);
create index if not exists flock_original_sharing_extraction_status_idx on
 public.flock_original_sharing_extraction_candidates(review_status);
alter table public.flock_original_sharing_extraction_candidates enable row level security;
revoke all on public.flock_original_sharing_extraction_candidates from public,anon,authenticated;
grant all on public.flock_original_sharing_extraction_candidates to service_role;
comment on table public.flock_original_sharing_extraction_candidates is
'Raw deterministic named-recipient extraction candidates from original government-linked CSV; direction and identities require verification, never auto-published to the public access graph.';

create table if not exists public.flock_original_document_scan_runs (
 run_id uuid primary key default gen_random_uuid(),
 scanned_at timestamptz not null default now(),
 seeded_pages integer not null check(seeded_pages >= 0),
 successfully_read_pages integer not null check(successfully_read_pages >= 0),
 new_document_links integer not null check(new_document_links >= 0),
 seen_document_links integer not null check(seen_document_links >= 0),
 named_recipient_candidates integer not null check(named_recipient_candidates >= 0),
 source_errors integer not null check(source_errors >= 0),
 summary text not null default ''
);
alter table public.flock_original_document_scan_runs enable row level security;
revoke all on public.flock_original_document_scan_runs from public,anon,authenticated;
grant all on public.flock_original_document_scan_runs to service_role;

-- Aggregate-only public dashboard: cannot expose unreviewed source documents
-- or speculative access relationships. The service publishes each run's
-- counts after a completed bounded scan, separately from the private queue.
create table if not exists public.flock_original_acquisition_public_metrics (
 metric_date date primary key,
 seeded_pages integer not null default 0,
 successfully_read_pages integer not null default 0,
 total_discovered_links integer not null default 0,
 total_reviewed_documents integer not null default 0,
 raw_named_recipient_candidates integer not null default 0,
 verified_original_sharing_edges integer not null default 0,
 verified_original_publishers integer not null default 0,
 source_errors integer not null default 0,
 updated_at timestamptz not null default now(),
 check(seeded_pages>=0 and successfully_read_pages>=0 and total_discovered_links>=0
 and total_reviewed_documents>=0 and raw_named_recipient_candidates>=0
 and verified_original_sharing_edges>=0 and verified_original_publishers>=0
 and source_errors>=0)
);
alter table public.flock_original_acquisition_public_metrics enable row level security;
revoke all on public.flock_original_acquisition_public_metrics from public,anon,authenticated;
grant select on public.flock_original_acquisition_public_metrics to anon,authenticated;
grant all on public.flock_original_acquisition_public_metrics to service_role;
create policy flock_original_acquisition_metrics_read on public.flock_original_acquisition_public_metrics
 for select to anon,authenticated using(true);
comment on table public.flock_original_acquisition_public_metrics is
'Non-identifying aggregate measurement of original gov document acquisition and independently published sharing evidence, NOT 490k verified relationships.';
