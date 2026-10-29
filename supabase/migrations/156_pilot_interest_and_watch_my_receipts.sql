-- User-owned product discovery only. No payments, subscriptions or charging.
create table if not exists public.research_pilot_interest(
 user_id uuid primary key references auth.users(id) on delete cascade,
 professional_role text not null check(professional_role in ('journalist','nonprofit','legal_researcher','academic','other')),
 seats_band text not null check(seats_band in ('1','2-5','6-20','21+')),
 willingness_band text not null check(willingness_band in ('not_sure','free_only','under_50','50_to_149','150_plus')),
 top_priority text not null check(top_priority in ('alerts','contract_diffs','collaboration','bulk_exports','records_requests')),
 organization_note text not null default '' check(char_length(organization_note)<=180),
 opted_in_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
alter table public.research_pilot_interest enable row level security;
revoke all on public.research_pilot_interest from public,anon,authenticated;
grant select,insert,update,delete on public.research_pilot_interest to authenticated;
create policy pilot_interest_own_read on public.research_pilot_interest for select to authenticated using(user_id=(select auth.uid()));
create policy pilot_interest_own_insert on public.research_pilot_interest for insert to authenticated with check(user_id=(select auth.uid()));
create policy pilot_interest_own_update on public.research_pilot_interest for update to authenticated
 using(user_id=(select auth.uid())) with check(user_id=(select auth.uid()));
create policy pilot_interest_own_delete on public.research_pilot_interest for delete to authenticated using(user_id=(select auth.uid()));
-- Allow each user to read their own SMTP submission states only. Service-role
-- remains the sole writer. These receipts DO NOT prove final inbox delivery.
grant select on public.flock_watch_send_claims,public.flock_watch_deliveries to authenticated;
create policy watch_claims_own_read on public.flock_watch_send_claims for select to authenticated using(user_id=(select auth.uid()));
create policy watch_receipts_own_read on public.flock_watch_deliveries for select to authenticated using(user_id=(select auth.uid()));
