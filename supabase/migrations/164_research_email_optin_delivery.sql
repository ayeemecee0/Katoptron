-- Independent, explicitly opted-in research digest email consent.
-- A research follow NEVER enables email. Historical records never replay on enrollment.
create table if not exists public.research_email_subscriptions (
 user_id uuid not null references auth.users(id) on delete cascade,
 locality_key text not null check(locality_key ~ '^[a-z0-9][a-z0-9 -]{1,120}\\|[A-Z]{2}$'),
 topics text[] not null default array['contract','policy','oversight','sharing','procurement']::text[]
  check(cardinality(topics) between 1 and 5 and topics <@ array['contract','policy','oversight','sharing','procurement']::text[]),
 keyword text not null default '' check(length(keyword)<=160),
 enabled boolean not null default true,
 opted_in_at timestamptz not null default now(),
 changed_at timestamptz not null default now(),
 primary key (user_id,locality_key)
);
create or replace function public.research_email_reset_consent_baseline()
returns trigger language plpgsql set search_path = '' as $$
begin
 new.changed_at := clock_timestamp();
 if (old.enabled is distinct from new.enabled and new.enabled is true)
  or old.topics is distinct from new.topics or old.keyword is distinct from new.keyword then
  new.opted_in_at := clock_timestamp();
 else
  new.opted_in_at := old.opted_in_at;
 end if;
 return new;
end;$$;
revoke all on function public.research_email_reset_consent_baseline() from public,anon,authenticated;
drop trigger if exists research_email_consent_change on public.research_email_subscriptions;
create trigger research_email_consent_change before update on public.research_email_subscriptions
for each row execute function public.research_email_reset_consent_baseline();
alter table public.research_email_subscriptions enable row level security;
revoke all on public.research_email_subscriptions from public,anon,authenticated;
grant select,delete on public.research_email_subscriptions to authenticated;
grant insert(user_id,locality_key,topics,keyword) on public.research_email_subscriptions to authenticated;
grant update(topics,keyword,enabled) on public.research_email_subscriptions to authenticated;
create policy research_email_own_select on public.research_email_subscriptions for select to authenticated
 using ((select auth.uid())=user_id);
create policy research_email_own_insert on public.research_email_subscriptions for insert to authenticated
 with check ((select auth.uid())=user_id);
create policy research_email_own_update on public.research_email_subscriptions for update to authenticated
 using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id);
create policy research_email_own_delete on public.research_email_subscriptions for delete to authenticated
 using ((select auth.uid())=user_id);
create table if not exists public.research_email_send_claims (
 user_id uuid not null references auth.users(id) on delete cascade,
 locality_key text not null,
 event_key text not null references public.flock_agency_watch_events(event_key),
 status text not null default 'queued' check(status in ('queued','claimed','smtp_submitted','uncertain','canceled')),
 claimed_at timestamptz not null default now(),
 status_changed_at timestamptz not null default now(),
 smtp_accepted_at timestamptz,
 failure_code text,
 primary key(user_id,locality_key,event_key)
);
create table if not exists public.research_email_delivery_receipts (
 user_id uuid not null references auth.users(id) on delete cascade,
 locality_key text not null,
 event_key text not null references public.flock_agency_watch_events(event_key),
 smtp_accepted_at timestamptz not null default now(),
 primary key(user_id,locality_key,event_key),
 foreign key(user_id,locality_key,event_key)
  references public.research_email_send_claims(user_id,locality_key,event_key)
);
create index if not exists research_email_claims_user_time on public.research_email_send_claims(user_id,claimed_at desc);
alter table public.research_email_send_claims enable row level security;
alter table public.research_email_delivery_receipts enable row level security;
revoke all on public.research_email_send_claims from public,anon,authenticated;
revoke all on public.research_email_delivery_receipts from public,anon,authenticated;
grant select on public.research_email_send_claims to authenticated;
grant select on public.research_email_delivery_receipts to authenticated;
create policy research_email_claims_owner_read on public.research_email_send_claims for select to authenticated
 using ((select auth.uid())=user_id);
create policy research_email_receipts_owner_read on public.research_email_delivery_receipts for select to authenticated
 using ((select auth.uid())=user_id);
-- A service-only, explicitly permissioned accessor. It excludes unconfirmed accounts.
create or replace function public.research_email_delivery_candidates()
returns table(user_id uuid,locality_key text,email text,topics text[],keyword text,opted_in_at timestamptz)
language sql security definer set search_path = '' stable as $$
 select s.user_id,s.locality_key,u.email,s.topics,s.keyword,s.opted_in_at
 from public.research_email_subscriptions s join auth.users u on u.id=s.user_id
 where s.enabled is true and u.email_confirmed_at is not null and u.email is not null
 and s.opted_in_at <= now()
 order by s.opted_in_at asc
 limit 500
$$;
revoke all on function public.research_email_delivery_candidates() from public,anon,authenticated;
grant execute on function public.research_email_delivery_candidates() to service_role;
comment on table public.research_email_subscriptions is
 'Separate email-specific opt in with immutable server-controlled baseline, not activated by research follows.';
comment on table public.research_email_delivery_receipts is
 'SMTP accepted submission receipt only. Does not confirm mailbox delivery.';
