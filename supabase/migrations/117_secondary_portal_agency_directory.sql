-- 117: Licensed secondary agency directory, no surveillance camera coordinates.
-- Source: EyesOnFlock via deflock-data CC BY-SA 4.0, snapshot timestamps.
create table if not exists public.flock_secondary_portal_agencies(
 source_agency_id text primary key check(length(source_agency_id) between 2 and 160),
 agency_name text not null check(length(agency_name) between 2 and 300),
 state_code text,
 agency_type text not null default 'other',
 is_reporting_portal boolean not null,
 portal_slug text,
 source_reported_mixed_cameras integer,
 source_reported_searches integer,
 source_reported_hotlist_hits integer,
 source_reported_network_links integer,
 source_snapshot_at timestamptz not null,
 source_url text not null default 'https://eyesonflock.com',
 source_tier text not null default 'secondary_aggregated_portal_snapshot'
   check(source_tier='secondary_aggregated_portal_snapshot'),
 source_license text not null default 'CC BY-SA 4.0',
 reconciled_at timestamptz not null default now(),
 check(state_code is null or state_code ~ '^[A-Z]{2}$'),
 check(portal_slug is null or length(portal_slug)<=160),
 check(source_reported_mixed_cameras is null or source_reported_mixed_cameras>=0),
 check(source_reported_searches is null or source_reported_searches>=0),
 check(source_reported_hotlist_hits is null or source_reported_hotlist_hits>=0),
 check(source_reported_network_links is null or source_reported_network_links>=0)
);
create index if not exists flock_secondary_portal_agency_state_idx
 on public.flock_secondary_portal_agencies(state_code,agency_name);
create index if not exists flock_secondary_portal_source_idx
 on public.flock_secondary_portal_agencies(source_snapshot_at desc);
alter table public.flock_secondary_portal_agencies enable row level security;
revoke all on public.flock_secondary_portal_agencies from public,anon,authenticated;
grant select on public.flock_secondary_portal_agencies to anon,authenticated;
grant select,insert,update,delete on public.flock_secondary_portal_agencies to service_role;
drop policy if exists flock_secondary_portal_read on public.flock_secondary_portal_agencies;
create policy flock_secondary_portal_read on public.flock_secondary_portal_agencies
 for select to anon,authenticated using (true);
comment on table public.flock_secondary_portal_agencies is
'Original-source-derived CC BY-SA source-dated SECONDARY agency metadata, not source-verified Flock camera hardware or geographic pins. Never combine counters with official GIS map.';

-- Evidence gaps are derived by application from current public records; do not
-- create or infer a camera location from any agency index or portal metric.
