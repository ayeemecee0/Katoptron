-- M3 core source-tier and source-freshness acceptance. No new cameras.
do $m3$
declare
 v_official integer;
 v_flock integer;
 v_generic integer;
begin
 select count(*) filter(where c.verification_status='verified'),
        count(*) filter(where c.verification_status='verified' and
          c.source_flock_label_status='source_flock_identified'),
        count(*) filter(where c.verification_status='verified' and
          c.source_flock_label_status='generic_lpr')
 into v_official,v_flock,v_generic
 from public.flock_camera_locations c;
 if v_official < 316 or v_flock < 293 or v_generic < 23 then
   raise exception 'M3 originally accepted source-tier baseline unexpectedly reduced';
 end if;
 if exists(
  select 1 from public.flock_camera_locations c
  left join public.trusted_flock_gis_sources s on s.gis_layer_url=c.source_url
    and s.jurisdiction_label=c.jurisdiction_label and s.source_status='verified'
  where c.verification_status='verified'
    and (s.source_key is null
      or c.location_accuracy <> 'exact'
      or c.source_type <> 'official_government'
      or c.verification_method <> 'official_georeferenced_camera_record_v1'
      or c.evidence_sha256 !~ '^[a-f0-9]{64}$'
      or c.last_source_recheck_at is null
      or c.last_source_recheck_at < now() - interval '365 days'
      or c.last_source_recheck_at > now() + interval '10 minutes'
      or (c.source_flock_label_status='source_flock_identified'
          and s.source_key not in (
           'agency_alachua_fl','elpaso_co','lawrenceville_ga','monroe_wa',
           'newport_beach_ca','peoria_az','webster_tx'))
      or (s.source_key='live_oak_tx'
          and (c.source_flock_label_status <> 'generic_lpr'
            or c.evidence_summary not like '%NOT per-device manufacturer%'))
      or (s.source_key in (
           'agency_alachua_fl','elpaso_co','lawrenceville_ga','monroe_wa',
           'newport_beach_ca','peoria_az','webster_tx')
          and c.source_flock_label_status <> 'source_flock_identified'))
 ) then raise exception 'M3 primary-source identity, freshness or Flock label classification invalid';end if;
 if exists(
  select 1 from public.flock_source_attributed_map_points p
  left join public.flock_attributed_source_policies s on
    s.source_key=p.source_key and s.policy_status='approved'
  where p.publication_status='active'
   and (s.source_key is null or s.gis_layer_url<>p.source_url
        or s.jurisdiction_label<>p.jurisdiction_label
        or p.source_checked_at is null
        or p.source_checked_at < now() - interval '14 days'
        or p.source_checked_at > now() + interval '10 minutes')
 ) then raise exception 'M3 source-attributed provisional evidence stale or unapproved';end if;
 if has_table_privilege('anon','public.flock_point_evidence_attestations','SELECT')
    or has_table_privilege('authenticated','public.flock_point_evidence_attestations','UPDATE')
    or has_table_privilege('anon','public.flock_gis_candidate_lifecycle','SELECT')
 then raise exception 'M3 private source evidence available to public';end if;
 if not exists (select 1 from pg_trigger where
    tgrelid='public.flock_camera_locations'::regclass
    and tgname='guard_m3_positive_source_label_on_insert'
    and tgenabled='O') then
    raise exception 'M3 automated positive GIS source-label insert guard disabled';end if;
end $m3$;

-- Rollback-only negative proof: service_role must be unable to bootstrap a
-- "Flock-labeled" position even from an already approved camera's coordinates.
-- No transaction is committed; never alters the canonical inventory.
begin;
set local role service_role;
do $negative$
begin
 begin
  insert into public.flock_camera_locations
  (record_key,label,jurisdiction_label,latitude,longitude,
   location_accuracy,uncertainty_radius_m,source_type,source_url,
   evidence_summary,evidence_sha256,verification_method,
   first_documented_on,last_confirmed_on,verification_status,
   last_source_recheck_at,source_flock_label_status)
  select 'm3-test-untrusted-label-'||substr(md5(random()::text),1,8),
   label,jurisdiction_label,latitude,longitude,
   location_accuracy,uncertainty_radius_m,source_type,source_url,
   evidence_summary,evidence_sha256,verification_method,
   first_documented_on,last_confirmed_on,verification_status,
   now(),'source_flock_identified'
  from public.flock_camera_locations where record_key=
    (select record_key from public.flock_camera_locations
     where source_flock_label_status='source_flock_identified' limit 1);
  raise exception 'Automated importer incorrectly assigned Flock-positive label';
 exception when others then
  if sqlerrm not like 'Automated GIS imports cannot certify Flock manufacturer/source labels%' then
   raise;
  end if;
 end;
end $negative$;
reset role;
rollback;
