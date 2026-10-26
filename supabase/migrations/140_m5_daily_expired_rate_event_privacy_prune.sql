-- 140: M5 daily deletion of expired privacy-minimized rate events.
-- A report's coordinates, description, and URL are already erased by M5/139.
-- Retain only account ID and creation time until the 24h rate window expires;
-- a scheduled service-only worker now removes stale event rows, even if the
-- contributor never submits another report.
create or replace function public.prune_expired_community_submission_rate_events()
returns integer
language plpgsql security definer set search_path='' as $body$
declare removed integer;
begin
 delete from public.flock_private_submission_rate_events
  where submitted_at < now()-interval '24 hours';
 get diagnostics removed = row_count;
 return removed;
end $body$;
revoke all on function public.prune_expired_community_submission_rate_events()
 from public,anon,authenticated,service_role;
grant execute on function public.prune_expired_community_submission_rate_events()
 to service_role;
comment on function public.prune_expired_community_submission_rate_events() is
 'Service-role-only scheduled deletion of all private rate-event data outside the rolling 24-hour enforcement period. Does not touch reports, photos, camera evidence or user accounts.';
