-- 154: No collaborator may rewrite an investigation's original author,
-- original workspace, or a request's original parent case.
create or replace function public.research_guard_case_identity()
returns trigger language plpgsql set search_path = '' as $$
begin
 if new.created_by is distinct from old.created_by or new.workspace_id is distinct from old.workspace_id then
  raise exception 'Original case author and workspace identity are immutable';
 end if;
 return new;
end $$;
drop trigger if exists research_cases_protect_identity on public.research_cases;
create trigger research_cases_protect_identity before update on public.research_cases
 for each row execute function public.research_guard_case_identity();
create or replace function public.research_guard_request_identity()
returns trigger language plpgsql set search_path = '' as $$
begin
 if new.created_by is distinct from old.created_by or new.case_id is distinct from old.case_id then
  raise exception 'Records request author and parent case are immutable';
 end if;
 return new;
end $$;
drop trigger if exists research_requests_protect_identity on public.research_case_requests;
create trigger research_requests_protect_identity before update on public.research_case_requests
 for each row execute function public.research_guard_request_identity();
revoke all on function public.research_guard_case_identity() from public,anon,authenticated;
revoke all on function public.research_guard_request_identity() from public,anon,authenticated;
