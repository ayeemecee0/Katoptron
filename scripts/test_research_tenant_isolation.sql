-- Isolated CI PostgreSQL only. Never invoke this fixture against production.
\set ON_ERROR_STOP on
create schema auth;
create schema storage;
create role anon;
create role authenticated;
create role service_role;
create table auth.users(id uuid primary key);
create function auth.uid() returns uuid language sql stable as $$
 select nullif(current_setting('request.jwt.claim.sub',true),'')::uuid $$;
grant usage on schema public,auth,storage to authenticated,anon,service_role;
create table storage.buckets(id text primary key,name text not null,public boolean,
 file_size_limit integer,allowed_mime_types text[]);
create table storage.objects(bucket_id text,name text,primary key(bucket_id,name));
alter table storage.objects enable row level security;
grant select,insert,delete on storage.objects to authenticated;
\i supabase/migrations/150_research_workspace_cases_and_private_files.sql
\i supabase/migrations/151_research_workspace_rls_policies.sql
\i supabase/migrations/152_research_workspace_invites_and_storage.sql
\i supabase/migrations/153_research_collaborator_owner_controls.sql
\i supabase/migrations/154_research_immutable_case_and_request_identity.sql
\i supabase/migrations/157_research_collaborator_roles.sql
\i supabase/migrations/158_research_request_audit_lifecycle.sql
\i supabase/migrations/159_prevent_research_orphan_storage.sql
\i supabase/migrations/155_original_government_version_review_queue.sql
\i supabase/migrations/160_fix_original_source_url_check.sql
insert into public.flock_original_page_versions(source_id,source_url,locality_key,source_date,text_sha256,anchor_context_sha256)
 values('official-frankfort-version-test',
 'https://www.frankfort.ky.gov/m/NewsFlash/Home/Detail/274',
 'frankfort|KY','2026-10-13',repeat('a',64),repeat('b',64));
select 1/(case when (select count(*) from public.flock_original_page_versions)=1 then 1 else 0 end) as valid_original_receipt;
select 1/(case when ('https://gov.example.gov/public bad' ~ '^https://[^[:space:]]+$')=false then 1 else 0 end) as unsafe_url_rejected;



insert into auth.users values
 ('11111111-1111-1111-1111-111111111111'),
 ('22222222-2222-2222-2222-222222222222'),
 ('33333333-3333-3333-3333-333333333333');
insert into public.research_workspaces(id,owner_id,title) values
 ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  '11111111-1111-1111-1111-111111111111','Private source research');
insert into public.research_cases(id,workspace_id,created_by,agency_key,title)
 values('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  '11111111-1111-1111-1111-111111111111','folsom|CA','Government contract research');
insert into public.research_case_requests(id,case_id,created_by,subject)
 values('cccccccc-cccc-cccc-cccc-cccccccccccc',
  'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  '11111111-1111-1111-1111-111111111111','Agency primary documents');
insert into storage.objects(bucket_id,name) values
 ('research-case-files','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb/original.pdf');
insert into public.research_workspace_members(workspace_id,user_id,role)
 values('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  '22222222-2222-2222-2222-222222222222','viewer');

set role authenticated;
set request.jwt.claim.sub='33333333-3333-3333-3333-333333333333';
do $$
begin
 if (select count(*) from public.research_cases)<>0 then raise exception 'Outsider read private case';end if;
 if (select count(*) from public.research_case_requests)<>0 then raise exception 'Outsider read private request';end if;
 if (select count(*) from storage.objects where bucket_id='research-case-files')<>0 then raise exception 'Outsider read private response';end if;
 if (select count(*) from public.research_workspaces)<>0 then raise exception 'Outsider read private workspace';end if;
end $$;

set request.jwt.claim.sub='22222222-2222-2222-2222-222222222222';
do $$
begin
 if (select count(*) from public.research_cases)<>1 then raise exception 'Accepted viewer cannot read case';end if;
 if (select count(*) from public.research_case_requests)<>1 then raise exception 'Viewer cannot read requests';end if;
 if (select count(*) from storage.objects where bucket_id='research-case-files')<>1 then raise exception 'Viewer cannot read response';end if;
end $$;
-- Viewers cannot edit a case or create a new one.
do $$
declare n integer;
begin
 update public.research_cases set status='investigating'
  where id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
 get diagnostics n=row_count;
 if n<>0 then raise exception 'Viewer illegally edited case';end if;
 begin
  insert into public.research_cases(workspace_id,created_by,agency_key,title)
  values ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
          '22222222-2222-2222-2222-222222222222','test|CA','Forbidden viewer edit');
  raise exception 'Viewer illegally inserted new case';
 exception when insufficient_privilege then null; end;
end $$;

-- Owner may change roles; an unrelated user may not.
set request.jwt.claim.sub='33333333-3333-3333-3333-333333333333';
do $$
begin
 begin
  perform public.research_change_collaborator_role('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
   '22222222-2222-2222-2222-222222222222','editor');
  raise exception 'Non-owner changed member role';
 exception when raise_exception then
  if sqlerrm='Non-owner changed member role' then raise; end if;
 end;
end $$;
set request.jwt.claim.sub='11111111-1111-1111-1111-111111111111';
do $$
begin
 if not public.research_change_collaborator_role('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
 '22222222-2222-2222-2222-222222222222','editor') then
  raise exception 'Owner role change failed';
 end if;
end $$;

set request.jwt.claim.sub='22222222-2222-2222-2222-222222222222';
update public.research_cases set status='investigating'
 where id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
update public.research_case_requests set status='sent',
 response_due_on='2026-11-15' where id='cccccccc-cccc-cccc-cccc-cccccccccccc';
do $$
begin
 if (select count(*) from public.research_request_activity
  where request_id='cccccccc-cccc-cccc-cccc-cccccccccccc' and new_status='sent')<>1 then
  raise exception 'Request timeline did not record editor change';
 end if;
end $$;

-- Only owner may delete, and direct deletion is prevented while Storage bytes remain.
set request.jwt.claim.sub='11111111-1111-1111-1111-111111111111';
do $$
begin
 begin
  delete from public.research_cases where id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
  raise exception 'Case deletion improperly orphaned private blob';
 exception when raise_exception then
  if sqlerrm='Case deletion improperly orphaned private blob' then raise; end if;
 end;
end $$;
reset role;
delete from storage.objects where bucket_id='research-case-files';
set role authenticated;
set request.jwt.claim.sub='11111111-1111-1111-1111-111111111111';
delete from public.research_cases where id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
do $$
begin
 if (select count(*) from public.research_case_requests)<>0 then raise exception 'Case draft remained';end if;
 if (select count(*) from public.research_request_activity)<>0 then raise exception 'Request edit history remained';end if;
end $$;
reset role;
select 'RESEARCH_AUTH_TENANT_LIFECYCLE_PASS' as result;
