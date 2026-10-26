-- Community density visual-anchor repair: draw aggregate badges at a REAL
-- reported OSM location within the cell, never at an offshore mathematical
-- cell center. Example position is an unverified OSM observation, not a
-- verified camera or the location of every report represented by the badge.
-- Adds columns to the existing public security-invoker view; no source
-- data modifications, government promotions, or server-side secrets.
create or replace view public.flock_public_osm_community_density
with (security_invoker=true) as
select
 floor(p.latitude/3.0::double precision)*3.0::double precision
   +1.5::double precision as cell_latitude,
 floor(p.longitude/3.0::double precision)*3.0::double precision
   +1.5::double precision as cell_longitude,
 count(*)::integer as community_report_count,
 (array_agg(p.latitude order by p.osm_key))[1] as example_latitude,
 (array_agg(p.longitude order by p.osm_key))[1] as example_longitude
from public.flock_osm_community_points p
where p.evidence_tier='community_osm'
group by 1,2;

grant select on public.flock_public_osm_community_density to anon,authenticated;
comment on view public.flock_public_osm_community_density is
'3-degree OSM report-density aggregates. Display anchors are actual example source coordinates, NOT centroid camera positions, manufacturer proof, unique installed devices or detections.';
