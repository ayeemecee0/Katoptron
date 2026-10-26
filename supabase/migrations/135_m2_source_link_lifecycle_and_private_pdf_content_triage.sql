-- 135: Source-link liveness observations and private PDF triage.
-- Source 403, timeout or changed HTML NEVER revoke a government fact.
-- An original URL appearing in a page is NOT proof of document contents.
create table if not exists public.flock_original_document_link_observations(
 government_page_url text not null check(government_page_url like 'https://%'),
 document_url text not null references public.flock_original_document_leads(document_url) on delete cascade,
 first_seen_at timestamptz not null default now(),
 last_seen_at timestamptz not null default now(),
 last_page_sha256 text not null check(last_page_sha256 ~ '^[0-9a-f]{64}$'),
 successful_absence_streak integer not null default 0 check(successful_absence_streak between 0 and 999),
 link_status text not null default 'linked_on_last_successful_scan'
  check(link_status in ('linked_on_last_successful_scan','missing_once_after_successful_scan',
     'not_linked_after_two_successful_scans')),
 primary key(government_page_url,document_url)
);
alter table public.flock_original_document_link_observations enable row level security;
revoke all on public.flock_original_document_link_observations from public,anon,authenticated;
grant select,insert,update on public.flock_original_document_link_observations to service_role;
comment on table public.flock_original_document_link_observations is
'PRIVATE hyperlink appearance history. Two missing successful government page scans show only absent link text, not policy withdrawal, contract expiry, camera revocation, or source deletion.';
insert into public.flock_original_document_link_observations
(government_page_url,document_url,first_seen_at,last_seen_at,last_page_sha256)
select government_page_url,document_url,first_seen_at,last_seen_at,source_page_sha256
from public.flock_original_document_leads
on conflict do nothing;

create or replace function public.record_original_document_link_scan(
 p_government_page_url text,p_document_urls jsonb,p_page_sha256 text
) returns void
language plpgsql security invoker set search_path = ''
as $fn$
declare n int;
begin
 if p_government_page_url not like 'https://%.gov/%'
    and p_government_page_url not like 'https://%.gov'
 then raise exception 'Invalid original government page'; end if;
 if length(p_government_page_url)>1500
    or p_page_sha256 !~ '^[0-9a-f]{64}$'
    or jsonb_typeof(p_document_urls) <> 'array'
    or jsonb_array_length(p_document_urls)>55
 then raise exception 'Invalid bounded original document scan'; end if;
 -- Fail atomically if a supplied lead was not already accepted by the
 -- current acquisition and linked from this exact original government page.
 select count(*) into n from jsonb_array_elements_text(p_document_urls) u(document_url)
 where not exists(select 1 from public.flock_original_document_leads l
   where l.document_url=u.document_url
     and l.government_page_url=p_government_page_url);
 if n>0 then raise exception 'Unindexed cross-source document reference'; end if;
 update public.flock_original_document_link_observations o
    set successful_absence_streak=least(successful_absence_streak+1,999),
        link_status=case when successful_absence_streak >= 1
          then 'not_linked_after_two_successful_scans'
          else 'missing_once_after_successful_scan' end
 where o.government_page_url=p_government_page_url
   and not exists(select 1 from jsonb_array_elements_text(p_document_urls) x(document_url)
         where x.document_url=o.document_url);
 insert into public.flock_original_document_link_observations
  (government_page_url,document_url,last_page_sha256,successful_absence_streak,link_status)
 select p_government_page_url,x.document_url,p_page_sha256,0,
        'linked_on_last_successful_scan'
 from (select distinct document_url from jsonb_array_elements_text(p_document_urls)
       x(document_url)) x
 on conflict(government_page_url,document_url) do update set
    last_seen_at=now(), last_page_sha256=excluded.last_page_sha256,
    successful_absence_streak=0,
    link_status='linked_on_last_successful_scan';
end;$fn$;
revoke all on function public.record_original_document_link_scan(text,jsonb,text)
 from public,anon,authenticated;
grant execute on function public.record_original_document_link_scan(text,jsonb,text) to service_role;

create table if not exists public.flock_original_pdf_content_triage(
 document_url text not null,
 content_sha256 text not null,
 triaged_at timestamptz not null default now(),
 pages_reported integer not null check(pages_reported between 0 and 1000),
 pages_examined integer not null check(pages_examined between 0 and 12),
 triage_status text not null check(triage_status in
  ('readable_document_indicators_only','no_extractable_text','held_parse_error','held_page_limit')),
 document_signal_flags jsonb not null default '{}'::jsonb
  check(jsonb_typeof(document_signal_flags)='object'),
 evidence_tier text not null default 'automated_private_unverified_indicators'
  check(evidence_tier='automated_private_unverified_indicators'),
 primary key(document_url,content_sha256),
 foreign key(document_url,content_sha256)
  references public.flock_original_document_pdf_receipts(document_url,content_sha256)
  on delete cascade
);
alter table public.flock_original_pdf_content_triage enable row level security;
revoke all on public.flock_original_pdf_content_triage from public,anon,authenticated;
grant select,insert,update on public.flock_original_pdf_content_triage to service_role;
comment on table public.flock_original_pdf_content_triage is
'PRIVATE bounded metadata-only PDF classification (page counts, keyword presence). Does NOT store extracted text, personal data, exact amounts, signatures, dates, votes, or evidence sufficient to publish contracts or permissions. Human original-content verification remains separate.';

alter table public.flock_original_acquisition_public_metrics
 add column if not exists pdf_content_triaged_documents integer not null
 default 0 check(pdf_content_triaged_documents >= 0);
alter table public.flock_original_acquisition_public_metrics
 add column if not exists original_links_missing_two_successful_scans integer not null
 default 0 check(original_links_missing_two_successful_scans >= 0);
comment on column public.flock_original_acquisition_public_metrics.pdf_content_triaged_documents is
'Distinct PDFs with successful automated metadata/keyword triage. Not content-level independently verified original facts.';
comment on column public.flock_original_acquisition_public_metrics.original_links_missing_two_successful_scans is
'Original document links absent from two successful current publisher page fetches. NOT withdrawn agreements, policies, permissions, or cameras.';
