-- 118: genuine opt-in subscription records, no travel-history data.
create table if not exists public.flock_watch_subscriptions (
 user_id uuid not null references auth.users(id) on delete cascade,
 locality_key text not null check(locality_key ~ '^[a-z0-9 ]+\|[A-Z]{2}$' and length(locality_key)<=130),
 email_enabled boolean not null default false,
 watch_government boolean not null default true,
 watch_vendor boolean not null default true,
 watch_sharing boolean not null default true,
 watch_renewals boolean not null default true,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 primary key (user_id,locality_key)
);
create index if not exists flock_watch_subscriptions_locality_idx
 on public.flock_watch_subscriptions(locality_key) where email_enabled;
alter table public.flock_watch_subscriptions enable row level security;
revoke all on public.flock_watch_subscriptions from public,anon,authenticated;
grant select,insert,update,delete on public.flock_watch_subscriptions to authenticated;
grant all on public.flock_watch_subscriptions to service_role;
create policy flock_watch_self_select on public.flock_watch_subscriptions for select
 to authenticated using ((select auth.uid())=user_id);
create policy flock_watch_self_insert on public.flock_watch_subscriptions for insert
 to authenticated with check ((select auth.uid())=user_id);
create policy flock_watch_self_update on public.flock_watch_subscriptions for update
 to authenticated using ((select auth.uid())=user_id)
 with check ((select auth.uid())=user_id);
create policy flock_watch_self_delete on public.flock_watch_subscriptions for delete
 to authenticated using ((select auth.uid())=user_id);
comment on table public.flock_watch_subscriptions is
'Explicit owner-authenticated public government-evidence watch subscriptions. Email opt-in is false by default; physical journeys, addresses, plates and private routes are never collected.';

-- Agency-specific first-party and secondary reported structural changes.
-- Publishing old or missing information must never become allegations of
-- surveillance misconduct, detected plate reads or exact map cameras.
create table if not exists public.flock_agency_watch_events(
 event_key text primary key check(length(event_key) between 20 and 128),
 locality_key text check(locality_key is null or length(locality_key)<=130),
 source_agency_id text,
 kind text not null check(kind in
 ('government_decision','contract_document','contract_renewal','vendor_portal_snapshot',
  'sharing_list_changed','retention_changed','vendor_count_changed')),
 title text not null check(length(title) between 4 and 280),
 summary text not null check(length(summary) between 10 and 800),
 source_url text not null check(source_url like 'https://%'),
 source_date date,
 evidence_tier text not null check(evidence_tier in
 ('original_government','vendor_first_party','secondary_aggregated_portal_snapshot')),
 observed_at timestamptz not null default now()
);
create index if not exists flock_agency_watch_events_locality_idx on
 public.flock_agency_watch_events(locality_key,observed_at desc);
create index if not exists flock_agency_watch_events_source_idx on
 public.flock_agency_watch_events(source_agency_id,observed_at desc);
alter table public.flock_agency_watch_events enable row level security;
revoke all on public.flock_agency_watch_events from public,anon,authenticated;
grant select on public.flock_agency_watch_events to anon,authenticated;
grant all on public.flock_agency_watch_events to service_role;
create policy flock_watch_events_public on public.flock_agency_watch_events for select
 to anon,authenticated using (true);

-- Only the automated sender can mark an event sent. Anonymous and regular
-- authenticated users cannot observe delivery metadata for others.
create table if not exists public.flock_watch_deliveries(
 user_id uuid not null references auth.users(id) on delete cascade,
 locality_key text not null,
 event_key text not null references public.flock_agency_watch_events(event_key) on delete cascade,
 delivered_at timestamptz not null default now(),
 primary key(user_id,locality_key,event_key)
);
alter table public.flock_watch_deliveries enable row level security;
revoke all on public.flock_watch_deliveries from public,anon,authenticated;
grant select,insert on public.flock_watch_deliveries to service_role;

-- Sender-specific RPC: yields ONLY opted-in subscriptions backed by a verified
-- Auth mailbox. This function must not be executable by public readers.
create or replace function public.flock_watch_delivery_candidates()
returns table (user_id uuid,email text,locality_key text,
 watch_government boolean,watch_vendor boolean,
 watch_sharing boolean,watch_renewals boolean)
language sql stable security definer set search_path=public,pg_temp
as $$
 select s.user_id,u.email,s.locality_key,s.watch_government,s.watch_vendor,
        s.watch_sharing,s.watch_renewals
 from public.flock_watch_subscriptions s
 join auth.users u on u.id=s.user_id
 where s.email_enabled and u.email_confirmed_at is not null
   and u.email is not null and u.deleted_at is null;
$$;
revoke all on function public.flock_watch_delivery_candidates()
 from public,anon,authenticated;
grant execute on function public.flock_watch_delivery_candidates() to service_role;
comment on function public.flock_watch_delivery_candidates() is
'Owner-managed automation only. Enumerates users with explicitly enabled email watches AND confirmed Auth email; no anonymous access.';
