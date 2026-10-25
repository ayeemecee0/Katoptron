do $$
begin
 if (select count(*) from public.flock_vendor_portal_snapshots
     where disclosure_status='verified_source_snapshot') <> 13 then
   raise exception 'Expected thirteen reviewed direct vendor snapshots';
 end if;
 if (select count(distinct state_code) from public.flock_vendor_portal_snapshots
     where disclosure_status='verified_source_snapshot') <> 5 then
   raise exception 'Expected five states of direct Flock disclosures';
 end if;
 if not exists(select 1 from public.flock_vendor_portal_snapshots
    where agency_key='trophy_club_tx_pd' and source_date='2026-07-24'
      and reported_total_cameras=10 and retention_days=30) then
   raise exception 'Texas original Flock source missing';
 end if;
 if not exists(select 1 from public.flock_vendor_portal_snapshots
    where agency_key='college_place_wa_pd' and source_date='2026-07-26'
      and reported_total_cameras=8 and reported_hotlist_hits_30d=2) then
   raise exception 'Washington original Flock source missing';
 end if;
 if not exists(select 1 from public.flock_vendor_portal_snapshots
    where agency_key='indialantic_fl_pd' and reported_total_cameras=14) then
   raise exception 'Florida original Flock source missing';
 end if;
 if not exists(select 1 from public.flock_vendor_portal_snapshots
    where agency_key='university_of_arizona_az_pd' and reported_total_cameras=59) then
   raise exception 'Arizona original Flock source missing';
 end if;
 if (select count(*) from public.flock_camera_locations
       where jurisdiction_label='Menifee, CA') <> 0 then
   raise exception 'Vendor source expansion must never authorize raw GIS candidate points';
 end if;
 raise notice 'Five-state direct-vendor disclosure and zero-camera-promotion PASS';
end $$;
