-- 116: read-only full OSM source positions in compact signed-int32 pairs.
-- Exact reported coordinates, not coarse aggregates or invented grid centers.
-- Each pair = latitude*1e7 and longitude*1e7 (network-byte-order int32).
-- 116159 points currently occupy 929272 binary bytes, suitable for a
-- single bounded public read; no OSM submitter details, person, plate or route.
create function public.flock_public_osm_exact_render_snapshot()
returns table(point_count integer,source_snapshot_date date,coordinates_base64 text)
language sql stable security invoker
set search_path=public,pg_temp
as $$
  select count(*)::integer,
         max(source_snapshot_date),
         encode(string_agg(
             pg_catalog.int4send(round(latitude*10000000)::integer)
             ||pg_catalog.int4send(round(longitude*10000000)::integer),
             ''::bytea order by osm_key), 'base64')
  from public.flock_osm_community_points
  where evidence_tier='community_osm'
    and latitude between 17 and 72 and longitude between -180 and -64;
$$;
revoke all on function public.flock_public_osm_exact_render_snapshot()
 from public,anon,authenticated;
grant execute on function public.flock_public_osm_exact_render_snapshot()
 to anon,authenticated,service_role;
comment on function public.flock_public_osm_exact_render_snapshot()
 is 'Read-only complete OSM community report coordinates, 8-byte big-endian signed int32 pairs at 1e-7 degree precision. Source-attributed and UNVERIFIED. No clustering or government camera promotion.';

