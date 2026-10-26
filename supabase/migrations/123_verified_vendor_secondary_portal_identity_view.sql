-- 123: First-party Flock portal <> licensed secondary network crosswalk.
-- This corroborates identity OF THE PORTAL, NOT the agency's physical camera
-- locations, equipment operation, or actual recipient queries.
create or replace view public.flock_public_portal_identity_matches
with (security_invoker=true) as
select v.agency_key as first_party_agency_key,
       v.agency_label as first_party_agency_label,
       v.portal_url as first_party_portal_url,
       v.source_date as first_party_source_date,
       p.source_agency_id,
       p.agency_name as secondary_agency_name,
       p.portal_slug as secondary_portal_slug,
       p.state_code,
       p.source_snapshot_at as secondary_source_snapshot_at,
       p.source_reported_network_links as secondary_reported_network_links,
       'original_flock_portal_slug_exact'::text as match_basis,
       'portal_identity_only_not_government_authority_or_camera_verification'::text as evidence_boundary
from public.flock_vendor_portal_snapshots v
join public.flock_secondary_portal_agencies p
 on p.portal_slug=split_part(trim(trailing '/' from v.portal_url),'/',4)
 and p.is_reporting_portal
 and p.state_code=v.state_code
where v.disclosure_status='verified_source_snapshot'
  and v.portal_url ~ '^https://transparency[.]flocksafety[.]com/[a-z0-9-]+/?$'
  and p.source_tier='secondary_aggregated_portal_snapshot';
revoke all on public.flock_public_portal_identity_matches from public,anon,authenticated;
grant select on public.flock_public_portal_identity_matches to anon,authenticated,service_role;
comment on view public.flock_public_portal_identity_matches is
'Links exact vendor Flock transparency portal URL slugs to EyesOnFlock network identities where state matches. Does not prove a municipal government is the operator, camera manufacturer, current location or recipient searches.';
