-- M5 privacy and pruning live/ephemeral acceptance, entirely rolled back.
do $security$
begin
 if has_function_privilege('anon',
   'public.prune_expired_community_submission_rate_events()','EXECUTE')
 or has_function_privilege('authenticated',
   'public.prune_expired_community_submission_rate_events()','EXECUTE')
 or not has_function_privilege('service_role',
   'public.prune_expired_community_submission_rate_events()','EXECUTE')
 then raise exception 'Community anti-abuse ledger prune RPC permissions incorrect';end if;
end $security$;
begin;
select set_config('katoptron.m5_prune_user',gen_random_uuid()::text,true);
insert into auth.users(id) values(current_setting('katoptron.m5_prune_user')::uuid);
insert into public.flock_private_submission_rate_events(user_id,submitted_at)
values(current_setting('katoptron.m5_prune_user')::uuid,now()-interval '26 hours'),
      (current_setting('katoptron.m5_prune_user')::uuid,now()-interval '2 hours');
set local role service_role;
select public.prune_expired_community_submission_rate_events();
reset role;
do $verify$
begin
 if (select count(*) from public.flock_private_submission_rate_events
   where user_id=current_setting('katoptron.m5_prune_user')::uuid)<>1
 then raise exception 'Expired private events were retained or active events erased';end if;
end $verify$;
rollback;
