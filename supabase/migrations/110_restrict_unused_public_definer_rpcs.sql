-- M1: reduce the externally callable SECURITY DEFINER RPC surface.
-- The verified-contract URL predicate is referenced only inside an owner-run
-- protected trigger; the legacy area predicate has no current RLS/view use.
-- Preserve service-role and owner execution. Do NOT revoke the two public
-- source predicates required by RLS (gis_camera_authority_current,
-- is_current_flock_polygon_camera_gis_source).
revoke execute on function public.is_current_government_document_url(text,text,text)
 from public,anon,authenticated;
revoke execute on function public.official_flock_area_source_is_current(text)
 from public,anon,authenticated;
grant execute on function public.is_current_government_document_url(text,text,text)
 to service_role;
grant execute on function public.official_flock_area_source_is_current(text)
 to service_role;
