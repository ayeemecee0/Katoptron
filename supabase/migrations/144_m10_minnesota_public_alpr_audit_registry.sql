-- 144: Minnesota Legislature original ALPR audit registry metadata.
-- Title/index metadata is public. A title that names Flock is NOT
-- independently reviewed PDF content or proof of current ALPR operation.
create table if not exists public.flock_public_mn_alpr_audit_registry (
 source_url text primary key
   check (source_url ~ '^https://www\.lrl\.mn\.gov/docs/20[0-9]{2}/mandated/[0-9]{6}\.pdf$'),
 registry_url text not null default 'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735'
   check (registry_url = 'https://www.lrl.mn.gov/mndocs/mandates_detail?orderid=8735'),
 report_id text not null check (report_id ~ '^[0-9]{2}-[0-9]{4}\.pdf$'),
 report_title text not null check (length(report_title) between 18 and 400),
 listed_publishers text not null default '' check (length(listed_publishers) <= 450),
 publication_date date,
 coverage_period text not null default '' check (length(coverage_period) <= 260),
 received_date date,
 title_scope text not null
   check(title_scope in ('flock_named_in_title','other_vendor_named_in_title',
                       'mixed_or_ambiguous_title','unspecified_alpr_title')),
 evidence_tier text not null default 'state_legislative_registry_index_metadata_only'
   check(evidence_tier = 'state_legislative_registry_index_metadata_only'),
 registry_sha256 text not null check(registry_sha256 ~ '^[0-9a-f]{64}$'),
 first_indexed_at timestamptz not null default now(),
 last_observed_at timestamptz not null default now(),
 constraint mn_audit_report_id_unique unique(report_id)
);
create index if not exists mn_alpr_audit_registry_scope_date
 on public.flock_public_mn_alpr_audit_registry(title_scope, publication_date desc);
alter table public.flock_public_mn_alpr_audit_registry enable row level security;
revoke all on public.flock_public_mn_alpr_audit_registry from public,anon,authenticated;
grant select on public.flock_public_mn_alpr_audit_registry to anon,authenticated;
grant select,insert,update on public.flock_public_mn_alpr_audit_registry to service_role;
create policy mn_alpr_registry_public_metadata_read
 on public.flock_public_mn_alpr_audit_registry for select to anon,authenticated
 using (true);
comment on table public.flock_public_mn_alpr_audit_registry is
 'Original Minnesota state legislature ALPR audit LISTING METADATA, auto-indexed; no PDF text reviewed or current Flock manufacturer/install/compliance conclusion. Index order/date and title may be revised by publisher.';

create table if not exists public.flock_private_mn_alpr_registry_scan_runs (
 scanned_at timestamptz primary key default now(),
 registry_sha256 text not null check(registry_sha256 ~ '^[0-9a-f]{64}$'),
 report_links integer not null check(report_links between 20 and 500),
 flock_titles integer not null check(flock_titles between 0 and 500),
 new_links integer not null check(new_links between 0 and 500),
 index_metadata_only boolean not null default true check(index_metadata_only),
 scan_method text not null default 'state_legislative_mandate_table_html'
  check(scan_method='state_legislative_mandate_table_html')
);
alter table public.flock_private_mn_alpr_registry_scan_runs enable row level security;
revoke all on public.flock_private_mn_alpr_registry_scan_runs from public,anon,authenticated;
grant select,insert on public.flock_private_mn_alpr_registry_scan_runs to service_role;
comment on table public.flock_private_mn_alpr_registry_scan_runs is
 'Private scan diagnostics only, never evidence that an original document content or agency policy was independently verified.';
