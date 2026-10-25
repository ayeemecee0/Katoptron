-- 098: Public aggregate health reports from hosted-origin synthetic Geoapify
-- acceptance checks. No provider keys, URLs, submitted addresses or user routes.
create table if not exists public.flock_provider_health_checks (
 checked_at timestamptz primary key default now(),
 provider text not null default 'geoapify' check(provider='geoapify'),
 result_code text not null
   check(result_code in ('passed','provider_error','inconclusive')),
 routing_http_status smallint check(routing_http_status between 100 and 599),
 geocoding_http_status smallint check(geocoding_http_status between 100 and 599),
 browser_test_passed boolean not null,
 fixture_type text not null default 'public_fixed_route'
   check(fixture_type='public_fixed_route'),
 check_origin text not null default 'official_github_pages'
   check(check_origin='official_github_pages'),
 constraint health_report_consistency check (
   (result_code='passed' and browser_test_passed
    and routing_http_status=200 and geocoding_http_status=200)
    or result_code<>'passed')
);
alter table public.flock_provider_health_checks enable row level security;
revoke all on public.flock_provider_health_checks from public,anon,authenticated,service_role;
grant select on public.flock_provider_health_checks to anon,authenticated,service_role;
grant insert(result_code,routing_http_status,geocoding_http_status,browser_test_passed)
 on public.flock_provider_health_checks to service_role;
create policy public_fixed_provider_health
 on public.flock_provider_health_checks for select to anon,authenticated
 using (provider='geoapify' and fixture_type='public_fixed_route'
    and check_origin='official_github_pages');

create or replace view public.flock_public_latest_provider_health
 with (security_invoker=true) as
select checked_at,provider,result_code,
 routing_http_status,geocoding_http_status,browser_test_passed,
 fixture_type,check_origin
from public.flock_provider_health_checks
order by checked_at desc limit 1;
revoke all on public.flock_public_latest_provider_health from public,anon,authenticated,service_role;
grant select on public.flock_public_latest_provider_health to anon,authenticated,service_role;
comment on table public.flock_provider_health_checks is
'One synthetic fixed public routing+geocoding hosted-origin browser acceptance result per check. Not Geoapify account-wide remaining credits, uptime SLA, or assurance that visitor routes will succeed. No real user route or location stored.';
