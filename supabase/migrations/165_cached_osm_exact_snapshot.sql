-- Cache nationwide original OSM coordinates once after each authenticated
-- source import. A per-visitor ordered binary aggregation over >116k original
-- records intermittently exceeded PostgREST's statement timeout (57014).
-- One public immutable read model, no source or government evidence promotion.
create table if not exists public.flock_osm_exact_snapshot_cache (
  singleton boolean primary key default true check (singleton),
  point_count integer not null check (point_count between 90000 and 200000),
  source_snapshot_date date not null,
  coordinates_base64 text not null,
  refreshed_at timestamptz not null default now(),
  constraint osm_exact_cache_nonempty check (octet_length(coordinates_base64)>0)
);
alter table public.flock_osm_exact_snapshot_cache enable row level security;
revoke all on public.flock_osm_exact_snapshot_cache from public, anon, authenticated;
grant select on public.flock_osm_exact_snapshot_cache to anon, authenticated, service_role;
grant insert, update on public.flock_osm_exact_snapshot_cache to service_role;
drop policy if exists public_exact_osm_read on public.flock_osm_exact_snapshot_cache;
create policy public_exact_osm_read on public.flock_osm_exact_snapshot_cache
 for select to anon, authenticated using (singleton);

create or replace function public.katoptron_refresh_osm_exact_snapshot_cache()
returns integer language plpgsql security invoker
set search_path = public, pg_temp
as $$
declare
 n integer;
 stamp date;
 payload text;
begin
 select count(*)::integer,
        max(source_snapshot_date),
        encode(string_agg(
            pg_catalog.int4send(round(latitude*10000000)::integer)
            || pg_catalog.int4send(round(longitude*10000000)::integer),
            ''::bytea order by osm_key), 'base64')
 into n, stamp, payload
 from public.flock_osm_community_points
 where evidence_tier='community_osm'
   and latitude between 17 and 72
   and longitude between -180 and -64;
 if n not between 90000 and 200000 or stamp is null or payload is null or
    octet_length(decode(payload,'base64')) <> n*8 then
    raise exception 'Unreconciled national OSM original-coordinate source';
 end if;
 insert into public.flock_osm_exact_snapshot_cache
  (singleton,point_count,source_snapshot_date,coordinates_base64,refreshed_at)
 values (true,n,stamp,payload,now())
 on conflict(singleton) do update set
  point_count=excluded.point_count,
  source_snapshot_date=excluded.source_snapshot_date,
  coordinates_base64=excluded.coordinates_base64,
  refreshed_at=excluded.refreshed_at;
 return n;
end $$;
revoke all on function public.katoptron_refresh_osm_exact_snapshot_cache()
 from public, anon, authenticated;
grant execute on function public.katoptron_refresh_osm_exact_snapshot_cache()
 to service_role;
comment on function public.katoptron_refresh_osm_exact_snapshot_cache()
 is 'Private authenticated importer-only public OSM source cache refresh. No individual plate data or government camera inference.';

-- Exact same public RPC schema, unchanged per-observation coordinates.
-- Query is now a single public RLS-protected row rather than a huge sort.
create or replace function public.flock_public_osm_exact_render_snapshot()
returns table(point_count integer, source_snapshot_date date, coordinates_base64 text)
language sql stable security invoker set search_path=public,pg_temp
as $$
 select c.point_count,c.source_snapshot_date,c.coordinates_base64
 from public.flock_osm_exact_snapshot_cache c where c.singleton;
$$;
revoke all on function public.flock_public_osm_exact_render_snapshot()
 from public, anon, authenticated;
grant execute on function public.flock_public_osm_exact_render_snapshot()
 to anon,authenticated,service_role;
comment on function public.flock_public_osm_exact_render_snapshot()
 is 'Precomputed public OSM original-coordinate snapshot; same 8-byte unverified individual source locations and timestamp, no camera promotion.';

-- Seed cached public data from currently authenticated original OSM rows.
select public.katoptron_refresh_osm_exact_snapshot_cache();
