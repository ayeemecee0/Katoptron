-- 121: dated SECONDARY retention observations from licensed EyesOnFlock.
-- Data is a vendor portal aggregator reading, not independently re-read
-- first-party vendor content. Never overwrite the original first-party
-- flock_vendor_portal_snapshots table with this data.
create table if not exists public.flock_secondary_portal_retention_history(
 source_agency_id text not null references public.flock_secondary_portal_agencies(source_agency_id),
 observed_on date not null,
 retention_days integer check(retention_days between 0 and 3650),
 portal_slug text not null check(length(portal_slug) between 2 and 160),
 source_url text not null check(source_url like 'https://eyesonflock.com/portal/%'),
 evidence_tier text not null default 'secondary_aggregated_portal_snapshot'
  check(evidence_tier='secondary_aggregated_portal_snapshot'),
 first_recorded_at timestamptz not null default now(),
 primary key(source_agency_id,observed_on)
);
create index if not exists flock_secondary_retention_source_idx on
 public.flock_secondary_portal_retention_history(source_agency_id,observed_on desc);
alter table public.flock_secondary_portal_retention_history enable row level security;
revoke all on public.flock_secondary_portal_retention_history from public,anon,authenticated;
grant select on public.flock_secondary_portal_retention_history to anon,authenticated;
grant all on public.flock_secondary_portal_retention_history to service_role;
create policy flock_secondary_retention_read on public.flock_secondary_portal_retention_history
 for select to anon,authenticated using(true);
comment on table public.flock_secondary_portal_retention_history is
'Append-only source-dated EyesOnFlock aggregator snapshots. Retention change needs two nonnull readings. No assertion of current Flock policy or direct firsthand vendor verification.';
