-- Original government event chronology cannot be forged by public accounts.
do $milestone$
begin
 if not (select relrowsecurity from pg_class where oid='public.flock_original_civic_milestones'::regclass)
 then raise exception 'Milestones require RLS';end if;
 if has_table_privilege('anon','public.flock_original_civic_milestones','INSERT')
 or has_table_privilege('authenticated','public.flock_original_civic_milestones','UPDATE')
 or not has_table_privilege('anon','public.flock_original_civic_milestones','SELECT')
 then raise exception 'Public chronology privileges incorrect';end if;
 if not exists(select 1 from public.flock_original_civic_milestones where
 milestone_key='palo_alto_vote_2023_04_03' and event_date='2023-04-03'
 and event_type='recorded_governing_body_decision'
 and date_basis='original_city_recorded_action_date')
 then raise exception 'Original city 2023 Council decision missing or misdated';end if;
 if not exists(select 1 from public.flock_original_civic_milestones where
 milestone_key='mill_valley_suspension_2026_09_09'
 and event_date='2026-09-09'
 and date_basis='original_city_reported_effective_date')
 then raise exception 'Original government dated operational statement missing';end if;
 if not exists(select 1 from public.flock_original_civic_milestones where
 milestone_key='palo_alto_estimate_undated'
 and event_date is null and date_basis='date_not_reported'
 and amount_usd=165900 and amount_basis='government_estimate_not_executed_contract')
 then raise exception 'Source cost estimate must never become executed expense or invented date';end if;
 if exists(select 1 from public.flock_original_civic_milestones where
 event_date is null and date_basis<>'date_not_reported'
 or amount_usd is not null and amount_basis<>'government_estimate_not_executed_contract')
 then raise exception 'Chronology introduced false temporal or expenditure certainty';end if;
end $milestone$;
