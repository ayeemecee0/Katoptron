-- 153: Owner-only team administration, without exposing auth.users or email addresses.
create or replace function public.research_list_collaborators(p_workspace uuid)
returns table(member_id uuid,member_role text,joined_at timestamptz)
language plpgsql security definer set search_path = ''
as $$
begin
 if auth.uid() is null or not exists(select 1 from public.research_workspaces w
   where w.id=p_workspace and w.owner_id=auth.uid()) then
  raise exception 'Workspace ownership required';
 end if;
 return query select m.user_id,m.role,m.joined_at from public.research_workspace_members m
  where m.workspace_id=p_workspace order by m.joined_at;
end $$;
revoke all on function public.research_list_collaborators(uuid) from public,anon;
grant execute on function public.research_list_collaborators(uuid) to authenticated;
create or replace function public.research_remove_collaborator(p_workspace uuid,p_user uuid)
returns boolean language plpgsql security definer set search_path = ''
as $$
declare deleted_member uuid;
begin
 if auth.uid() is null or p_user is null or not exists(select 1 from public.research_workspaces w
   where w.id=p_workspace and w.owner_id=auth.uid()) then
  raise exception 'Workspace ownership required';
 end if;
 delete from public.research_workspace_members m where m.workspace_id=p_workspace
   and m.user_id=p_user returning m.user_id into deleted_member;
 return deleted_member is not null;
end $$;
revoke all on function public.research_remove_collaborator(uuid,uuid) from public,anon;
grant execute on function public.research_remove_collaborator(uuid,uuid) to authenticated;
