-- 141: Evidence analytics must never count manufacturer-unknown generic LPR
-- coordinates or source-attributed/unconfirmed camera leads as independently
-- corroborated Flock equipment. All inputs are already RLS-approved public
-- source views or published original GIS points. No private community reports.

create or replace view public.flock_analytics_states
with (security_invoker=true) as
with types as (
 select e.state_code,
  count(*)::integer as total_accountability_records,
  count(*) filter(where e.event_type='agenda_mention')::integer as agenda_mentions,
  count(*) filter(where e.event_type='executed_contract')::integer as documented_signed_contracts
 from public.flock_accountability_directory e
 where e.state_code ~ '^[A-Z]{2}$' group by e.state_code
),
camera_labels as (
 select substring(c.jurisdiction_label, ', ([A-Z]{2})$') as state_code,
   count(*) filter(where c.source_flock_label_status='source_flock_identified')::integer as flock_source_points,
   count(*) filter(where c.source_flock_label_status='generic_lpr')::integer as generic_lpr_points
 from public.flock_camera_locations c
 where c.verification_status='verified' and c.location_accuracy='exact'
   and c.jurisdiction_label ~ ', [A-Z]{2}$'
 group by substring(c.jurisdiction_label, ', ([A-Z]{2})$')
)
select coalesce(s.state_code,t.state_code,c.state_code) as state_code,
 coalesce(s.verified_camera_points,0)::integer as verified_exact_gis_points,
 coalesce(s.verified_camera_jurisdictions,0)::integer as verified_point_jurisdictions,
 coalesce(s.dated_program_records,0)::integer as source_dated_program_records,
 coalesce(s.terminated_program_records,0)::integer as terminated_as_of_source,
 coalesce(t.total_accountability_records,0)::integer as accountability_records,
 coalesce(t.agenda_mentions,0)::integer as agenda_mentions,
 coalesce(t.documented_signed_contracts,0)::integer as signed_contracts,
 coalesce(c.flock_source_points,0)::integer as source_flock_labeled_points,
 coalesce(c.generic_lpr_points,0)::integer as generic_lpr_points
from public.flock_public_state_evidence_index s
full join types t on t.state_code=s.state_code
full join camera_labels c on c.state_code=coalesce(s.state_code,t.state_code)
where coalesce(s.state_code,t.state_code,c.state_code) ~ '^[A-Z]{2}$';
revoke all on public.flock_analytics_states from public,anon,authenticated,service_role;
grant select on public.flock_analytics_states to anon,authenticated,service_role;

create or replace view public.flock_analytics_overview
with (security_invoker=true) as
select
 (select count(*)::integer from public.flock_camera_locations
   where verification_status='verified' and location_accuracy='exact') as exact_government_points,
 -- Only independently corroborated *published* points. Unconfirmed city GIS
 -- and private user submissions DO NOT qualify as corroborated.
 (select count(*)::integer from public.flock_public_tiered_camera_points
   where evidence_tier='independently_corroborated') as separately_corroborated_points,
 (select count(*)::integer from public.flock_documented_programs
   where record_status='verified') as source_dated_programs,
 (select count(*)::integer from public.flock_documented_programs
   where record_status='verified' and program_status='terminated_at_source_date') as terminated_at_source_date,
 (select count(*)::integer from public.flock_accountability_directory) as accountability_records,
 (select count(*)::integer from public.flock_accountability_directory
   where event_type='executed_contract') as documented_signed_contracts,
 (select count(*)::integer from public.flock_individual_public_positions) as documented_individual_positions,
 (select count(*)::integer from public.flock_accountability_roles) as sourced_professional_roles,
 (select count(*)::integer from public.flock_analytics_states
   where verified_exact_gis_points>0) as states_with_exact_gis_evidence,
 (select count(*)::integer from public.flock_analytics_states) as states_with_any_documented_evidence,
 (select count(*)::integer from public.flock_camera_locations
   where verification_status='verified' and location_accuracy='exact'
    and source_flock_label_status='source_flock_identified') as source_flock_labeled_points,
 (select count(*)::integer from public.flock_camera_locations
   where verification_status='verified' and location_accuracy='exact'
    and source_flock_label_status='generic_lpr') as generic_lpr_points,
 (select count(*)::integer from public.flock_public_tiered_camera_points
   where evidence_tier='source_attributed_unconfirmed') as source_attributed_unconfirmed_points,
 (select count(*)::integer from public.flock_public_tiered_camera_points
   where evidence_tier='government_verified') as additional_government_verified_points;
revoke all on public.flock_analytics_overview from public,anon,authenticated,service_role;
grant select on public.flock_analytics_overview to anon,authenticated,service_role;

comment on view public.flock_analytics_overview is
'Count each distinct published evidence tier separately; 293 source Flock-labeled government GIS points and 23 generic LPR points must not be conflated; source-attributed provisional points are NOT independently corroborated or active hardware. No private reporter metrics.';
comment on view public.flock_analytics_states is
'State breakdown of published government evidence with explicit Flock source-label versus manufacturer-unconfirmed LPR split, plus program and accountability-only jurisdictions.';
