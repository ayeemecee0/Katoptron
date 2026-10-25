-- 099: Exact-count viewport fallback for dense national ODbL camera observations.
-- Uses only public, read-only community data. Never touches verified GIS cameras.
-- The function cannot invent camera points: returned coordinates are reporting
-- cell centers, labeled as density aggregates, not equipment positions.
create or replace function public.flock_public_osm_viewport_density(
 p_south double precision, p_north double precision,
 p_west double precision, p_east double precision,
 p_cell_degrees double precision)
returns table(cell_latitude double precision,cell_longitude double precision,
 community_report_count bigint)
language plpgsql stable security invoker
set search_path=public,pg_temp
as $$
begin
 if p_south is null or p_north is null or p_west is null or p_east is null
    or p_cell_degrees is null
    or p_south::text in ('NaN','Infinity','-Infinity')
    or p_north::text in ('NaN','Infinity','-Infinity')
    or p_west::text in ('NaN','Infinity','-Infinity')
    or p_east::text in ('NaN','Infinity','-Infinity')
    or p_south < 17 or p_north > 72 or p_west < -180 or p_east > -64
    or p_north <= p_south or p_east <= p_west
    or p_north-p_south > 4 or p_east-p_west > 6
    or p_cell_degrees not in (0.005,0.01,0.02,0.05,0.1,0.25,0.5) then
  raise exception 'Invalid bounded community density request' using errcode='22023';
 end if;
 return query
 select (floor(p.latitude/p_cell_degrees)*p_cell_degrees+
             p_cell_degrees/2)::double precision,
        (floor(p.longitude/p_cell_degrees)*p_cell_degrees+
             p_cell_degrees/2)::double precision,
        count(*)::bigint
 from public.flock_osm_community_points p
 where p.latitude >= p_south and p.latitude <= p_north
   and p.longitude >= p_west and p.longitude <= p_east
   and p.evidence_tier='community_osm'
 group by 1,2 order by 1,2
 limit 501;
end;
$$;
revoke all on function public.flock_public_osm_viewport_density(
 double precision,double precision,double precision,double precision,double precision)
 from public;
grant execute on function public.flock_public_osm_viewport_density(
 double precision,double precision,double precision,double precision,double precision)
 to anon, authenticated, service_role;
comment on function public.flock_public_osm_viewport_density(
 double precision,double precision,double precision,double precision,double precision)
 is 'Read-only bounded viewport OSM reporting-density groups. Returns up to 501 cells so the client detects truncation, and never an inferred camera position. NOT an official GIS record.';
