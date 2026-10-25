-- 103: Morehead Police publish Flock programme and camera-location map imagery.
-- This is jurisdiction-level original-government evidence only. Do not create
-- individual GPS pins from regional screenshots, or count vendor totals as
-- individually verified cameras.
insert into public.flock_documented_programs (
 program_key,jurisdiction_label,state_code,program_status,official_evidence_url,
 official_claim_summary,source_date,reported_camera_count,record_status,
 reviewed_at,official_camera_map_url
) values (
 'morehead_ky','Morehead, KY','KY','documented_at_source_date',
 'https://www.morehead-ky.gov/DepartmentsSubPage/5/flock-cameras',
 'Morehead Police original government Flock Safety camera program webpage describes the agency camera network, 2025-2026 programme audit resources, a vendor transparency portal, and published original-government camera-location map images for downtown Morehead, Rowan County and North End. This record documents the program and a city map resource only. It does not verify a complete or current individually georeferenced camera inventory.',
 '2026-10-25',null,'verified',now(),
 'https://www.morehead-ky.gov/DepartmentsSubPage/5/flock-cameras'
) on conflict(program_key) do nothing;
