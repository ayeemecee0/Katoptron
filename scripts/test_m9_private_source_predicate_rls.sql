-- Release acceptance: privileged source-authority functions are not
-- callable as public RPCs, yet public GIS RLS still returns the same points.
do $policy$
begin
 if has_function_privilege('anon','public.gis_camera_authority_current(text,text)','EXECUTE')
 or has_function_privilege('authenticated','public.gis_camera_authority_current(text,text)','EXECUTE')
 or has_function_privilege('anon','public.is_current_flock_polygon_camera_gis_source(text)','EXECUTE')
 or has_function_privilege('authenticated','public.is_current_flock_polygon_camera_gis_source(text)','EXECUTE')
 then raise exception 'Old publicly callable SECURITY DEFINER authority RPC remains exposed';end if;
 if not has_function_privilege('anon',
 'katoptron_internal.gis_camera_authority_current(text,text)','EXECUTE')
 or not has_function_privilege('authenticated',
 'katoptron_internal.is_current_flock_polygon_camera_gis_source(text)','EXECUTE')
 then raise exception 'Reader RLS internal authority gate not executable';end if;
 if (select count(*) from pg_policies where schemaname='public'
 and tablename in ('flock_camera_locations','flock_documented_coverage_areas')
 and qual like '%katoptron_internal.%')<>2
 then raise exception 'Public source RLS policies no longer reference internal evidence authority';end if;
 if (select count(*) from pg_proc p where p.pronamespace='public'::regnamespace
 and p.prosecdef and has_function_privilege('anon',p.oid,'EXECUTE'))<>0
 then raise exception 'Public SECURITY DEFINER function remains callable by anon';end if;
end $policy$;

begin;
set local role anon;
do $anon$
declare exact_points integer;
begin
 select count(*) into exact_points from public.flock_camera_locations
 where verification_status='verified' and location_accuracy='exact';
 if exact_points>=200 and exact_points<293 then
  raise exception 'M9 RLS source relocation silently removed government camera coverage';end if;
 if exact_points<>(
    select count(*) from public.flock_camera_locations
    where verification_status='verified' and location_accuracy='exact'
      and source_url like 'https://%')
 then raise exception 'Public camera evidence lost source provenance';end if;
end $anon$;
reset role;
rollback;
