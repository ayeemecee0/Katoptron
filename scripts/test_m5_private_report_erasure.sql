-- M5 production-safe rollback acceptance: full erasure + deletion-resistant cap.
begin;
select set_config('katoptron.m5_owner',gen_random_uuid()::text,true);
select set_config('katoptron.m5_other',gen_random_uuid()::text,true);
insert into auth.users(id) values
 (current_setting('katoptron.m5_owner')::uuid),
 (current_setting('katoptron.m5_other')::uuid);
select set_config('request.jwt.claim.sub',current_setting('katoptron.m5_owner'),true);
set local role authenticated;
with report as(
 insert into public.flock_community_submissions
 (latitude,longitude,description,consent_to_review,publication_consent)
 values(38.5816,-121.4944,'Rollback-only private synthetic report one, not a factual Flock camera observation.',true,false)
 returning submission_id)
select set_config('katoptron.m5_case_a',submission_id::text,true) from report;
do $check$
begin
 if not public.withdraw_own_community_report(current_setting('katoptron.m5_case_a')::uuid)
 then raise exception 'Contributor withdrawal failed';end if;
end $check$;
select set_config('request.jwt.claim.sub',current_setting('katoptron.m5_other'),true);
do $check$
begin
 if public.delete_withdrawn_community_report(current_setting('katoptron.m5_case_a')::uuid)
 then raise exception 'Cross-account report deletion allowed';end if;
end $check$;
select set_config('request.jwt.claim.sub',current_setting('katoptron.m5_owner'),true);
do $check$
begin
 if not public.delete_withdrawn_community_report(current_setting('katoptron.m5_case_a')::uuid)
 then raise exception 'Contributors cannot permanently delete withdrawn reports';end if;
 if exists(select 1 from public.flock_community_submissions
  where submission_id=current_setting('katoptron.m5_case_a')::uuid)
 then raise exception 'Owner content persisted after deletion';end if;

end $check$;
reset role;
do $check$
begin
 if exists(select 1 from public.flock_point_evidence_cases
  where case_key='tier_'||md5(current_setting('katoptron.m5_case_a')))
 then raise exception 'Withdrawn candidate persisted after report erasure';end if;
 if exists(select 1 from public.flock_point_evidence_attestations
  where case_key='tier_'||md5(current_setting('katoptron.m5_case_a')))
 then raise exception 'Derived attestation persisted after report erasure';end if;
end $check$;
set local role authenticated;
with report as(
 insert into public.flock_community_submissions
 (latitude,longitude,description,consent_to_review,publication_consent)
 values(38.5817,-121.4944,'Rollback-only synthetic second source for reporter-owned photo removal safety test.',true,false)
 returning submission_id)
select set_config('katoptron.m5_case_b',submission_id::text,true) from report;
do $check$
begin
 if not public.withdraw_own_community_report(current_setting('katoptron.m5_case_b')::uuid)
 then raise exception 'Second private synthetic report withdrawal failed';end if;
end $check$;
reset role;
-- Storage metadata fixture is NOT a blob. Rollback is mandatory.
insert into storage.objects(bucket_id,name,owner,owner_id)
values('katoptron-community-evidence',
 current_setting('katoptron.m5_owner')||'/'||current_setting('katoptron.m5_case_b')||'/evidence.webp',
 current_setting('katoptron.m5_owner')::uuid,current_setting('katoptron.m5_owner'));
set local role authenticated;
do $check$
begin
 begin
  perform public.delete_withdrawn_community_report(current_setting('katoptron.m5_case_b')::uuid);
  raise exception 'Attempted erasure succeeded without Storage photo deletion';
 exception when others then
  if sqlerrm not like 'Delete private report photos with Storage API before erasing report%'
  then raise;end if;
 end;
end $check$;
-- Third report consumes third submission regardless of first erasure.
insert into public.flock_community_submissions
 (latitude,longitude,description,consent_to_review,publication_consent)
 values(38.5818,-121.4944,'Rollback-only third report for 24-hour limit even after first report deletion.',true,false);
reset role;
do $check$
begin
 if (select count(*) from public.flock_private_submission_rate_events
 where user_id=current_setting('katoptron.m5_owner')::uuid)<>3
 then raise exception 'Rate ledger lost erased report';end if;
end $check$;
set local role authenticated;
do $check$
begin
 begin
  insert into public.flock_community_submissions
   (latitude,longitude,description,consent_to_review,publication_consent)
  values(38.5819,-121.4944,'Rollback-only fourth report must fail despite erasing the original case.',true,false);
  raise exception 'Rate-limit bypass through erasure';
 exception when others then
  if sqlerrm not like 'Maximum 3 reports per rolling 24 hours%' then raise;end if;
 end;
end $check$;
reset role;
do $check$
begin
 if to_regprocedure('public.set_community_review_status(uuid,text)') is not null
 then raise exception 'Unaudited two-parameter reviewer RPC still executable';end if;
 if has_table_privilege('anon','public.flock_private_submission_rate_events','SELECT')
 or has_table_privilege('authenticated','public.flock_private_submission_rate_events','SELECT')
 then raise exception 'Rate-event account metadata exposed publicly';end if;
end $check$;
rollback;
