-- M2 preflight regression. Everything is rolled back, including the
-- temporary public-ish GIS candidate. There is zero camera publication.
begin;
insert into public.flock_gis_source_candidates
 (gis_layer_url,layer_name,geometry_type,object_id_field,layer_purpose)
values
 ('https://services.arcgis.com/example/arcgis/rest/services/M2_Preflight_Test/FeatureServer/0',
  'Flock Cameras','esriGeometryPoint','OBJECTID',
  'Private source-change preflight verification regression fixture');

select public.reactivate_changed_gis_source_evidence();
do $new_lead$
declare due timestamptz;
begin
 select next_review_after into due from public.flock_gis_candidate_lifecycle
 where gis_layer_url like '%/M2_Preflight_Test/FeatureServer/0';
 if due is null or due>now()+interval '2 minutes'
 then raise exception 'New original-agency research source not due immediately';end if;
end $new_lead$;

-- The prior bug: a due source was moved 30 days forward before triage.
select public.reactivate_changed_gis_source_evidence();
do $still_due$
declare due timestamptz;
begin
 select next_review_after into due from public.flock_gis_candidate_lifecycle
 where gis_layer_url like '%/M2_Preflight_Test/FeatureServer/0';
 if due is null or due>now()+interval '2 minutes'
 then raise exception 'M2 preflight illegally delayed an unchanged overdue source';end if;
end $still_due$;

-- Only after a completed triage pass does the full reconciler set cooldown.
select public.reconcile_flock_gis_candidate_lifecycle();
do $cooldown$
declare due timestamptz;
begin
 select next_review_after into due from public.flock_gis_candidate_lifecycle
 where gis_layer_url like '%/M2_Preflight_Test/FeatureServer/0';
 if due not between now()+interval '29 days' and now()+interval '31 days'
 then raise exception 'M2 post-triage cooldown not applied';end if;
end $cooldown$;

-- A genuinely NEW government source relationship makes a fresh lead due now.
update public.flock_gis_source_candidates
 set public_gov_context_url='https://agency.example.gov/flock-layer-review'
 where gis_layer_url like '%/M2_Preflight_Test/FeatureServer/0';
select public.reactivate_changed_gis_source_evidence();
do $changed$
declare due timestamptz;
begin
 select next_review_after into due from public.flock_gis_candidate_lifecycle
 where gis_layer_url like '%/M2_Preflight_Test/FeatureServer/0';
 if due is null or due>now()+interval '2 minutes'
 then raise exception 'M2 new agency link did not reopen the research source';end if;
 if exists(select 1 from public.trusted_flock_gis_sources
           where gis_layer_url like '%/M2_Preflight_Test/FeatureServer/0')
 then raise exception 'M2 research preflight illegally created trusted source';end if;
end $changed$;
rollback;
