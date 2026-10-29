-- 148: stateful, private, crash-reconcilable at-most-once Watch outbox.
-- Previously claimed rows default to 'claimed' so an upgrade can NEVER resend them.
alter table public.flock_watch_send_claims
 add column if not exists status text not null default 'claimed'
   check (status in ('queued','claimed','smtp_submitted','uncertain','failed','canceled')),
 add column if not exists status_changed_at timestamptz not null default now(),
 add column if not exists smtp_accepted_at timestamptz,
 add column if not exists failure_code text;
create index if not exists flock_watch_send_claims_status_idx
 on public.flock_watch_send_claims(status,status_changed_at);
alter table public.flock_watch_send_claims enable row level security;
revoke all on public.flock_watch_send_claims from public,anon,authenticated;
grant select,insert,update on public.flock_watch_send_claims to service_role;
comment on column public.flock_watch_send_claims.status is
 'queued = safe before SMTP; claimed = may have attempted SMTP; smtp_submitted = SMTP accepted; uncertain = no resend; failed/canceled = terminal. Receipt records SMTP handoff, not final inbox acceptance.';
