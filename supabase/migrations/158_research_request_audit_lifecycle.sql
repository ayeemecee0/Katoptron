-- An immutable history of status and date edits made through authenticated cases.
create table if not exists public.research_request_activity(
 id uuid primary key default gen_random_uuid(),
 request_id uuid not null references public.research_case_requests(id) on delete cascade,
 actor_id uuid references auth.users(id) on delete set null,
 previous_status text not null,
 new_status text not null,
 previous_due_on date,
 new_due_on date,
 action_at timestamptz not null default now()
);
create index if not exists research_request_activity_request_idx on public.research_request_activity(request_id,action_at desc);
alter table public.research_request_activity enable row level security;
revoke all on public.research_request_activity from public,anon,authenticated;
grant select on public.research_request_activity to authenticated;
create policy research_request_activity_read on public.research_request_activity
 for select to authenticated
 using(exists(select 1 from public.research_case_requests r where r.id=request_id));
create or replace function public.research_record_request_change()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
 if old.status is distinct from new.status or
    old.sent_on is distinct from new.sent_on or
    old.response_due_on is distinct from new.response_due_on or
    old.response_received_on is distinct from new.response_received_on then
  insert into public.research_request_activity(request_id,actor_id,previous_status,new_status,
    previous_due_on,new_due_on) values(old.id,auth.uid(),old.status,new.status,
    old.response_due_on,new.response_due_on);
 end if;
 return new;
end $$;
revoke all on function public.research_record_request_change() from public,anon,authenticated;
drop trigger if exists research_requests_record_lifecycle on public.research_case_requests;
create trigger research_requests_record_lifecycle after update on public.research_case_requests
 for each row execute function public.research_record_request_change();
