-- 122: bounded per-agency retention history for public Agency X-Ray.
-- The underlying append-only source history grows weekly; returning all
-- archived snapshots would eventually truncate paginated browser reads.
-- Keep three latest source observations per agency for comparison. View runs
-- with caller's RLS permissions, and excludes no agency in the registry.
create or replace view public.flock_public_agency_retention_recent
with (security_invoker=true) as
select source_agency_id,observed_on,retention_days,portal_slug,
       source_url,evidence_tier
from (
 select r.*,
 row_number() over(partition by source_agency_id order by observed_on desc) as rn
 from public.flock_secondary_portal_retention_history r
) r where rn <= 3;
revoke all on public.flock_public_agency_retention_recent from public,anon,authenticated;
grant select on public.flock_public_agency_retention_recent to anon,authenticated,service_role;
comment on view public.flock_public_agency_retention_recent is
'Latest three source-dated EyesOnFlock SECONDARY retention observations per known agency; not current source-authoritative Flock retention policy.';
