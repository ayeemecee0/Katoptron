-- Source conversion scorecard. Counts represent distinct states of evidence, not camera totals added together.
create or replace view public.flock_public_acquisition_scorecard
with (security_invoker=true) as
select
 (select count(*) from public.flock_camera_locations
  where verification_status='verified' and location_accuracy='exact')::bigint as original_gis_points,
 (select count(distinct jurisdiction_label) from public.flock_camera_locations
  where verification_status='verified' and location_accuracy='exact')::bigint as original_gis_jurisdictions,
 (select count(*) from public.flock_public_tiered_camera_points
  where evidence_tier='source_attributed_unconfirmed')::bigint as source_attributed_unconfirmed_points,
 (select count(*) from public.flock_osm_community_points)::bigint as community_observations,
 (select count(*) from public.flock_documented_programs
  where record_status='verified')::bigint as documented_government_programs;
revoke all on public.flock_public_acquisition_scorecard from public,anon,authenticated;
grant select on public.flock_public_acquisition_scorecard to anon,authenticated,service_role;
comment on view public.flock_public_acquisition_scorecard is
'Evidence tiers are NOT additive unique cameras. Reports include overlaps, historical programs and unverified community observations. A source-attributed camera observation is not a verified Flock device.';
