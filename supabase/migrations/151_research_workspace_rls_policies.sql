-- 151: tenant isolation policies for workspaces and case materials.
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

