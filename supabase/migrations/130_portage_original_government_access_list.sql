-- 130: Source-specific Portage (IN) government statement, as observed.
-- City characterizes the seven named organizations as "Federal entities".
-- Publisher text is preserved verbatim; none is automatically promoted to a
-- federal agency classification or an active/current search permission.
insert into public.flock_original_sharing_sources
(source_key,source_agency_id,source_url,publisher_name,source_kind,
 first_observed_on,source_section,captured_scope)
values
('portage_in_original_government','portage-in-pd',
 'https://portagein.gov/547/Flock-Information-Center',
 'City of Portage Police Department, Indiana','original_government',
 '2026-10-25','Who has access to the data?','published_list_excerpt')
on conflict(source_key) do nothing;

with originals(name) as (
 values
 ('NICTD (Northern Indiana Commuter Transportation District – Transit Police)'),
 ('NCMEC (National Center for Missing and Exploited Children)'),
 ('U.S. Marshals'),
 ('FBI (Federal Bureau of Investigation)'),
 ('NPS (National Park Service - Indiana Dunes)'),
 ('Veterans Affairs PD'),
 ('U.S. Postal Service Inspections Services')
), resolved as(
 select originals.name,
 (select case when count(*)=1 then min(p.source_agency_id) end
  from public.flock_secondary_portal_agencies p
  where p.agency_name=originals.name) matched_id
 from originals
)
insert into public.flock_original_sharing_edges
(source_key,recipient_label,recipient_source_agency_id,identity_basis,
 first_observed_on)
select 'portage_in_original_government',name,matched_id,
 case when matched_id is null then 'unresolved_original_publisher_label'
 else 'exact_source_agency_name' end,'2026-10-25'
from resolved
on conflict(source_key,recipient_label) do nothing;

update public.flock_original_acquisition_public_metrics
 set verified_original_sharing_edges=(select count(*) from public.flock_original_sharing_edges),
 verified_original_publishers=(select count(*) from public.flock_original_sharing_sources),
 updated_at=now()
 where metric_date=current_date;
