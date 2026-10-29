-- 152: one-use collaboration and private evidence storage.
-- Invite tokens are single-use, short-lived UUIDs; only workspace owners may
-- create/read them. No unauthenticated share URLs or automatic email invitations.
create table if not exists public.research_workspace_invites(
 token uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references public.research_workspaces(id) on delete cascade,
 created_by uuid not null references auth.users(id) on delete cascade,
 role text not null check(role in ('editor','viewer')),
 expires_at timestamptz not null default (now()+interval '7 days'),
 accepted_by uuid references auth.users(id) on delete set null,
 accepted_at timestamptz,
 created_at timestamptz not null default now(),
 check(expires_at<=created_at+interval '7 days'),
 check((accepted_by is null)=(accepted_at is null))
);
create index if not exists research_invites_workspace_idx on public.research_workspace_invites(workspace_id);
alter table public.research_workspace_invites enable row level security;
revoke all on public.research_workspace_invites from public,anon,authenticated;
grant select,insert,delete on public.research_workspace_invites to authenticated;
create policy research_invites_owner_read on public.research_workspace_invites for select to authenticated
 using(exists(select 1 from public.research_workspaces w where w.id=workspace_id and w.owner_id=(select auth.uid())));
create policy research_invites_owner_create on public.research_workspace_invites for insert to authenticated
 with check(created_by=(select auth.uid()) and accepted_by is null and accepted_at is null
 and expires_at>now() and exists(select 1 from public.research_workspaces w where w.id=workspace_id and w.owner_id=(select auth.uid())));
create policy research_invites_owner_delete on public.research_workspace_invites for delete to authenticated
 using(exists(select 1 from public.research_workspaces w where w.id=workspace_id and w.owner_id=(select auth.uid())));

create or replace function public.research_accept_invite(invite_token uuid)
returns uuid language plpgsql security definer set search_path = ''
as $$
declare v_workspace uuid; v_role text; v_uid uuid;
begin
 v_uid:=auth.uid();
 if v_uid is null or invite_token is null then raise exception 'Authenticated invite required'; end if;
 select i.workspace_id,i.role into v_workspace,v_role
 from public.research_workspace_invites i
 where i.token=invite_token and i.accepted_by is null and i.expires_at>now()
 for update;
 if v_workspace is null then raise exception 'Invalid, expired or used invite'; end if;
 if exists (select 1 from public.research_workspaces w where w.id=v_workspace and w.owner_id=v_uid) then
  raise exception 'Already workspace owner';
 end if;
 insert into public.research_workspace_members(workspace_id,user_id,role)
 values(v_workspace,v_uid,v_role)
 on conflict (workspace_id,user_id) do update set role=excluded.role;
 update public.research_workspace_invites set accepted_by=v_uid,accepted_at=now() where token=invite_token;
 return v_workspace;
end $$;
revoke all on function public.research_accept_invite(uuid) from public,anon;
grant execute on function public.research_accept_invite(uuid) to authenticated;

insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
 values ('research-case-files','research-case-files',false,10485760,
 array['application/pdf','image/png','image/jpeg','text/plain'])
 on conflict (id) do update set public=false,file_size_limit=10485760,
 allowed_mime_types=excluded.allowed_mime_types;
create policy research_storage_read on storage.objects for select to authenticated
 using(bucket_id='research-case-files' and exists (
  select 1 from public.research_cases c
  where name like c.workspace_id::text||'/'||c.id::text||'/%'));
create policy research_storage_insert on storage.objects for insert to authenticated
 with check(bucket_id='research-case-files' and exists(
 select 1 from public.research_cases c join public.research_workspaces w on w.id=c.workspace_id
 where name like c.workspace_id::text||'/'||c.id::text||'/%' and
 (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m
 where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
create policy research_storage_delete on storage.objects for delete to authenticated
 using(bucket_id='research-case-files' and exists(
 select 1 from public.research_cases c join public.research_workspaces w on w.id=c.workspace_id
 where name like c.workspace_id::text||'/'||c.id::text||'/%' and
 (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m
 where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
