-- Official Morehead Flock site shows maps; never infer exact camera coords.
begin;
do $$
declare checked integer;
begin
 select count(*) into checked
 from public.flock_documented_programs
 where program_key='morehead_ky'
   and record_status='verified'
   and jurisdiction_label='Morehead, KY'
   and state_code='KY'
   and reported_camera_count is null
   and official_camera_map_url=official_evidence_url
   and official_evidence_url='https://www.morehead-ky.gov/DepartmentsSubPage/5/flock-cameras'
   and official_claim_summary ilike '%not verify a complete%';
 if checked<>1 then
    raise exception 'Original Morehead municipal Flock source not strictly classified';
 end if;
 if exists(select 1 from public.flock_camera_locations
       where jurisdiction_label='Morehead, KY' and verification_status='verified')
 then raise exception 'Morehead government source programme invented exact camera pins';end if;
end $$;
rollback;
