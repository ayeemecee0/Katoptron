-- 131: Flock-only simulated route evidence needs a positive source-level
-- Flock designation. Government-mapped generic LPR != Flock-labeled GIS.
-- A source label does NOT independently establish manufacturer serials,
-- camera uptime or plate reads. New source imports fail closed by default.
alter table public.flock_camera_locations
  add column if not exists source_flock_label_status text not null
  default 'unconfirmed'
  check (source_flock_label_status in
   ('source_flock_identified','generic_lpr','unconfirmed'));

comment on column public.flock_camera_locations.source_flock_label_status is
'Flock-only route screening: original GIS explicitly identifies the source point as Flock (source_flock_identified), government GIS says generic LPR (generic_lpr), or original camera-level evidence not established (unconfirmed). Not per-device manufacturer, operation or detection proof. New imports default unconfirmed and require separate owner-reviewed evidence.';

-- Backfill ONLY the 7 already independently reviewed Flock-named GIS layers.
-- Do not infer equipment identities from agency-level Flock agreements.
update public.flock_camera_locations c
   set source_flock_label_status = 'source_flock_identified'
  from public.trusted_flock_gis_sources s
 where c.source_url=s.gis_layer_url
   and c.jurisdiction_label=s.jurisdiction_label
   and s.source_status='verified'
   and c.verification_status='verified'
   and s.source_key in (
     'agency_alachua_fl','elpaso_co','lawrenceville_ga',
     'monroe_wa','newport_beach_ca','peoria_az','webster_tx');

-- City of Live Oak publishes the precise locations as generic 'LPR Camera'.
-- Flock program linkage is not source proof of individual Flock hardware.
update public.flock_camera_locations c
   set source_flock_label_status = 'generic_lpr'
  from public.trusted_flock_gis_sources s
 where c.source_url=s.gis_layer_url
   and c.jurisdiction_label=s.jurisdiction_label
   and s.source_status='verified'
   and c.verification_status='verified'
   and s.source_key='live_oak_tx';

-- Classification is an owner-reviewed evidentiary assertion. Scheduled
-- service-role rechecks may update freshness or revoke sources, but cannot
-- silently promote a generic/unknown position to Flock-labeled route evidence.
create or replace function public.guard_immutable_source_flock_label_status()
returns trigger language plpgsql set search_path = '' as $guard$
begin
 if new.source_flock_label_status is distinct from old.source_flock_label_status then
   raise exception 'Source Flock route classification immutable: owner-reviewed evidence migration required';
 end if;
 return new;
end;
$guard$;
revoke all on function public.guard_immutable_source_flock_label_status() from public,anon,authenticated;
drop trigger if exists guard_immutable_source_flock_label_status
  on public.flock_camera_locations;
create trigger guard_immutable_source_flock_label_status
before update of source_flock_label_status on public.flock_camera_locations
for each row execute function public.guard_immutable_source_flock_label_status();
