-- 127: original-publisher source rechecks never silently revoke old dated evidence.
create table if not exists public.flock_original_sharing_rechecks(
 source_key text not null references public.flock_original_sharing_sources(source_key) on delete restrict,
 checked_at timestamptz not null default now(),
 check_result text not null check(check_result in
 ('all_previously_published_names_still_present','publisher_list_changed_or_incomplete',
  'source_section_unavailable','source_fetch_unavailable')),
 expected_names integer not null check(expected_names>=0),
 matched_names integer not null check(matched_names>=0 and matched_names<=expected_names),
 source_http_status integer check(source_http_status between 100 and 599),
 page_sha256 text check(page_sha256 is null or page_sha256 ~ '^[a-f0-9]{64}$'),
 primary key(source_key,checked_at)
);
create index if not exists flock_original_sharing_rechecks_latest_idx
 on public.flock_original_sharing_rechecks(source_key,checked_at desc);
alter table public.flock_original_sharing_rechecks enable row level security;
revoke all on public.flock_original_sharing_rechecks from public,anon,authenticated;
grant select on public.flock_original_sharing_rechecks to anon,authenticated;
grant all on public.flock_original_sharing_rechecks to service_role;
create policy flock_original_recheck_read on public.flock_original_sharing_rechecks
 for select to anon,authenticated using (true);
create or replace view public.flock_public_original_sharing_source_health
 with (security_invoker=true) as
select s.source_key,s.source_agency_id,s.source_url,s.source_kind,
 s.first_observed_on,s.last_successfully_rechecked_at,
 r.checked_at as last_attempted_at,r.check_result,r.expected_names,r.matched_names,
 r.source_http_status
from public.flock_original_sharing_sources s
left join lateral (
 select checked_at,check_result,expected_names,matched_names,source_http_status
 from public.flock_original_sharing_rechecks r
 where r.source_key=s.source_key order by checked_at desc limit 1
) r on true;
revoke all on public.flock_public_original_sharing_source_health from public,anon,authenticated;
grant select on public.flock_public_original_sharing_source_health to anon,authenticated,service_role;
comment on view public.flock_public_original_sharing_source_health is
'Original source fetch/recheck status; only a complete fetched list supports last successfully rechecked. Fetch errors never imply source deletion, sharing revocation or current permission.';
