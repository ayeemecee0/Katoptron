-- 150: Private, consent-based research workspaces. No public plate, route or
-- law-enforcement search data; source records remain publicly cited separately.
create table if not exists public.research_workspaces (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null references auth.users(id) on delete cascade,
 title text not null check (char_length(title) between 3 and 120),
 created_at timestamptz not null default now()
);
create table if not exists public.research_workspace_members (
 workspace_id uuid not null references public.research_workspaces(id) on delete cascade,
 user_id uuid not null references auth.users(id) on delete cascade,
 role text not null check (role in ('editor','viewer')),
 joined_at timestamptz not null default now(),
 primary key(workspace_id,user_id)
);
create index if not exists research_workspace_members_user_idx
 on public.research_workspace_members(user_id,workspace_id);
create table if not exists public.research_cases (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references public.research_workspaces(id) on delete cascade,
 created_by uuid not null references auth.users(id) on delete cascade,
 agency_key text not null check(char_length(agency_key) between 3 and 160),
 title text not null check(char_length(title) between 4 and 180),
 description text not null default '' check(char_length(description)<=5000),
 status text not null default 'open' check(status in ('open','investigating','waiting_for_records','resolved','archived')),
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 unique(id,workspace_id)
);
create index if not exists research_cases_workspace_idx
 on public.research_cases(workspace_id,updated_at desc);
create table if not exists public.research_case_requests (
 id uuid primary key default gen_random_uuid(),
 case_id uuid not null references public.research_cases(id) on delete cascade,
 created_by uuid not null references auth.users(id) on delete cascade,
 subject text not null default 'Public records request' check(char_length(subject) between 3 and 200),
 recipient text not null default '' check(char_length(recipient)<=250),
 body text not null default '' check(char_length(body)<=18000),
 status text not null default 'draft' check(status in ('draft','sent','awaiting_response','received','closed')),
 sent_on date, response_due_on date, response_received_on date,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create index if not exists research_requests_case_idx on public.research_case_requests(case_id);
create table if not exists public.research_case_notes(
 id uuid primary key default gen_random_uuid(),
 case_id uuid not null references public.research_cases(id) on delete cascade,
 author_id uuid not null references auth.users(id) on delete cascade,
 note text not null check(char_length(note) between 1 and 5000),
 source_url text check(source_url is null or (source_url ~ '^https://[^[:space:]]{5,1400}$')),
 created_at timestamptz not null default now()
);
create index if not exists research_case_notes_case_idx on public.research_case_notes(case_id,created_at desc);
create table if not exists public.research_case_files (
 id uuid primary key default gen_random_uuid(),
 case_id uuid not null references public.research_cases(id) on delete cascade,
 uploaded_by uuid not null references auth.users(id) on delete cascade,
 storage_path text not null unique check(char_length(storage_path) between 15 and 500),
 filename text not null check(char_length(filename) between 1 and 180),
 file_size integer not null check(file_size between 1 and 10485760),
 created_at timestamptz not null default now()
);
create index if not exists research_files_case_idx on public.research_case_files(case_id);

-- Owner can see/manage workspace; members may read the workspace they join.
alter table public.research_workspaces enable row level security;
alter table public.research_workspace_members enable row level security;
alter table public.research_cases enable row level security;
alter table public.research_case_requests enable row level security;
alter table public.research_case_notes enable row level security;
alter table public.research_case_files enable row level security;
revoke all on public.research_workspaces,public.research_workspace_members,
 public.research_cases,public.research_case_requests,public.research_case_notes,
 public.research_case_files from public,anon,authenticated;
grant select,insert,update,delete on public.research_workspaces,
 public.research_workspace_members,public.research_cases,public.research_case_requests,
 public.research_case_notes,public.research_case_files to authenticated;

create policy research_workspace_read on public.research_workspaces for select to authenticated
 using(owner_id=(select auth.uid()) or exists
 (select 1 from public.research_workspace_members m where m.workspace_id=id and m.user_id=(select auth.uid())));
create policy research_workspace_create on public.research_workspaces for insert to authenticated
 with check(owner_id=(select auth.uid()));
create policy research_workspace_edit on public.research_workspaces for update to authenticated
 using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));
