-- 138: M3 fail-closed source-specific manufacturer-label publication contract.
-- This protects Flock-only simulations against a future service-role GIS
-- import that bypasses the default='unconfirmed' by providing an explicit
-- source_flock_identified value. Database-owner editorial migrations can
-- classify sources only after separately reviewed original proof.
create or replace function public.guard_m3_positive_source_label_on_insert()
returns trigger language plpgsql security invoker set search_path = ''
as $guard$
begin
  if current_user='service_role'
     and new.source_flock_label_status <> 'unconfirmed' then
    raise exception 'Automated GIS imports cannot certify Flock manufacturer/source labels';
  end if;
  return new;
end;
$guard$;
revoke all on function public.guard_m3_positive_source_label_on_insert()
  from public,anon,authenticated,service_role;
drop trigger if exists guard_m3_positive_source_label_on_insert
  on public.flock_camera_locations;
create trigger guard_m3_positive_source_label_on_insert
before insert on public.flock_camera_locations
for each row execute function public.guard_m3_positive_source_label_on_insert();

comment on function public.guard_m3_positive_source_label_on_insert() is
'Prevents service-role ingestion from choosing positive Flock-source or generic LPR classifications. New GIS positions default unconfirmed until independently owner-reviewed source evidence exists. Does not affect prior reviewed classifications.';

create index if not exists flock_camera_source_flock_label_status_idx
 on public.flock_camera_locations(source_flock_label_status)
 where verification_status='verified';
