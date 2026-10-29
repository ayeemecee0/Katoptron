-- Keep privilege changes owner-only with explicit user UUID and workspace.
create or replace function public.research_change_collaborator_role(p_workspace uuid,p_user uuid,p_role text)
returns boolean language plpgsql security definer set search_path = ''
as $$
declare changed uuid;
begin
 if auth.uid() is null or p_user is null or p_role not in ('viewer','editor') or
 not exists(select 1 from public.research_workspaces w where w.id=p_workspace and w.owner_id=auth.uid())
 then raise exception 'Owner permission and valid collaborator role required'; end if;
 update public.research_workspace_members m set role=p_role
 where m.workspace_id=p_workspace and m.user_id=p_user
 returning m.user_id into changed;
 return changed is not null;
end $$;
revoke all on function public.research_change_collaborator_role(uuid,uuid,text) from public,anon;
grant execute on function public.research_change_collaborator_role(uuid,uuid,text) to authenticated;
