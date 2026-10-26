-- M6 original government statement date is publication, not termination.
do $check$
begin
 if not exists(select 1 from public.flock_original_civic_milestones where
 milestone_key='salem_ma_flock_nonrenewal_statement_2026_07_23'
 and jurisdiction_label='Salem, MA'
 and event_type='government_disclosure_publication'
 and event_date='2026-07-23'
 and date_basis='original_city_reported_publication_date'
 and amount_usd is null and amount_basis is null
 and source_url='https://www.salemma.gov/m/NewsFlash/Home/Detail/427'
 and summary like '%NOT establish the actual contract expiration day%') then
 raise exception 'Salem original statement incorrectly dated or upgraded to executed contract';
 end if;
 if not exists(select 1 from public.flock_original_civic_milestones
  where milestone_key='bellevue_id_resolution_25_11_2025_03_24'
    and event_date='2025-03-24' and date_basis='original_city_recorded_action_date'
    and amount_usd is null) then
  raise exception 'Bellevue original government authorization not source-qualified';
 end if;
 if (select count(*) from public.flock_individual_public_positions
  where position_key like 'bellevue_2025_25_11_%' and record_status='verified') <> 5 then
  raise exception 'Bellevue source-named votes missing';
 end if;
 if has_table_privilege('anon','public.flock_original_civic_milestones','UPDATE')
 or has_table_privilege('authenticated','public.flock_individual_public_positions','INSERT') then
  raise exception 'Unreviewed user can edit original government accountability facts';
 end if;
end $check$;
