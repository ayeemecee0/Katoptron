begin;
do $v$
begin
 if not (select relrowsecurity from pg_class
  where oid='public.flock_provider_health_checks'::regclass) then
  raise exception 'Provider check table needs RLS';
 end if;
 if not exists(select 1 from pg_class
  where oid='public.flock_public_latest_provider_health'::regclass
   and reloptions @> array['security_invoker=true']::text[]) then
  raise exception 'Provider report view must be security invoker';
 end if;
 if has_table_privilege('anon','public.flock_provider_health_checks','INSERT')
  or has_table_privilege('anon','public.flock_provider_health_checks','UPDATE')
  or has_table_privilege('service_role','public.flock_provider_health_checks','UPDATE')
  or has_column_privilege('service_role','public.flock_provider_health_checks','fixture_type','INSERT')
 then raise exception 'Synthetic provider probe append privileges unsafe';
 end if;
end $v$;
insert into public.flock_provider_health_checks
(checked_at,result_code,routing_http_status,geocoding_http_status,browser_test_passed)
values('2026-10-24T00:00:00Z','passed',200,200,true);
set local role anon;
do $v$
declare r record;
begin
 select * into r from public.flock_public_latest_provider_health;
 if r.result_code<>'passed' or r.provider<>'geoapify'
 or not r.browser_test_passed or r.fixture_type<>'public_fixed_route'
 then raise exception 'Public status does not reflect fixed hosted-origin sample';
 end if;
end $v$;
reset role;
rollback;
