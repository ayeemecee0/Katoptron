-- 100: Current government-confirmed hyperlinks to vendor transparency portals.
-- This is a PUBLIC DIRECTORY OF LINKS, never a count of hardware or location.
-- Only a rechecked exact link on an already verified original govt programme
-- document qualifies. Entry disappears on revocation or expiry after 30 days.
create table if not exists public.flock_government_vendor_directory (
 program_key text not null references public.flock_documented_programs(program_key),
 portal_url text not null check (
  portal_url ~ '^https://transparency\.flocksafety\.com/[a-z0-9-]+$'),
 government_page_sha256 text not null
  check (government_page_sha256 ~ '^[0-9a-f]{64}$'),
 checked_at timestamptz not null default now(),
 link_status text not null default 'direct_government_link'
  check (link_status in ('direct_government_link','withdrawn')),
 first_seen_at timestamptz not null default now(),
 primary key(program_key,portal_url),
 constraint vendor_link_check_time check (checked_at<=now()+interval '1 hour')
);
create index if not exists flock_government_vendor_directory_live_idx
 on public.flock_government_vendor_directory(checked_at desc)
 where link_status='direct_government_link';
alter table public.flock_government_vendor_directory enable row level security;
revoke all on public.flock_government_vendor_directory
 from public,anon,authenticated,service_role;
grant select on public.flock_government_vendor_directory to anon,authenticated,service_role;
grant insert (program_key,portal_url,government_page_sha256,checked_at,link_status)
 on public.flock_government_vendor_directory to service_role;
grant update (government_page_sha256,checked_at,link_status)
 on public.flock_government_vendor_directory to service_role;
create policy published_current_government_vendor_direct_links
 on public.flock_government_vendor_directory for select to anon,authenticated
 using (link_status='direct_government_link'
        and checked_at>=now()-interval '30 days');
create or replace view public.flock_public_government_vendor_directory
 with (security_invoker=true) as
select d.program_key,p.jurisdiction_label,p.state_code,p.program_status,
       p.source_date as government_document_date,
       p.official_evidence_url as original_government_url,
       d.portal_url,d.checked_at,
       'government_page_direct_vendor_portal_link'::text as source_tier
from public.flock_government_vendor_directory d
join public.flock_documented_programs p using(program_key)
where p.record_status='verified'
  and d.link_status='direct_government_link'
  and d.checked_at>=now()-interval '30 days';
revoke all on public.flock_public_government_vendor_directory
 from public,anon,authenticated,service_role;
grant select on public.flock_public_government_vendor_directory
 to anon,authenticated,service_role;
comment on view public.flock_public_government_vendor_directory is
'Government page directly links a Flock vendor transparency portal, rechecked within 30 days. Link presence only, NOT original-government verification of manufacturer camera count, positions or operational status.';
