-- 091: Research leads from agency-owned Flock disclosures that directly link
-- the vendor portal. This DOES NOT scrape Flock, approve values or create pins.
create table if not exists public.flock_vendor_portal_source_leads (
  government_source_url text not null check (
    government_source_url ~ '^https://[A-Za-z0-9.-]+/' and
    length(government_source_url) <= 1600),
  portal_url text not null check (
    portal_url ~ '^https://transparency[.]flocksafety[.]com/[a-z0-9-]+/?$'
    and length(portal_url) <= 250),
  government_page_sha256 text not null check (
    government_page_sha256 ~ '^[a-f0-9]{64}$'),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','approved_for_research','rejected')),
  first_seen_at timestamptz not null default now(),
  primary key (government_source_url,portal_url)
);
alter table public.flock_vendor_portal_source_leads enable row level security;
revoke all on public.flock_vendor_portal_source_leads from
  public,anon,authenticated,service_role;
grant select on public.flock_vendor_portal_source_leads to service_role;
grant insert(government_source_url,portal_url,government_page_sha256)
 on public.flock_vendor_portal_source_leads to service_role;
comment on table public.flock_vendor_portal_source_leads is
'PRIVATE original agency webpage -> Flock vendor portal hyperlink leads. No implied metric verification or source review. No publicly readable rows. Vendor website scraping is not part of this discovery process.';
