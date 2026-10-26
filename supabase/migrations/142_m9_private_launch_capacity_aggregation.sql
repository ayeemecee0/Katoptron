-- 142: Service-only production-capacity snapshot for free-tier early warning.
-- Returns aggregate counts and byte totals, NEVER a contributor identity,
-- coordinate, license plate, storage object key, review note, or report body.
-- Deliberately does not grant anonymous/authenticated RPC invocation.
create or replace function public.katoptron_private_launch_capacity()
returns jsonb
language sql stable security definer set search_path = ''
as $function$
 select pg_catalog.jsonb_build_object(
   'database_bytes',pg_catalog.pg_database_size(pg_catalog.current_database()),
   'private_community_report_count',
       (select count(*) from public.flock_community_submissions),
   'private_community_photo_count',
       (select count(*) from storage.objects
        where bucket_id='katoptron-community-evidence'),
   'private_community_photo_metadata_bytes',
       (select coalesce(sum(
          case when (metadata->>'size') ~ '^[0-9]{1,15}$'
               then (metadata->>'size')::bigint
               else 0::bigint end),0)::bigint
        from storage.objects where bucket_id='katoptron-community-evidence'),
   'private_photo_size_metadata_missing',
       (select count(*) from storage.objects where bucket_id='katoptron-community-evidence'
          and coalesce((metadata->>'size') ~ '^[0-9]{1,15}$',false)=false),
   'retained_one_day_rate_events',
       (select count(*) from public.flock_private_submission_rate_events),
   'expired_one_day_rate_events',
       (select count(*) from public.flock_private_submission_rate_events
          where submitted_at<pg_catalog.now()-interval '26 hours'),
   'active_auth_accounts',
       (select count(*) from auth.users),
   'registered_private_bucket_count',
       (select count(*) from storage.buckets
          where id='katoptron-community-evidence' and public=false)
 );
$function$;
revoke all on function public.katoptron_private_launch_capacity()
 from public,anon,authenticated,service_role;
grant execute on function public.katoptron_private_launch_capacity()
 to service_role;
comment on function public.katoptron_private_launch_capacity() is
 'Private service-role-only aggregate production capacity snapshot. No object names, coordinates, private identities, or raw reports. Report/photo totals are operational aggregates, not published source evidence or a Storage org-wide bill.';
