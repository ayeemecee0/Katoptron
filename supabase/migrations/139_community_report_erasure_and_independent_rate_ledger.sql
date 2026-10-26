-- 139: M5 contributor-controlled erasure, immutable rolling-window abuse cap,
-- and removal of obsolete unaudited two-argument reviewer outcome RPC.
-- A report must be withdrawn and all associated private Storage objects
-- actually deleted through the Storage API before source-derived private
-- evidence and reporter content can be permanently erased.

create table if not exists public.flock_private_submission_rate_events (
 event_id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 submitted_at timestamptz not null default now()
);
create index if not exists flock_private_submission_rate_events_user_time
 on public.flock_private_submission_rate_events(user_id,submitted_at desc);
alter table public.flock_private_submission_rate_events enable row level security;
revoke all on public.flock_private_submission_rate_events from public,anon,authenticated,service_role;
comment on table public.flock_private_submission_rate_events is
 'Private minimally scoped one-day abuse ledger: user and submission time only; NO coordinates, description, source URL, photos, report ID or public access. Old entries for a user are pruned during the next attempted submission. Account deletion cascades.';

-- Preserve historical last-24-hour counts across this schema change.
insert into public.flock_private_submission_rate_events(user_id,submitted_at)
select submitter_id,created_at from public.flock_community_submissions
where created_at >= now()-interval '24 hours';

create or replace function katoptron_internal.throttle_community_report()
returns trigger language plpgsql security definer set search_path='' as $body$
declare recent_reports integer;
begin
 if (select auth.uid()) is null or new.submitter_id is distinct from (select auth.uid()) then
   raise exception 'Authenticated report owner required' using errcode='42501';
 end if;
 perform pg_catalog.pg_advisory_xact_lock(
   pg_catalog.hashtextextended(new.submitter_id::text,0));
 delete from public.flock_private_submission_rate_events
   where user_id=new.submitter_id and submitted_at<now()-interval '24 hours';
 select count(*) into recent_reports from public.flock_private_submission_rate_events r
 where r.user_id=new.submitter_id and r.submitted_at>=now()-interval '24 hours';
 if recent_reports>=3 then
   raise exception 'Maximum 3 reports per rolling 24 hours'
      using errcode='P0001';
 end if;
 insert into public.flock_private_submission_rate_events(user_id) values(new.submitter_id);
 return new;
end
$body$;
revoke all on function katoptron_internal.throttle_community_report()
 from public,anon,authenticated,service_role;

create or replace function public.delete_withdrawn_community_report(p_id uuid)
returns boolean
language plpgsql security definer set search_path='' as $body$
declare
 own_report public.flock_community_submissions%rowtype;
 ckey text;
begin
 if (select auth.uid()) is null then
   raise exception 'Authentication required' using errcode='42501';
 end if;
 select * into own_report from public.flock_community_submissions
 where submission_id=p_id and submitter_id=(select auth.uid())
 for update;
 if not found then return false;end if;
 if own_report.report_status<>'withdrawn' then
   raise exception 'Withdraw report before permanent deletion'
     using errcode='P0001';
 end if;
 -- Supabase does NOT permit blob deletion by SQL. Require proof that the
 -- exact report's Storage prefix is empty after contributor-driven
 -- Storage API removal, to avoid orphaned photo bytes and reviewer URLs.
 if exists(
   select 1 from storage.objects o
   where o.bucket_id='katoptron-community-evidence'
     and o.name like own_report.submitter_id::text||'/'||p_id::text||'/%'
 ) then
   raise exception 'Delete private report photos with Storage API before erasing report'
     using errcode='P0001';
 end if;
 ckey:='tier_'||md5(p_id::text);
 -- Only the deterministic derived candidate for THIS private report.
 -- Delete dependent research records first. If an independent source
 -- links to it unexpectedly, the FK blocks erasure rather than secretly
 -- deleting independently sourced evidence.
 delete from public.flock_gis_point_case_dispositions where case_key=ckey;
 delete from public.flock_source_attributed_map_points where case_key=ckey;
 delete from public.flock_point_evidence_attestations where case_key=ckey;
 delete from public.flock_point_evidence_cases where case_key=ckey;
 -- Cascades into reviewer history + duplicate-screening metadata.
 delete from public.flock_community_submissions where submission_id=p_id
 and submitter_id=own_report.submitter_id and report_status='withdrawn';
 return true;
end $body$;
revoke all on function public.delete_withdrawn_community_report(uuid)
 from public,anon,authenticated,service_role;
grant execute on function public.delete_withdrawn_community_report(uuid)
 to authenticated;
comment on function public.delete_withdrawn_community_report(uuid) is
 'Contributor-only authenticated permanent erasure after withdrawal and confirmed private Storage object deletion. Deletes one user-owned report, reviewer history, screening and report-derived withdrawn source candidates. Preserves anonymous one-day rate counter to prevent delete/repost spam.';

-- Historical two-argument review RPC allowed the correct reviewer to change
-- outcomes without a required note or auditable history. The supported
-- three-argument function requires nontrivial reviewer explanation.
revoke all on function public.set_community_review_status(uuid,text)
 from public,anon,authenticated,service_role;
drop function if exists public.set_community_review_status(uuid,text);
