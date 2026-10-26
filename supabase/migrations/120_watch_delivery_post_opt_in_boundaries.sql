-- 120: sender-specific confirmed-email subscription enumeration with start-date.
-- Do not replay existing historical source records to new subscribers.
drop function if exists public.flock_watch_delivery_candidates();
create function public.flock_watch_delivery_candidates()
returns table (user_id uuid,email text,locality_key text,
 watch_government boolean,watch_vendor boolean,
 watch_sharing boolean,watch_renewals boolean, subscribed_at timestamptz)
language sql stable security definer set search_path=public,pg_temp
as $$
 select s.user_id,u.email,s.locality_key,s.watch_government,s.watch_vendor,
        s.watch_sharing,s.watch_renewals,s.created_at
 from public.flock_watch_subscriptions s
 join auth.users u on u.id=s.user_id
 where s.email_enabled and u.email_confirmed_at is not null
   and u.email is not null and u.deleted_at is null
   and (u.is_anonymous is not true);
$$;
revoke all on function public.flock_watch_delivery_candidates()
 from public,anon,authenticated;
grant execute on function public.flock_watch_delivery_candidates() to service_role;
