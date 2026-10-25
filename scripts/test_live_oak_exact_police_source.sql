-- Exact reviewed Live Oak city Flock-map source exception cannot be reused by
-- a random Esri layer or app. Existing official GIS policies are unaffected.
begin;
do $$
declare n integer;
begin
 select count(*) into n
 from public.trusted_flock_gis_sources s
 join public.gis_verification_profiles p using(source_key)
 where s.source_key='live_oak_tx'
   and s.source_status='verified' and p.profile_status='verified'
   and s.gis_layer_url='https://services9.arcgis.com/xdpiCgT89eSIEpbi/arcgis/rest/services/LiveOakCameras/FeatureServer/0'
   and s.government_evidence_url='https://www.liveoaktx.net/departments/police/flock-safety'
   and s.jurisdiction_label='Live Oak, TX'
   and p.identity_mode='municipal_public_flock_map'
   and p.service_evidence_mode='city_police_direct_map'
   and p.expected_layer_name='Cameras'
   and p.camera_id_field='OBJECTID' and p.vendor_field='Device_Type';
 if n<>1 then raise exception 'Reviewed city-map source not bound exactly';end if;
 if (select count(*) from public.gis_verification_profiles
     where identity_mode='municipal_public_flock_map')<>1 then
   raise exception 'City map authority exception not unique';
 end if;
 begin
   insert into public.gis_verification_profiles (
      source_key,expected_layer_name,identity_mode,vendor_field,camera_id_field,
      service_evidence_mode,profile_status,review_basis)
   values('unrelated_agency','Cameras','municipal_public_flock_map',
      'Device_Type','OBJECTID','city_police_direct_map','verified',
      repeat('Unauthorized copied camera GIS exception.',3));
   raise exception 'Wrong jurisdiction inherited municipal map trust';
 exception when check_violation then null;
 end;
end;
$$;
rollback;
