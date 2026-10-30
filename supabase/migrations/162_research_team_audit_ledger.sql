-- 162: owner-only team event ledger. No invitation secrets, emails or private case contents.
create table if not exists public.research_team_activity(
 id bigint generated always as identity primary key,
 workspace_id uuid not null references public.research_workspaces(id) on delete cascade,
 actor_id uuid,
 subject_id uuid,
 event_type text not null check(event_type in ('invite_created','invite_revoked','invite_accepted','member_joined','member_removed','role_changed')),
 role_before text check(role_before is null or role_before in ('viewer','editor')),
 role_after text check(role_after is null or role_after in ('viewer','editor')),
 happened_at timestamptz not null default now()
);
create index if not exists research_team_activity_owner_timeline on public.research_team_activity(workspace_id,happened_at desc);
alter table public.research_team_activity enable row level security;
revoke all on public.research_team_activity from public,anon,authenticated;
grant select on public.research_team_activity to authenticated;
create policy research_team_activity_owner_read on public.research_team_activity for select to authenticated
 using (exists(select 1 from public.research_workspaces w where w.id=workspace_id and w.owner_id=(select auth.uid())));
comment on table public.research_team_activity is 'Internal append-only owner-visible team role/invite metadata, no email/token/source/case body.';

create schema if not exists katoptron_private;
revoke all on schema katoptron_private from public,anon,authenticated;
create or replace function katoptron_private.audit_research_team_changes()
returns trigger language plpgsql security definer set search_path=''
as $$
declare
 ws uuid;
 kind text;
 target uuid;
 old_role text;
 new_role text;
begin
 if TG_TABLE_NAME='research_workspace_members' then
  if TG_OP='DELETE' then ws:=old.workspace_id;target:=old.user_id;
  else ws:=new.workspace_id;target:=new.user_id;end if;
  if TG_OP='INSERT' then kind:='member_joined';new_role:=new.role;
  elsif TG_OP='DELETE' then kind:='member_removed';old_role:=old.role;
  elsif TG_OP='UPDATE' and old.role is distinct from new.role then
   kind:='role_changed';old_role:=old.role;new_role:=new.role;
  end if;
 elsif TG_TABLE_NAME='research_workspace_invites' then
  if TG_OP='DELETE' then ws:=old.workspace_id;else ws:=new.workspace_id;end if;
  if TG_OP='INSERT' then kind:='invite_created';new_role:=new.role;
  elsif TG_OP='DELETE' and old.accepted_by is null then kind:='invite_revoked';old_role:=old.role;
  elsif TG_OP='UPDATE' and old.accepted_by is null and new.accepted_by is not null
    then kind:='invite_accepted';target:=new.accepted_by;new_role:=new.role;
  end if;
 else raise exception 'Unsupported team audit source';
 end if;
 if kind is not null then
  insert into public.research_team_activity(workspace_id,actor_id,subject_id,event_type,role_before,role_after)
   values(ws,auth.uid(),target,kind,old_role,new_role);
 end if;
 if TG_OP='DELETE' then return old;end if;
 return new;
end $$;
revoke all on function katoptron_private.audit_research_team_changes() from public,anon,authenticated;

drop trigger if exists audit_research_member_change on public.research_workspace_members;
create trigger audit_research_member_change after insert or update or delete on public.research_workspace_members
 for each row execute function katoptron_private.audit_research_team_changes();
drop trigger if exists audit_research_invite_change on public.research_workspace_invites;
create trigger audit_research_invite_change after insert or update or delete on public.research_workspace_invites
 for each row execute function katoptron_private.audit_research_team_changes();
