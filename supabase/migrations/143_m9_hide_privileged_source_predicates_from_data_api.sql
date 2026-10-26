-- 143: Move two narrowly scoped public GIS authority predicates to existing
-- non-exposed katoptron_internal schema. Keep boolean authority checks in
-- published camera/coverage RLS without exposing SECURITY DEFINER RPC names
-- under /rest/v1/rpc/. The internal schema is NOT added to PostgREST
-- exposed schemas. These functions still reveal no private raw source data.

create or replace function katoptron_internal.gis_camera_authority_current(
 p_url text,p_jurisdiction text)
returns boolean language sql stable security definer set search_path=''
as $predicate$
 select exists(
  select 1 from public.trusted_flock_gis_sources s
   where s.gis_layer_url=p_url and s.jurisdiction_label=p_jurisdiction
     and s.source_status='verified'
 )
$predicate$;
revoke all on function katoptron_internal.gis_camera_authority_current(text,text)
 from public,anon,authenticated,service_role;
grant execute on function katoptron_internal.gis_camera_authority_current(text,text)
 to anon,authenticated,service_role;

create or replace function katoptron_internal.is_current_flock_polygon_camera_gis_source(
 p_source_key text)
returns boolean language sql stable security definer set search_path=''
as $predicate$
 select exists(
  select 1 from public.trusted_flock_gis_sources s
   where s.source_key=p_source_key and s.source_status='verified'
 )
$predicate$;
revoke all on function katoptron_internal.is_current_flock_polygon_camera_gis_source(text)
 from public,anon,authenticated,service_role;
grant execute on function katoptron_internal.is_current_flock_polygon_camera_gis_source(text)
 to anon,authenticated,service_role;

-- Keep the *identical* policy predicates and reader roles; only the routine
-- location moves behind the existing API-private schema.
alter policy only_verified_flock_camera_locations on public.flock_camera_locations
using (
 verification_status='verified' and
 (verification_method <> 'official_georeferenced_camera_record_v1' or
   katoptron_internal.gis_camera_authority_current(source_url,jurisdiction_label))
);
alter policy original_gov_coverage_areas_only on public.flock_documented_coverage_areas
using (
 geometry_status='verified' and
 ((government_source_key is not null and
    katoptron_internal.is_current_flock_polygon_camera_gis_source(government_source_key))
  or (government_program_key is not null and exists(
    select 1 from public.flock_documented_programs p
    where p.program_key=flock_documented_coverage_areas.government_program_key
      and p.record_status='verified' and p.program_status='documented_at_source_date'
  )))
);

-- Retain former public routine *definitions* for rollback diagnostics, but
-- revoke their Data API access. No public RLS policy continues to use them.
revoke all on function public.gis_camera_authority_current(text,text)
 from public,anon,authenticated,service_role;
revoke all on function public.is_current_flock_polygon_camera_gis_source(text)
 from public,anon,authenticated,service_role;
comment on function katoptron_internal.gis_camera_authority_current(text,text) is
 'Private-schema RLS-only government camera source eligibility boolean. It is executable by Postgres RLS reader roles but not exposed as a public Data API RPC.';
comment on function katoptron_internal.is_current_flock_polygon_camera_gis_source(text) is
 'Private-schema RLS-only government polygon authority boolean; original source still required; no raw private table access.';
