-- Source portal identity evidence tier audit (read-only).
do $$
begin
 if not exists(
   select 1 from pg_class where oid='public.flock_public_portal_identity_matches'::regclass
    and reloptions @> ARRAY['security_invoker=true']::text[]
 ) then raise exception 'Agency portal crosswalk view does not respect caller RLS'; end if;
 if not has_table_privilege('anon','public.flock_public_portal_identity_matches','SELECT')
 then raise exception 'Public portal identity evidence is not accessible'; end if;
 if exists(
   select 1 from public.flock_public_portal_identity_matches m
   where m.match_basis<>'original_flock_portal_slug_exact'
    or m.first_party_portal_url not like 'https://transparency.flocksafety.com/%'
    or m.evidence_boundary<>'portal_identity_only_not_government_authority_or_camera_verification'
    or m.secondary_portal_slug<>split_part(trim(trailing '/' from m.first_party_portal_url),'/',4)
 ) then raise exception 'Portal crosswalk lost exact first-party source URL qualification'; end if;
end $$;
