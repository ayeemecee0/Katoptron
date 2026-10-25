-- 090: State evidence footprint includes vendor-primary agency disclosures
-- in a DISTINCT column. Never add vendor counts to georeferenced GIS pins.
create or replace view public.flock_public_state_evidence_index
with (security_invoker=true) as
with camera_counts as (
 select substring(c.jurisdiction_label from ', ([A-Z]{2})$') as state_code,
        count(*)::integer as verified_camera_points,
        count(distinct c.jurisdiction_label)::integer as verified_camera_jurisdictions
 from public.flock_camera_locations c
 where c.verification_status='verified' and c.location_accuracy='exact'
   and c.jurisdiction_label ~ ', [A-Z]{2}$'
 group by substring(c.jurisdiction_label from ', ([A-Z]{2})$')
),
program_counts as (
 select p.state_code,count(*)::integer as dated_program_records,
        count(*) filter (where p.program_status='terminated_at_source_date')::integer
          as terminated_program_records
 from public.flock_documented_programs p
 where p.record_status='verified' and p.state_code ~ '^[A-Z]{2}$'
 group by p.state_code
),
vendor_counts as (
 select v.state_code,count(distinct v.agency_key)::integer as vendor_disclosed_agencies
 from public.flock_vendor_portal_snapshots v
 where v.disclosure_status='verified_source_snapshot'
 group by v.state_code
)
select coalesce(c.state_code,p.state_code,v.state_code) as state_code,
       coalesce(c.verified_camera_points,0)::integer as verified_camera_points,
       coalesce(c.verified_camera_jurisdictions,0)::integer as verified_camera_jurisdictions,
       coalesce(p.dated_program_records,0)::integer as dated_program_records,
       coalesce(p.terminated_program_records,0)::integer as terminated_program_records,
       coalesce(v.vendor_disclosed_agencies,0)::integer as vendor_disclosed_agencies
from camera_counts c
full outer join program_counts p on p.state_code=c.state_code
full outer join vendor_counts v
  on v.state_code=coalesce(c.state_code,p.state_code)
where coalesce(c.state_code,p.state_code,v.state_code) ~ '^[A-Z]{2}$';
revoke all on public.flock_public_state_evidence_index
 from public,anon,authenticated,service_role;
grant select on public.flock_public_state_evidence_index
 to anon,authenticated,service_role;
comment on view public.flock_public_state_evidence_index is
'Separate verified GIS point counts, dated government program counts, and distinct agency counts with source-dated vendor-provided Flock portal snapshots. Vendor camera totals are NOT GIS points.';