create policy research_workspace_delete on public.research_workspaces for delete to authenticated
 using(owner_id=(select auth.uid()));

create policy research_member_read on public.research_workspace_members for select to authenticated
 using(user_id=(select auth.uid()));
create policy research_member_delete on public.research_workspace_members for delete to authenticated
 using(user_id=(select auth.uid()));
-- No direct member INSERT/UPDATE. Invite codes only accepted through restricted RPC.

create policy research_case_read on public.research_cases for select to authenticated
 using(exists(select 1 from public.research_workspaces w where w.id=workspace_id));
create policy research_case_insert on public.research_cases for insert to authenticated
 with check(created_by=(select auth.uid()) and exists(select 1 from public.research_workspaces w
 where w.id=workspace_id and (w.owner_id=(select auth.uid()) or exists
 (select 1 from public.research_workspace_members m where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
create policy research_case_edit on public.research_cases for update to authenticated
 using(exists(select 1 from public.research_workspaces w where w.id=workspace_id and
 (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m
 where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))))
 with check(exists(select 1 from public.research_workspaces w where w.id=workspace_id and
 (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m
 where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
create policy research_case_delete on public.research_cases for delete to authenticated
 using(exists(select 1 from public.research_workspaces w where w.id=workspace_id and w.owner_id=(select auth.uid())));

create policy research_request_read on public.research_case_requests for select to authenticated
 using(exists(select 1 from public.research_cases c where c.id=case_id));
create policy research_request_insert on public.research_case_requests for insert to authenticated
 with check(created_by=(select auth.uid()) and exists
 (select 1 from public.research_cases c join public.research_workspaces w on w.id=c.workspace_id
 where c.id=case_id and (w.owner_id=(select auth.uid()) or exists
 (select 1 from public.research_workspace_members m where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
create policy research_request_update on public.research_case_requests for update to authenticated
 using(exists(select 1 from public.research_cases c join public.research_workspaces w on w.id=c.workspace_id
 where c.id=case_id and (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))))
 with check(exists(select 1 from public.research_cases c join public.research_workspaces w on w.id=c.workspace_id
 where c.id=case_id and (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
create policy research_request_delete on public.research_case_requests for delete to authenticated
 using(exists(select 1 from public.research_cases c join public.research_workspaces w on w.id=c.workspace_id
 where c.id=case_id and w.owner_id=(select auth.uid())));

create policy research_note_read on public.research_case_notes for select to authenticated
 using(exists(select 1 from public.research_cases c where c.id=case_id));
create policy research_note_insert on public.research_case_notes for insert to authenticated
 with check(author_id=(select auth.uid()) and exists(select 1 from public.research_cases c
 join public.research_workspaces w on w.id=c.workspace_id where c.id=case_id
 and (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m
 where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
create policy research_note_delete on public.research_case_notes for delete to authenticated
 using(author_id=(select auth.uid()));

create policy research_file_read on public.research_case_files for select to authenticated
 using(exists(select 1 from public.research_cases c where c.id=case_id));
create policy research_file_insert on public.research_case_files for insert to authenticated
 with check(uploaded_by=(select auth.uid()) and exists(select 1 from public.research_cases c
 join public.research_workspaces w on w.id=c.workspace_id where c.id=case_id and
 storage_path like c.workspace_id::text||'/'||c.id::text||'/%' and
 (w.owner_id=(select auth.uid()) or exists(select 1 from public.research_workspace_members m
 where m.workspace_id=w.id and m.user_id=(select auth.uid()) and m.role='editor'))));
create policy research_file_delete on public.research_case_files for delete to authenticated
 using(uploaded_by=(select auth.uid()) or exists(select 1 from public.research_cases c
 join public.research_workspaces w on w.id=c.workspace_id where c.id=case_id and w.owner_id=(select auth.uid())));

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
