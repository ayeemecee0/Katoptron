-- 133: One authenticated original government Flock procurement decision and
-- five named roll-call votes from Bellevue ID Common Council approved minutes.
-- Source: original government council minutes, item 7(d), page 7 of 8.
-- The original heading contains an apparent 2024 typo; date is corroborated
-- by meeting body and approved April 14, 2025 footer/record.
-- A vote authorizing signing is NOT a verified executed contract, payment,
-- installed camera, active operation, or present data-sharing permission.
insert into public.flock_original_civic_milestones
(milestone_key,jurisdiction_label,event_type,event_date,date_basis,title,summary,
 source_url,amount_usd,amount_basis,source_reviewed_on)
values (
 'bellevue_id_resolution_25_11_2025_03_24',
 'Bellevue, ID','recorded_governing_body_decision','2025-03-24',
 'original_city_recorded_action_date',
 'Bellevue Common Council approved Flock Safety contract authorization, 5–0',
 'Approved March 24, 2025 council minutes, agenda item 7(d), record a five-to-zero vote authorizing the Bellevue Marshal to execute an agreement for two Flock Safety ALPR cameras with spending ceilings of $7,300 in FY2025 and $6,000 in FY2026. These figures are authorization ceilings, NOT an executed agreement amount, actual spending, camera installation or current use. Minutes were approved April 14, 2025.',
 'https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf',
 null,null,'2026-10-25'
) on conflict (milestone_key) do nothing;

-- Names grounded in same official minutes' roll call page 1 and vote page 7.
-- Do not infer how the mayor, the absent member, or other officials voted.
insert into public.flock_individual_public_positions
(position_key,person_name,office_title,jurisdiction_label,state_code,
 record_kind,recorded_position,action_date,document_reference,evidence_description,
 original_government_url,source_kind,record_status,verified_at,last_checked_at)
values
 ('bellevue_2025_25_11_bergin','Tom Bergin','Council Member',
  'Bellevue, ID','ID','individual_roll_call_vote','yes','2025-03-24',
  'Resolution 25-11; March 24, 2025 approved minutes, pp. 1 and 7',
  'The original Bellevue Common Council minutes list Tom Bergin in the meeting roll call and Council Member Bergin among the five ayes on item 7(d), a motion authorizing the Marshal to execute a Flock Safety ALPR agreement for two cameras. This is a recorded vote, not proof a contract was later executed.',
  'https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf',
  'official_government_minutes','verified',now(),now()),
 ('bellevue_2025_25_11_wrede','Suzanne Wrede','Council Member',
  'Bellevue, ID','ID','individual_roll_call_vote','yes','2025-03-24',
  'Resolution 25-11; March 24, 2025 approved minutes, pp. 1 and 7',
  'Original Bellevue Common Council minutes identify Suzanne Wrede on the roll call and Council Member Wrede as seconding and voting aye on item 7(d), authorizing the Marshal to execute a Flock Safety agreement for two ALPR cameras. No executed contract or deployment is established.',
  'https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf',
  'official_government_minutes','verified',now(),now()),
 ('bellevue_2025_25_11_shay','Diane Shay','Council President',
  'Bellevue, ID','ID','individual_roll_call_vote','yes','2025-03-24',
  'Resolution 25-11; March 24, 2025 approved minutes, pp. 1 and 7',
  'Original Bellevue Common Council minutes name Council President Diane Shay in the roll call and identify Council President Shay among five recorded ayes on Flock Safety item 7(d). The vote authorized a contract signature and limited funds, not independently verified spending or equipment.',
  'https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf',
  'official_government_minutes','verified',now(),now()),
 ('bellevue_2025_25_11_mahoney','Shaun Mahoney','Council Member',
  'Bellevue, ID','ID','individual_roll_call_vote','yes','2025-03-24',
  'Resolution 25-11; March 24, 2025 approved minutes, pp. 1 and 7',
  'Original Bellevue Common Council minutes identify Shaun Mahoney on the roll call and Council Member Mahoney in the ayes on Flock Safety resolution 25-11. The action permitted a contract but is not evidence of actual purchase, a signed agreement or installed devices.',
  'https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf',
  'official_government_minutes','verified',now(),now()),
 ('bellevue_2025_25_11_davis','Tammy E. Davis','Council Member',
  'Bellevue, ID','ID','individual_roll_call_vote','yes','2025-03-24',
  'Resolution 25-11; March 24, 2025 approved minutes, pp. 1 and 7',
  'The Bellevue Common Council original minutes show Tammy E. Davis in the roll call and record Council Member Davis moving, then voting aye, on item 7(d), authorizing the Marshal to execute an agreement with Flock Safety for two ALPR cameras. No contract execution or deployment follows from this vote alone.',
  'https://bellevueidaho.gov/wp-content/uploads/2025/04/A.-03.24.2025-Regular-Council-Meeting-Minutes.pdf',
  'official_government_minutes','verified',now(),now())
on conflict(position_key) do nothing;
