-- 099 source-separated OSM fallback has bounded inputs, independent tier,
-- publicly readable aggregates, and never publishes a fabricated exact point.
begin;
do $$
declare n bigint;
begin
 if (select prosecdef from pg_proc where oid=
   'public.flock_public_osm_viewport_density(double precision,double precision,double precision,double precision,double precision)'::regprocedure)
 then raise exception 'Viewport aggregator unexpectedly runs with definer privileges'; end if;
 if not has_function_privilege('anon',
   'public.flock_public_osm_viewport_density(double precision,double precision,double precision,double precision,double precision)'::regprocedure,'EXECUTE')
 then raise exception 'Public viewer cannot retrieve community density'; end if;
 select coalesce(sum(community_report_count),0) into n
 from public.flock_public_osm_viewport_density(35,36,-87,-86,0.1);
 if n <> (select count(*) from public.flock_osm_community_points
     where latitude between 35 and 36 and longitude between -87 and -86)
 then raise exception 'Bounded source density not equal to original public observations'; end if;
 if (select count(*) from public.flock_public_osm_viewport_density(35,36,-87,-86,0.1))>501
 then raise exception 'RPC omitted reporting density upper bound'; end if;
 begin
  perform * from public.flock_public_osm_viewport_density(17,72,-180,-64,0.005);
  raise exception 'Unbounded national fine-grained query unexpectedly accepted';
 exception when sqlstate '22023' then null;
 end;
 begin
  perform * from public.flock_public_osm_viewport_density(35,36,-87,-86,0.001);
  raise exception 'Arbitrary cell width unexpectedly accepted';
 exception when sqlstate '22023' then null;
 end;
end $$;
rollback;
