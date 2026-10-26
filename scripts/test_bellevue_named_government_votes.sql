-- M6: Original Bellevue council roll-call and authorization claims only.
do $m6$
declare n integer;
begin
 if (select count(*) from public.flock_individual_public_positions
       where position_key like 'bellevue_2025_25_11_%')<>5 then
   raise exception 'Exactly five primary-source named votes should exist for Bellevue item 7(d)';
 end if;
 if (select count(*) from public.flock_individual_public_positions
       where position_key like 'bellevue_2025_25_11_%'
         and record_status='verified' and action_date='2025-03-24'
         and state_code='ID' and recorded_position='yes'
         and record_kind='individual_roll_call_vote'
         and source_kind='official_government_minutes'
         and document_reference like '%pp. 1 and 7%'
         and original_government_url =
           'https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf'
       )<>5 then
   raise exception 'Bellevue names/vote dates/primary minutes receipt mismatch';
 end if;
 if not exists(select 1 from public.flock_original_civic_milestones
   where milestone_key='bellevue_id_resolution_25_11_2025_03_24'
     and jurisdiction_label='Bellevue, ID'
     and event_type='recorded_governing_body_decision'
     and event_date='2025-03-24'
     and amount_usd is null
     and amount_basis is null
     and summary like '%NOT an executed agreement amount%') then
   raise exception 'Bellevue financial authorization confused with executed Flock contract';
 end if;
 if exists(select 1 from public.contracts c where lower(c.summary) like '%bellevue%'
   and c.review_status='published') then
   raise exception 'Bellevue procurement authority wrongly became executed signed agreement';
 end if;
 if has_table_privilege('anon','public.flock_individual_public_positions','INSERT')
 or has_table_privilege('service_role','public.flock_individual_public_positions','INSERT')
 or has_table_privilege('authenticated','public.flock_individual_public_positions','UPDATE') then
   raise exception 'Unreviewed user or automation can self-certify politician vote';
 end if;
end $m6$;
begin;
set local role anon;
do $m6$
begin
 if (select count(*) from public.flock_individual_public_positions
 where position_key like 'bellevue_2025_25_11_%')<>5 then
  raise exception 'Named government roll-call rows not visible to public';
 end if;
end $m6$;
rollback;
