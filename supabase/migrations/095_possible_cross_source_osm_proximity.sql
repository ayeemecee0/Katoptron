-- 095: Spatial *possible overlaps*, NOT confirmed identity equivalence.
-- The official count is unchanged; each official record emits at most one
-- nearest community OSM observation within 30m and an ambiguity count.
-- Bounding boxes use existing OSM lat/lon indexes before Haversine.
create or replace view public.flock_public_cross_source_proximity
with (security_invoker=true)
as
select
 o.record_key as government_record_key,
 o.jurisdiction_label,
 hits.osm_key as nearest_osm_key,
 round((hits.meters::numeric),1) as separation_m,
 hits.match_count as osm_observations_within_30m,
 case
   when hits.match_count > 1 then 'ambiguous_nearby_osm'
   when hits.match_count = 1 then 'possible_spatial_overlap'
   else 'no_nearby_osm'
 end as matching_status
from public.flock_camera_locations o
left join lateral (
 select
  count(*)::integer as match_count,
  (array_agg(q.osm_key order by q.distance_m,q.osm_key))[1] as osm_key,
  min(q.distance_m) as meters
 from (
  select p.osm_key,
   2.0 * 6371000.0 * asin(least(1.0,sqrt(
       power(sin(radians((p.latitude-o.latitude)/2.0)),2)
      +cos(radians(o.latitude))*cos(radians(p.latitude))
       *power(sin(radians((p.longitude-o.longitude)/2.0)),2)
   ))) as distance_m
  from public.flock_osm_community_points p
  where p.latitude between o.latitude - 0.0003 and o.latitude + 0.0003
    and p.longitude between o.longitude - 0.0013 and o.longitude + 0.0013
    and p.evidence_tier='community_osm'
 ) q where q.distance_m <= 30.0
) hits on true
where o.verification_status='verified' and o.location_accuracy='exact';
revoke all on public.flock_public_cross_source_proximity
 from public,anon,authenticated,service_role;
grant select on public.flock_public_cross_source_proximity
 to anon,authenticated,service_role;
comment on view public.flock_public_cross_source_proximity is
'Geographic proximity candidates from independently sourced OSM and original-government locations. Within 30m is only possible overlap, never a verified same physical device. Multiple nearby OSM records are ambiguous. Do not reduce either source count automatically or infer active camera status.';
