-- 125: source-authenticated, DIRECTIONAL sharing evidence without plate searches.
-- Published names cannot be promoted to verified network IDs on a city guess.
create table if not exists public.flock_original_sharing_sources (
 source_key text primary key check(source_key ~ '^[a-z0-9_-]{5,100}$'),
 source_agency_id text not null references public.flock_secondary_portal_agencies(source_agency_id),
 source_url text not null unique check(source_url ~ '^https://'),
 publisher_name text not null check(length(publisher_name) between 5 and 180),
 source_kind text not null check(source_kind in ('original_government','original_flock_vendor_portal')),
 published_at date,
 first_observed_on date not null,
 last_successfully_rechecked_at timestamptz,
 source_section text not null check(length(source_section) between 5 and 160),
 captured_scope text not null default 'published_list_excerpt' check(captured_scope in ('published_list_excerpt','complete_published_list')),
 interpretation text not null default 'publisher_listed_outbound_access_as_of_snapshot'
   check (interpretation='publisher_listed_outbound_access_as_of_snapshot'),
 check(first_observed_on<=current_date+1)
);
create index if not exists flock_original_sharing_source_agency_idx
 on public.flock_original_sharing_sources(source_agency_id);
alter table public.flock_original_sharing_sources enable row level security;
revoke all on public.flock_original_sharing_sources from public,anon,authenticated;
grant select on public.flock_original_sharing_sources to anon,authenticated;
grant all on public.flock_original_sharing_sources to service_role;
create policy flock_original_sharing_source_read
 on public.flock_original_sharing_sources for select to anon,authenticated using(true);

create table if not exists public.flock_original_sharing_edges (
 source_key text not null references public.flock_original_sharing_sources(source_key) on delete restrict,
 recipient_label text not null check(length(recipient_label) between 3 and 180),
 recipient_source_agency_id text references public.flock_secondary_portal_agencies(source_agency_id),
 identity_basis text not null check(identity_basis in ('exact_source_agency_name','unresolved_original_publisher_label')),
 first_observed_on date not null,
 source_status text not null default 'publisher_named_as_of_observation'
  check(source_status in ('publisher_named_as_of_observation','no_longer_listed','source_unavailable')),
 primary key(source_key,recipient_label),
 check((recipient_source_agency_id is null and identity_basis='unresolved_original_publisher_label') or
   (recipient_source_agency_id is not null and identity_basis='exact_source_agency_name'))
);
create index if not exists flock_original_sharing_target_idx on
 public.flock_original_sharing_edges(recipient_source_agency_id)
 where recipient_source_agency_id is not null;
alter table public.flock_original_sharing_edges enable row level security;
revoke all on public.flock_original_sharing_edges from public,anon,authenticated;
grant select on public.flock_original_sharing_edges to anon,authenticated;
grant all on public.flock_original_sharing_edges to service_role;
create policy flock_original_sharing_edge_read on public.flock_original_sharing_edges
 for select to anon,authenticated using(true);

create or replace view public.flock_public_original_sharing_evidence
 with (security_invoker=true) as
select e.source_key,s.source_agency_id,s.publisher_name,s.source_url,s.source_kind,
 s.source_section,s.captured_scope,s.published_at,s.first_observed_on as source_observed_on,
 s.last_successfully_rechecked_at,e.recipient_label,e.recipient_source_agency_id,
 e.identity_basis,e.source_status,e.first_observed_on as recipient_observed_on,
 s.interpretation
from public.flock_original_sharing_edges e
join public.flock_original_sharing_sources s on s.source_key=e.source_key;
revoke all on public.flock_public_original_sharing_evidence from public,anon,authenticated;
grant select on public.flock_public_original_sharing_evidence to anon,authenticated,service_role;

comment on view public.flock_public_original_sharing_evidence is
'Original city/vendor-hosted named outward access observations. This proves a publisher-listed permission as of a dated source observation, NOT actual searches, current permissions, reciprocal access, individually verified camera equipment or recipient ownership absent exact identity match.';
