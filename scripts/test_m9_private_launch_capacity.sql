-- M9 SQL release invariant: capacity API is ONLY service-role callable.
do $m9$
declare snapshot jsonb;
begin
 if has_function_privilege('anon',
    'public.katoptron_private_launch_capacity()','EXECUTE')
 or has_function_privilege('authenticated',
    'public.katoptron_private_launch_capacity()','EXECUTE')
 or not has_function_privilege('service_role',
    'public.katoptron_private_launch_capacity()','EXECUTE')
 then raise exception 'Private operational metrics exposed to public identities';end if;
 if not exists (select 1 from pg_proc where
  oid='public.katoptron_private_launch_capacity()'::regprocedure
  and prosecdef and provolatile='s'
  and proconfig @> array['search_path=""']::text[])
 then raise exception 'Operational capacity RPC definition changed unexpectedly';end if;
 snapshot:=public.katoptron_private_launch_capacity();
 if snapshot ?| array['email','user_id','latitude','longitude','storage_name',
                       'photo_url','description','camera_coordinates','token']
 then raise exception 'Capacity snapshot contains prohibited private details';end if;
 if (select count(*) from jsonb_object_keys(snapshot))<>9 or
    (snapshot->>'database_bytes')::bigint<=0 or
    (snapshot->>'registered_private_bucket_count')::integer<>1
 then raise exception 'Private capacity snapshot malformed or private bucket missing';end if;
 if (snapshot->>'private_community_report_count')::bigint<>(
     select count(*) from public.flock_community_submissions)
 then raise exception 'Private report count no longer reconciles';end if;
end $m9$;
begin;
set local role anon;
do $denied$
begin
 if has_function_privilege('public.katoptron_private_launch_capacity()','EXECUTE')
 then raise exception 'Anon can execute private capacity RPC';end if;
end $denied$;
reset role;
set local role authenticated;
do $denied$
begin
 if has_function_privilege('public.katoptron_private_launch_capacity()','EXECUTE')
 then raise exception 'Logged-in non-reviewers can execute private capacity RPC';end if;
end $denied$;
rollback;
