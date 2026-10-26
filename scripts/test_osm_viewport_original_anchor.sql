-- Source-backed OSM viewport cluster API must never position density badges
-- at fabricated camera coordinates, use privileged definer permissions, or
-- miscount the original community source observations.
do $anchor$
declare n bigint; cells integer;
begin
 if (select prosecdef from pg_proc where oid=
  'public.flock_public_osm_viewport_density_with_anchor(double precision,double precision,double precision,double precision,double precision)'::regprocedure)
 then raise exception 'Source-backed density view runs with privileged owner permissions';end if;
 if not has_function_privilege('anon',
  'public.flock_public_osm_viewport_density_with_anchor(double precision,double precision,double precision,double precision,double precision)'::regprocedure,'EXECUTE')
 then raise exception 'Community viewport density unavailable publicly';end if;
 select coalesce(sum(community_report_count),0),count(*) into n,cells
 from public.flock_public_osm_viewport_density_with_anchor(33.7,34.0,-84.5,-84.2,0.05);
 if n <> (select count(*) from public.flock_osm_community_points
           where latitude between 33.7 and 34.0 and longitude between -84.5 and -84.2
             and evidence_tier='community_osm')
 then raise exception 'Viewport source count differs from original OSM points';end if;
 if cells>500 then raise exception 'Viewport cluster result limit breached';end if;
 if exists(
 select 1 from public.flock_public_osm_viewport_density_with_anchor(33.7,34,-84.5,-84.2,0.05) d
 where d.community_report_count<=0 or d.example_latitude is null
 or d.example_longitude is null
 or d.example_latitude<33.7 or d.example_latitude>34
 or d.example_longitude< -84.5 or d.example_longitude> -84.2
 or d.example_latitude<d.cell_latitude-0.025-0.000001
 or d.example_latitude>d.cell_latitude+0.025+0.000001
 or d.example_longitude<d.cell_longitude-0.025-0.000001
 or d.example_longitude>d.cell_longitude+0.025+0.000001
 or not exists (
   select 1 from public.flock_osm_community_points p
   where p.evidence_tier='community_osm' and p.latitude=d.example_latitude
      and p.longitude=d.example_longitude
 )
 ) then raise exception 'Crowded OSM report cell anchor is fabricated or outside region';end if;
 begin
  perform * from public.flock_public_osm_viewport_density_with_anchor(
     17,72,-180,-64,0.005);
  raise exception 'Dangerous unbounded viewport source query accepted';
 exception when sqlstate '22023' then null;
 end;
end $anchor$;
