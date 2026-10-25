-- 105: reconcile legacy private point cases with public verified locations.
-- This ledger does not change case classification, attestations or public pins.
create table if not exists public.flock_gis_point_case_dispositions(
 case_key text primary key references public.flock_point_evidence_cases(case_key),
 disposition text not null check(disposition in
    ('resolved_same_published_camera','parked_source_endorsement',
     'awaiting_separate_original_camera_evidence')),
 explanation_code text not null check(explanation_code ~ '^[a-z_]{5,100}$'),
 original_public_record_key text references public.flock_camera_locations(record_key),
 updated_at timestamptz not null default now(),
 next_action_after timestamptz,
 constraint resolved_has_public_record check(
   (disposition='resolved_same_published_camera') =
   (original_public_record_key is not null))
);
alter table public.flock_gis_point_case_dispositions enable row level security;
revoke all on public.flock_gis_point_case_dispositions from public,anon,authenticated;
grant select,insert,update on public.flock_gis_point_case_dispositions to service_role;
create or replace function public.reconcile_flock_gis_point_case_dispositions()
returns jsonb language plpgsql security invoker set search_path=public,pg_temp
as $$
declare affected integer;
begin
 with chosen as (
  select c.case_key, c.jurisdiction_label,
    (select g.record_key from public.flock_camera_locations g
      where g.verification_status='verified'
        and g.location_accuracy='exact'
        and g.jurisdiction_label=c.jurisdiction_label
        and abs(g.latitude-c.latitude)<0.00015
        and abs(g.longitude-c.longitude)<0.00015
      order by abs(g.latitude-c.latitude)+abs(g.longitude-c.longitude),g.record_key
      limit 1) official_key
  from public.flock_point_evidence_cases c
  where c.classification='candidate'
    and c.jurisdiction_label in ('Live Oak, TX','Menifee, CA','Shelbyville, TN')
 ), shaped as (
   select case_key,
    case when official_key is not null then 'resolved_same_published_camera'
         when jurisdiction_label in ('Menifee, CA','Shelbyville, TN')
              then 'parked_source_endorsement'
         else 'awaiting_separate_original_camera_evidence' end as disposition,
    case when official_key is not null then 'same_jurisdiction_coordinates_already_published'
         when jurisdiction_label in ('Menifee, CA','Shelbyville, TN')
              then 'specific_layer_and_installation_status_unproven'
         else 'source_and_camera_identity_unresolved' end as reason,
    official_key
   from chosen
 ), merged as (
  insert into public.flock_gis_point_case_dispositions
   (case_key,disposition,explanation_code,original_public_record_key,next_action_after)
  select case_key,disposition,reason,official_key,
   case when official_key is null then now()+interval '90 days' else null end
   from shaped
  on conflict(case_key) do update set
   disposition=excluded.disposition,
   explanation_code=excluded.explanation_code,
   original_public_record_key=excluded.original_public_record_key,
   updated_at=now(),
   next_action_after=case
      when public.flock_gis_point_case_dispositions.disposition<>
           excluded.disposition then excluded.next_action_after
      else public.flock_gis_point_case_dispositions.next_action_after end
  returning case_key
 ) select count(*) into affected from merged;
 return jsonb_build_object('classified_private_cases',affected);
end;$$;
revoke all on function public.reconcile_flock_gis_point_case_dispositions()
 from public,anon,authenticated;
grant execute on function public.reconcile_flock_gis_point_case_dispositions()
 to service_role;
