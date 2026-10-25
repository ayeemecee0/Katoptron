-- 093: National community-only 3-degree map overview without disclosing invented camera pins.
-- Every displayed marker at low zoom describes the size of a geographic
-- reporting cell, NOT an installation at the center of that cell.
create or replace view public.flock_public_osm_community_density
with (security_invoker=true) as
select (floor(latitude / 3.0) * 3.0 + 1.5)::double precision as cell_latitude,
       (floor(longitude / 3.0) * 3.0 + 1.5)::double precision as cell_longitude,
       count(*)::integer as community_report_count
from public.flock_osm_community_points
where evidence_tier='community_osm'
group by 1,2;
revoke all on public.flock_public_osm_community_density
 from public,anon,authenticated,service_role;
grant select on public.flock_public_osm_community_density
 to anon,authenticated,service_role;
comment on view public.flock_public_osm_community_density is
'COARSE 3-degree map reporting density from ODbL community-labeled Flock source points, not exact camera locations or camera counts in a physical grid center. Source can overlap government pins.';
