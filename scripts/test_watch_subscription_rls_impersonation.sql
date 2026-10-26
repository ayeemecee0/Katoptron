-- Disposable CI-only RLS penetration checks; two Auth fixtures from validate.yml.
-- Run after creating all watch migrations, never against real user records.
begin;
insert into public.flock_watch_subscriptions(user_id,locality_key,email_enabled)
values ('22222222-2222-4222-8222-222222222222','private city|CA',true);

set local role authenticated;
select set_config('request.jwt.claim.sub',
 '11111111-1111-4111-8111-111111111111',true);

do $watch_owner_test$
declare n integer; blocked boolean:=false;
begin
 select count(*) into n from public.flock_watch_subscriptions;
 if n<>0 then raise exception 'BOLA: account A can view account B Watch subscriptions';end if;
 select count(*) into n from public.flock_watch_deliveries;
 if n<>0 then raise exception 'Subscriber can inspect private mail delivery receipts';end if;
 insert into public.flock_watch_subscriptions(user_id,locality_key,email_enabled)
 values ('11111111-1111-4111-8111-111111111111','own city|CA',false);
 select count(*) into n from public.flock_watch_subscriptions;
 if n<>1 then raise exception 'Owner cannot read own private Watch preference';end if;
 update public.flock_watch_subscriptions
 set email_enabled=true
 where user_id='11111111-1111-4111-8111-111111111111';
 if not found then raise exception 'Owner cannot update own opted-in preference';end if;
 update public.flock_watch_subscriptions
 set email_enabled=false
 where user_id='22222222-2222-4222-8222-222222222222';
 if found then raise exception 'BOLA: account A updated account B Watch preference';end if;
 delete from public.flock_watch_subscriptions
 where user_id='22222222-2222-4222-8222-222222222222';
 if found then raise exception 'BOLA: account A deleted account B Watch preference';end if;
 begin
  insert into public.flock_watch_subscriptions(user_id,locality_key)
  values ('22222222-2222-4222-8222-222222222222','forged city|CA');
 exception when insufficient_privilege or check_violation then blocked=true;
 end;
 if not blocked then raise exception 'BOLA: user A inserted subscription in user B identity';end if;
 if has_function_privilege('authenticated','public.flock_watch_delivery_candidates()','EXECUTE')
 then raise exception 'Public client can enumerate other users confirmed email addresses';end if;
end $watch_owner_test$;

reset role;
rollback;
