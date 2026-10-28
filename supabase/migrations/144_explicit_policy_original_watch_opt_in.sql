-- M10 · Separately consented original-government policy source alerts.
-- No new tables or public privileges: existing owner-only subscriptions and
-- service-owned event queues retain their RLS policies.
alter table public.flock_watch_subscriptions
 add column if not exists watch_policies boolean not null default false;
alter table public.flock_watch_subscriptions
 add column if not exists policy_opted_in_at timestamptz;

-- Database time, not a client-supplied timestamp, controls new-category start.
-- Re-enabling after unsubscribe starts a fresh window; unrelated edits do not
-- silently backdate or advance an existing user's policy opt-in.
create or replace function public.flock_watch_policy_opt_in_stamp()
returns trigger language plpgsql
set search_path = pg_catalog
as $$
begin
 if new.watch_policies is true then
  if tg_op='INSERT' or old.watch_policies is distinct from true then
   new.policy_opted_in_at=transaction_timestamp();
  else
   new.policy_opted_in_at=old.policy_opted_in_at;
  end if;
 else
  new.policy_opted_in_at=null;
 end if;
 return new;
end;
$$;
revoke all on function public.flock_watch_policy_opt_in_stamp()
 from public,anon,authenticated;
drop trigger if exists flock_watch_policy_opt_in_stamp on public.flock_watch_subscriptions;
create trigger flock_watch_policy_opt_in_stamp
 before insert or update on public.flock_watch_subscriptions
 for each row execute function public.flock_watch_policy_opt_in_stamp();

do $$
begin
 if not exists (select 1 from pg_constraint
                where conname='flock_watch_policy_since_consistency'
                  and conrelid='public.flock_watch_subscriptions'::regclass) then
  alter table public.flock_watch_subscriptions
   add constraint flock_watch_policy_since_consistency
   check ((watch_policies is true and policy_opted_in_at is not null)
       or (watch_policies is false and policy_opted_in_at is null));
 end if;
end $$;

-- Distinguish a reviewed policy document and a held, unadopted DRAFT.
-- Neither represents an implemented change or verified current system state.
alter table public.flock_agency_watch_events
 drop constraint if exists flock_agency_watch_events_kind_check;
alter table public.flock_agency_watch_events
 add constraint flock_agency_watch_events_kind_check check (
 kind in ('government_decision','contract_document','contract_renewal',
 'vendor_portal_snapshot','sharing_list_changed','retention_changed',
 'vendor_count_changed','policy_original_reviewed','policy_draft_reviewed')
);

comment on column public.flock_watch_subscriptions.watch_policies is
 'Separate explicit opt-in for new source-page-reviewed ALPR policy documents; default OFF.';
comment on column public.flock_watch_subscriptions.policy_opted_in_at is
 'Server-issued start of current policy alert opt-in. Excludes prior source events.';
comment on function public.flock_watch_policy_opt_in_stamp() is
 'Owner-row trigger stamps new policy consent at database time; blocks backdating.';
