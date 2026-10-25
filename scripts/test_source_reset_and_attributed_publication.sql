-- Fail-closed RLS + source-tier publication acceptance in a rolled-back fixture.
begin;
do $$
begin
 if not (select relrowsecurity from pg_class where oid='public.flock_gis_candidate_lifecycle'::regclass)
   or not (select relrowsecurity from pg_class where oid='public.flock_gis_point_case_dispositions'::regclass)
   or not (select relrowsecurity from pg_class where oid='public.flock_source_attributed_map_points'::regclass)
 then raise exception 'Source reset private/public ledgers not protected by RLS';end if;
 if has_table_privilege('anon','public.flock_gis_candidate_lifecycle','SELECT')
   or has_table_privilege('authenticated','public.flock_gis_point_case_dispositions','SELECT')
   or has_table_privilege('anon','public.flock_attributed_source_policies','SELECT')
   or has_table_privilege('service_role','public.flock_attributed_source_policies','UPDATE')
 then raise exception 'GIS source authority or evidence queue disclosed or writable';end if;
 if has_function_privilege('anon','public.reconcile_flock_gis_candidate_lifecycle()','EXECUTE')
   or has_function_privilege('authenticated','public.reconcile_flock_gis_point_case_dispositions()','EXECUTE')
 then raise exception 'Untrusted client can alter private GIS dispositions';end if;
 if not ('security_invoker=true'=any((select reloptions from pg_class
                 where oid='public.flock_public_tiered_camera_points'::regclass)))
 then raise exception 'Public tiered view lost invoker RLS';end if;
end $$;
-- A staged *separately published* source observation must stay outside official rows.
insert into public.flock_point_evidence_cases
(case_key,label,jurisdiction_label,latitude,longitude,evidence_summary,source_url)
values('tier_test_source_ledger_001','Civic map source test','Shelbyville, TN',
35.5,-86.5,'Test source-only place, not a verified active camera installation.',
'https://services3.arcgis.com/0Uo0Kvp9YTHRegvR/arcgis/rest/services/Flock_Cameras_-_Public/FeatureServer/0');
insert into public.flock_point_evidence_attestations
(evidence_key,case_key,source_kind,source_family,source_url,authority_url,
latitude,longitude,evidence_sha256,source_excerpt)
values('proof_test_source_ledger_001','tier_test_source_ledger_001',
'government_arcgis_organization','shelbyville.municipal.arcgis',
'https://services3.arcgis.com/0Uo0Kvp9YTHRegvR/arcgis/rest/services/Flock_Cameras_-_Public/FeatureServer/0',
'https://test.shelbyvilletn.org/planning-community-development/',
35.5,-86.5,repeat('a',64),
'The original city links an independently matching Esri organization, not an installed camera proof.');
insert into public.flock_source_attributed_map_points
(case_key,source_key,label,jurisdiction_label,latitude,longitude,source_url,
evidence_sha256,source_checked_at,publication_status,caveat)
values('tier_test_source_ledger_001','shelbyville_arcgis_affiliation',
'City-associated GIS observation','Shelbyville, TN',35.5,-86.5,
'https://services3.arcgis.com/0Uo0Kvp9YTHRegvR/arcgis/rest/services/Flock_Cameras_-_Public/FeatureServer/0',
repeat('a',64),now(),'active',
'City publisher-affiliated GIS observation, NOT a verified Flock installation, camera identity or currently active device. Do not count as a government-approved hardware record.');
set local role anon;
do $$
begin
 if (select count(*) from public.flock_public_tiered_camera_points
     where case_key='tier_test_source_ledger_001'
       and evidence_tier='source_attributed_unconfirmed')<>1
 then raise exception 'Source-attributed tier not publicly visible to anon';end if;
 if exists(select 1 from public.flock_public_tiered_camera_points
   where case_key='tier_test_source_ledger_001' and evidence_tier='government_verified')
 then raise exception 'Lower-confidence source promoted to government-verified';end if;
end $$;
reset role;
update public.flock_source_attributed_map_points
 set source_checked_at=now()-interval '16 days'
 where case_key='tier_test_source_ledger_001';
set local role anon;
do $$
begin
 if exists(select 1 from public.flock_public_tiered_camera_points
 where case_key='tier_test_source_ledger_001')
 then raise exception 'Stale source-attributed point did not automatically expire';end if;
end $$;
reset role;
rollback;
