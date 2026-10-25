-- 101: Exactly one original-city-police-published Flock camera-map exception.
--
-- This does NOT weaken the existing first-party, external-endorsement or
-- per-feature-vendor policies. The city police Flock programme page directly
-- links the Live Oak Camera Map; an independent October 5 Texas Tribune report
-- identifies that exact city camera map as Flock locations. Its underlying
-- Esri Cameras/0 layer has 23 LPR Camera points with complete typed ObjectIDs,
-- but does not certify present uptime or independently label each vendor.
-- Source-specific Python verification must re-follow the exact city page ->
-- exact ArcGIS application -> exact Web Map -> exact layer and every feature.
alter table public.gis_verification_profiles
  drop constraint gis_verification_profiles_identity_mode_check;
alter table public.gis_verification_profiles
  add constraint gis_verification_profiles_identity_mode_check
  check (identity_mode in ('per_feature_vendor','official_flock_layer','municipal_public_flock_map'));

alter table public.gis_verification_profiles
  drop constraint gis_verification_profiles_service_evidence_mode_check;
alter table public.gis_verification_profiles
  add constraint gis_verification_profiles_service_evidence_mode_check
  check (service_evidence_mode in ('explicit_flock_service_text',
     'listed_flock_layer','official_program_plus_vendor','city_police_direct_map'));

alter table public.gis_verification_profiles
  drop constraint gis_verification_profiles_check;
alter table public.gis_verification_profiles
  add constraint gis_verification_profiles_check check (
    (identity_mode='per_feature_vendor'
      and vendor_field ~ '^[A-Za-z][A-Za-z0-9_]{1,50}$')
    or (identity_mode='official_flock_layer'
      and expected_layer_name ~* '^(flock[_ ]cameras( - [A-Za-z][A-Za-z ]{0,60})?|flock unit locations)$'
      and camera_id_field ~ '^[A-Za-z][A-Za-z0-9_]{1,50}$'
      and (vendor_field is null or vendor_field ~ '^[A-Za-z][A-Za-z0-9_]{1,50}$'))
    or (identity_mode='municipal_public_flock_map'
      and source_key='live_oak_tx'
      and expected_layer_name='Cameras'
      and camera_id_field='OBJECTID'
      and vendor_field='Device_Type'
      and service_evidence_mode='city_police_direct_map')
  );

insert into public.trusted_flock_gis_sources (
 source_key,gis_layer_url,government_evidence_url,jurisdiction_label,
 expected_camera_type_field,expected_id_field,bounds_south,bounds_west,
 bounds_north,bounds_east,source_status,review_basis,reviewed_at
) values (
 'live_oak_tx',
 'https://services9.arcgis.com/xdpiCgT89eSIEpbi/arcgis/rest/services/LiveOakCameras/FeatureServer/0',
 'https://www.liveoaktx.net/departments/police/flock-safety',
 'Live Oak, TX','Device_Type','OBJECTID',29.3,-98.6,29.8,-98.1,
 'verified',
 'City police Flock Safety program page directly links its original Live Oak Camera Map. The linked ArcGIS Web Map references this exact original Cameras point layer with 23 unique typed OIDs and LPR Camera features, independently rechecked in two complete snapshots. The Texas Tribune (2026-10-05) independently calls this direct city map a Flock camera location map. Per-device vendor, installation date, and uptime are not independently confirmed. Narrow source-specific revalidation is required at each publication.',
 now()
) on conflict(source_key) do nothing;

insert into public.gis_verification_profiles (
 source_key,expected_layer_name,identity_mode,vendor_field,camera_id_field,
 service_evidence_mode,profile_status,reviewed_at,review_basis
) values (
 'live_oak_tx','Cameras','municipal_public_flock_map',
 'Device_Type','OBJECTID','city_police_direct_map','verified',now(),
 'Only the exact original Live Oak police Flock webpage to named Live Oak Camera Map and immutable public ArcGIS original LPR camera source count as checked through direct linked Web Map. No generic Esri ownership or LPR-only layer qualifies. Recheck page, app, Web Map, full source IDs and geometry; source locations do not prove current uptime or per-camera manufacturer.'
) on conflict(source_key) do nothing;
