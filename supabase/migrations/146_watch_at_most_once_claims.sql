-- 146: at-most-once source Watch SMTP attempt claim, distinct from delivery receipts.
-- Claim must be inserted BEFORE SMTP. A missing receipt after a claim is an
-- uncertain send requiring operator review, never automatic retransmission.
-- It does NOT assert successful inbox delivery or a published source change.
create table if not exists public.flock_watch_send_claims (
 user_id uuid not null references auth.users(id) on delete cascade,
 locality_key text not null,
 event_key text not null references public.flock_agency_watch_events(event_key) on delete cascade,
 claimed_at timestamptz not null default now(),
 primary key (user_id, locality_key, event_key)
);
create index if not exists flock_watch_send_claims_claimed_at_idx
 on public.flock_watch_send_claims(claimed_at);
alter table public.flock_watch_send_claims enable row level security;
revoke all on public.flock_watch_send_claims from public,anon,authenticated;
grant select,insert on public.flock_watch_send_claims to service_role;
comment on table public.flock_watch_send_claims is
 'Private at-most-once SMTP attempt reservations. Presence without a corresponding flock_watch_deliveries row is uncertain outcome requiring manual review; no resend.';
