-- 119: preserve original-source-derived access-list fingerprints independently of
-- counts. A changed fingerprint indicates DIFFERENT LISTED RECIPIENT IDS in a
-- dated SECONDARY network snapshot. It cannot establish actual searches,
-- current access, installations or any physical camera coordinates.
alter table public.flock_secondary_portal_agencies
 add column if not exists sharing_list_sha256 text
 check (sharing_list_sha256 is null or sharing_list_sha256 ~ '^[0-9a-f]{64}$');

create or replace view public.flock_public_signed_contract_end_dates
with (security_invoker=true) as
select c.id::text as contract_key,
 (coalesce(j.name,ag.name,'Agency name not documented')||
    case when j.state_code is null then '' else ', '||j.state_code end)::text as jurisdiction_label,
 j.state_code::text as state_code,
 c.contract_number::text as contract_number,
 c.signed_on::date as signed_on,c.ends_on::date as ends_on,
 c.amount_usd::numeric as amount_usd,
 c.summary::text as summary,s.url::text as source_url
from public.published_contracts c
join public.sources s on s.id=c.source_id and s.status='verified' and s.url like 'https://%'
left join public.agencies ag on ag.id=c.agency_id
left join public.jurisdictions j on j.id=ag.jurisdiction_id
where c.review_status='published' and c.vendor ilike '%flock%'
  and c.signed_on is not null and c.ends_on is not null;
revoke all on public.flock_public_signed_contract_end_dates from public,anon,authenticated;
grant select on public.flock_public_signed_contract_end_dates to anon,authenticated,service_role;
comment on view public.flock_public_signed_contract_end_dates is
'Only signed reviewed contract source end-dates; contract expiry does not establish automatic renewal. Identity might lack jurisdiction code.';

-- Ensure notifications are never conflated with observed user movement or
-- plate reads; only source-qualified structural evidence is eligible.
