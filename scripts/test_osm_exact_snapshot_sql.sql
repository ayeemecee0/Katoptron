-- Individual OSM render coordinates must reconcile exactly with public
-- source rows, never with community aggregate counts or official cameras.
do $qa$
declare n integer;source_n integer;payload text;stamp date;
begin
 if (select prosecdef from pg_proc
   where oid='public.flock_public_osm_exact_render_snapshot()'::regprocedure)
 then raise exception 'OSM render snapshot bypasses public row security';end if;
 if not has_function_privilege('anon',
    'public.flock_public_osm_exact_render_snapshot()'::regprocedure,'EXECUTE')
 then raise exception 'OSM all-zoom coordinate reader inaccessible';end if;
 select point_count,source_snapshot_date,coordinates_base64
 into n,stamp,payload from public.flock_public_osm_exact_render_snapshot();
 select count(*) into source_n from public.flock_osm_community_points
 where evidence_tier='community_osm'
 and latitude between 17 and 72 and longitude between -180 and -64;
 if n<>source_n then raise exception 'OSM point snapshot differs from exact source count';end if;
 if n>200000 then raise exception 'OSM source exceeds safe canvas bound';end if;
 if n>0 and (stamp is null or payload is null or
   octet_length(decode(payload,'base64'))<>n*8) then
   raise exception 'OSM compact coordinate source is missing or truncated';
 end if;
 if n=0 and payload is not null then raise exception 'Phantom original OSM points';end if;
 if exists(select 1 from public.flock_camera_locations where
     verification_method='community_osm_exact_render_snapshot')
 then raise exception 'OSM canvas must not promote community reports to government GIS';
 end if;
end $qa$;
