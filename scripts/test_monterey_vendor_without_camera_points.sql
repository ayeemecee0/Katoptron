-- M2 source-specific evidence: original Flock portal is an agency-level
-- dated snapshot of LPR plus other types, never GPS camera coordinates.
do $monterey$
begin
 if (select count(*) from public.flock_vendor_portal_snapshots
    where disclosure_status='verified_source_snapshot') <> 14 then
    raise exception 'M2 new first-party vendor source failed 14-agency reconciliation';
 end if;
 if not exists(select 1 from public.flock_vendor_portal_snapshots
   where agency_key='monterey_ca_pd' and agency_label='Monterey CA PD'
     and state_code='CA' and source_date='2026-07-24'
     and portal_url='https://transparency.flocksafety.com/monterey-ca-pd'
     and reported_total_cameras=37 and
         camera_count_scope='lpr_and_other_cameras'
     and retention_days=30 and reported_search_sessions_30d=113
     and reported_hotlist_hits_30d=1752 and
         reported_vehicle_detections_30d=499980)
   then raise exception 'M2 original Monterey Flock portal data missing or relabeled';end if;
 if (select count(distinct agency_key) from public.flock_vendor_portal_snapshots
    where state_code='CA' and disclosure_status='verified_source_snapshot') <> 10
   then raise exception 'M2 state-level vendor agency coverage not updated';end if;
 if exists(select 1 from public.flock_camera_locations
     where jurisdiction_label='Monterey, CA')
   then raise exception 'M2 original agency snapshot illegally generated GIS camera records';end if;
 if not (select relrowsecurity from pg_class
   where oid='public.flock_vendor_portal_snapshots'::regclass)
   then raise exception 'M2 vendor portal RLS disabled';end if;
end $monterey$;
