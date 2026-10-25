-- M2: candidate provenance drift must reopen research immediately, not
-- bypass source approval or keep re-searching after a completed due pass.
-- Test fixture rolls back every source and lifecycle mutation.
begin;
insert into public.flock_gis_source_candidates
(gis_layer_url,layer_name,geometry_type,object_id_field,layer_purpose)
values
('https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0',
 'Flock Cameras','esriGeometryPoint','OBJECTID',
 'Private GIS evidence reactivation regression fixture');
select public.reconcile_flock_gis_candidate_lifecycle();

do $first$
declare due timestamptz;
begin
 select next_review_after into due from public.flock_gis_candidate_lifecycle
 where gis_layer_url='https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0';
 if due is null or due>now()+interval '2 minutes' then
  raise exception 'New unverified candidate not immediately actionable';
 end if;
 if exists(select 1 from public.trusted_flock_gis_sources where
    gis_layer_url='https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0')
 then raise exception 'Lifecycle research mistakenly promoted trusted GIS authority';end if;
end $first$;

-- Emulate a parked source whose government attribution has JUST changed.
update public.flock_gis_candidate_lifecycle
set next_review_after=now()+interval '90 days'
where gis_layer_url='https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0';
update public.flock_gis_source_candidates
set public_gov_context_url='https://agency.example.gov/flock-research'
where gis_layer_url='https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0';
select public.reconcile_flock_gis_candidate_lifecycle();

do $changed$
declare due timestamptz;
begin
 select next_review_after into due from public.flock_gis_candidate_lifecycle
 where gis_layer_url='https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0';
 if due is null or due>now()+interval '2 minutes'
 then raise exception 'Changed agency-link evidence did not reopen research';end if;
end $changed$;

-- Another identical reconciliation represents one completed research pass;
-- it must restore the 30-day cooldown and avoid an endless metadata loop.
select public.reconcile_flock_gis_candidate_lifecycle();
do $cooled$
declare due timestamptz;
begin
 select next_review_after into due from public.flock_gis_candidate_lifecycle
 where gis_layer_url='https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0';
 if due is null or due<now()+interval '29 days'
   or due>now()+interval '31 days'
 then raise exception 'Unchanged research lead failed to enter bounded cooldown';end if;
 if exists(select 1 from public.trusted_flock_gis_sources where
    gis_layer_url='https://services.arcgis.com/example/arcgis/rest/services/M2_Research_Test/FeatureServer/0')
 then raise exception 'Source lifecycle escalated unverified camera authority';end if;
end $cooled$;
rollback;
