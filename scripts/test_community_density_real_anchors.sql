-- Coarse community density render anchors must be real original OSM points,
-- never mathematical water/empty cell centers or additional equipment claims.
-- This acceptance test is read-only and works in ephemeral CI and production.
do $density$
declare cell_count integer; source_count bigint;
begin
 if not exists(select 1 from pg_class
    where oid='public.flock_public_osm_community_density'::regclass
      and reloptions @> array['security_invoker=true']::text[])
 then raise exception 'Community map density must respect public-source RLS';end if;
 if not has_table_privilege('anon','public.flock_public_osm_community_density','SELECT')
 then raise exception 'Community aggregate unavailable to public readers';end if;
 if exists(
   select 1 from public.flock_public_osm_community_density d
   where d.community_report_count<=0
      or d.example_latitude is null or d.example_longitude is null
      or d.example_latitude<d.cell_latitude-1.5
      or d.example_latitude>=d.cell_latitude+1.5
      or d.example_longitude<d.cell_longitude-1.5
      or d.example_longitude>=d.cell_longitude+1.5
      or not exists(
        select 1 from public.flock_osm_community_points p
        where p.evidence_tier='community_osm'
          and p.latitude=d.example_latitude
          and p.longitude=d.example_longitude
      )
 ) then raise exception 'Community density cluster anchor invented or mismatched to source';end if;
 select count(*),coalesce(sum(community_report_count),0) into cell_count,source_count
 from public.flock_public_osm_community_density;
 if source_count<>(select count(*) from public.flock_osm_community_points
                   where evidence_tier='community_osm')
 then raise exception 'Community cluster totals do not match original OSM source';end if;
 if cell_count>500 then raise exception 'National OSM community cluster cap exceeded';end if;
 if exists(select 1 from public.flock_camera_locations where
     verification_method='community_osm_density_cluster')
 then raise exception 'Community aggregate falsely became a verified device';end if;
end $density$;
