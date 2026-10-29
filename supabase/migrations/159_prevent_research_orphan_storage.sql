-- Prevent direct case/workspace deletion from leaving inaccessible private
-- Storage blobs. Clients must first remove actual Storage objects through API.
create or replace function public.research_block_orphan_storage()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
 if exists(select 1 from storage.objects o
 where o.bucket_id='research-case-files'
   and o.name like old.workspace_id::text||'/'||old.id::text||'/%') then
  raise exception 'Delete private Storage attachments through Storage API before deleting the case';
 end if;
 return old;
end $$;
revoke all on function public.research_block_orphan_storage() from public,anon,authenticated;
drop trigger if exists research_case_requires_storage_cleanup on public.research_cases;
create trigger research_case_requires_storage_cleanup before delete on public.research_cases
 for each row execute function public.research_block_orphan_storage();
