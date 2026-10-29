-- Voluntary, user-owned pilot task metrics. No case notes, source URLs, routes, plate data, email addresses, or automatic tracking.
create table if not exists public.research_pilot_task_measurements (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 task_kind text not null check (task_kind in ('source_check','contract_review','policy_comparison','records_request','other')),
 manual_estimate_minutes integer not null check (manual_estimate_minutes between 1 and 1440),
 software_minutes integer not null check (software_minutes between 1 and 1440),
 task_completed boolean not null,
 recorded_at timestamptz not null default now()
);
create index if not exists research_pilot_task_measurements_owner_date
 on public.research_pilot_task_measurements(user_id,recorded_at desc);
alter table public.research_pilot_task_measurements enable row level security;
revoke all on public.research_pilot_task_measurements from public,anon,authenticated;
grant select,insert,delete on public.research_pilot_task_measurements to authenticated;
create policy pilot_measurements_select_own on public.research_pilot_task_measurements
 for select to authenticated using ((select auth.uid())=user_id);
create policy pilot_measurements_insert_own on public.research_pilot_task_measurements
 for insert to authenticated with check ((select auth.uid())=user_id);
create policy pilot_measurements_delete_own on public.research_pilot_task_measurements
 for delete to authenticated using ((select auth.uid())=user_id);
comment on table public.research_pilot_task_measurements is
 'Explicitly opted-in, owner-deletable self-reported research task durations; no browsing telemetry or personally identifiable research materials. No administrator reads from public client.';
