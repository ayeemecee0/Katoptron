-- 129: narrowly reviewed original-government timeline examples.
-- Do not convert an inferred day, estimated amount, city council agenda
-- listing, or camera map link into an executed contract or adoption date.
create table if not exists public.flock_original_civic_milestones (
 milestone_key text primary key check(length(milestone_key) between 8 and 120),
 jurisdiction_label text not null check(length(jurisdiction_label) between 5 and 150),
 event_type text not null check(event_type in
 ('recorded_governing_body_decision','agency_reported_operational_change',
  'government_disclosure_publication','government_reported_estimate')),
 event_date date,
 date_basis text not null check(date_basis in
 ('original_city_recorded_action_date','original_city_reported_effective_date',
  'original_city_reported_publication_date','date_not_reported')),
 title text not null check(length(title) between 6 and 250),
 summary text not null check(length(summary) between 20 and 1600),
 source_url text not null check(source_url like 'https://%'),
 amount_usd numeric check(amount_usd is null or amount_usd>=0),
 amount_basis text check(amount_basis is null or amount_basis='government_estimate_not_executed_contract'),
 evidence_tier text not null default 'original_government_reviewed'
  check(evidence_tier='original_government_reviewed'),
 source_reviewed_on date not null,
 check((event_date is null)=(date_basis='date_not_reported')),
 check(amount_usd is null or amount_basis='government_estimate_not_executed_contract')
);
alter table public.flock_original_civic_milestones enable row level security;
revoke all on public.flock_original_civic_milestones from public,anon,authenticated;
grant select on public.flock_original_civic_milestones to anon,authenticated;
grant all on public.flock_original_civic_milestones to service_role;
create policy flock_original_civic_milestones_read
 on public.flock_original_civic_milestones for select to anon,authenticated using (true);

insert into public.flock_original_civic_milestones
(milestone_key,jurisdiction_label,event_type,event_date,date_basis,title,summary,
 source_url,amount_usd,amount_basis,source_reviewed_on)
values
 ('palo_alto_vote_2023_04_03','Palo Alto, CA','recorded_governing_body_decision','2023-04-03',
  'original_city_recorded_action_date',
  'Palo Alto council voted 7–0 to approve ALPR implementation',
  'The city police public information portal reports that its City Council voted 7–0 on April 3, 2023, to approve ALPR implementation. The recorded council vote is a governance event, not proof that a camera was installed or activated on that date.',
  'https://www.paloalto.gov/Departments/Police/Public-Information-Portal/Automated-License-Plate-Recognition-ALPR',
  null,null,'2026-10-25'),
 ('palo_alto_logs_2026_04_21','Palo Alto, CA','government_disclosure_publication','2026-04-21',
  'original_city_reported_publication_date',
  'Palo Alto initially published partially redacted Flock search logs',
  'The city police portal states that it initially posted partially redacted Flock search logs on April 21, 2026. This dates publication of audit material, not the date of any particular individual ALPR search.',
  'https://www.paloalto.gov/Departments/Police/Public-Information-Portal/Automated-License-Plate-Recognition-ALPR',
  null,null,'2026-10-25'),
 ('palo_alto_estimate_undated','Palo Alto, CA','government_reported_estimate',null,
  'date_not_reported','Palo Alto published a three-year Flock cost estimate',
  'The original city police FAQ reports estimated three-year Flock ALPR costs of approximately $165,900, including described fiscal-year allocations. The city webpage does not establish a signed-contract date for this figure; it is not an authenticated executed agreement or verified actual expenditure.',
  'https://www.paloalto.gov/Departments/Police/Public-Information-Portal/Automated-License-Plate-Recognition-ALPR',
  165900,'government_estimate_not_executed_contract','2026-10-25'),
 ('mill_valley_suspension_2026_09_09','Mill Valley, CA','agency_reported_operational_change','2026-09-09',
  'original_city_reported_effective_date',
  'Mill Valley reported disabling its Flock ALPR and live-feed cameras',
  'An original Mill Valley Police Department statement says both ALPR and live-feed cameras have been disabled since September 9, 2026, because the city suspended use after concerns about enforceable data-control protections. This is a government statement of operational status, not a confirmed physical equipment removal or independently observed access revocation.',
  'https://millvalleypolice.gov/m/newsflash/home/detail/1639',
  null,null,'2026-10-25')
on conflict(milestone_key) do nothing;
