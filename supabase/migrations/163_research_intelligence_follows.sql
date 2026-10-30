-- 163: opt-in, private researcher-interest feed. Never sends email and never
-- replays historical events as if newly discovered. Initial follow time is DB-owned.
create table if not exists public.research_intelligence_follows(
 user_id uuid not null references auth.users(id) on delete cascade,
 locality_key text not null check(locality_key ~ '^[a-z0-9][a-z0-9 -]{1,120}\|[A-Z]{2}$'),
 topics text[] not null default array['contract','policy','oversight','sharing','procurement']::text[]
   check (cardinality(topics) between 1 and 5 and topics <@ array['contract','policy','oversight','sharing','procurement']::text[]),
 research_question text not null default '' check(length(research_question)<=160),
 opted_in_at timestamptz not null default now(),
 primary key(user_id,locality_key)
);
create index if not exists research_intelligence_follows_owner_time on public.research_intelligence_follows(user_id,opted_in_at desc);
alter table public.research_intelligence_follows enable row level security;
revoke all on table public.research_intelligence_follows from public,anon,authenticated;
grant select,delete on table public.research_intelligence_follows to authenticated;
grant insert(user_id,locality_key,topics,research_question) on table public.research_intelligence_follows to authenticated;
grant update(topics,research_question) on table public.research_intelligence_follows to authenticated;
create policy intelligence_follows_read_own on public.research_intelligence_follows
 for select to authenticated using ((select auth.uid())=user_id);
create policy intelligence_follows_insert_own on public.research_intelligence_follows
 for insert to authenticated with check ((select auth.uid())=user_id);
create policy intelligence_follows_update_own on public.research_intelligence_follows
 for update to authenticated using ((select auth.uid())=user_id)
 with check ((select auth.uid())=user_id);
create policy intelligence_follows_delete_own on public.research_intelligence_follows
 for delete to authenticated using ((select auth.uid())=user_id);
comment on table public.research_intelligence_follows is 'Explicit, user-owned in-app research feed preferences; no email sends, no retroactive new-event claims, no stored private documents. Baseline timestamp immutable for authenticated users.';
