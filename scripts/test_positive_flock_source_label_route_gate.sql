-- Regression: route metadata must fail closed for unknown/new camera sources.
do $check$
declare
 camera_key text;
 default_expr text;
begin
 select column_default into default_expr
   from information_schema.columns
  where table_schema='public' and table_name='flock_camera_locations'
    and column_name='source_flock_label_status';
 if default_expr is null or default_expr not like '%unconfirmed%' then
   raise exception 'Future GIS imports do not default to unconfirmed source label';
 end if;
 if not exists (select 1 from pg_trigger
                 where tgrelid='public.flock_camera_locations'::regclass
                   and tgname='guard_immutable_source_flock_label_status'
                   and tgenabled='O') then
   raise exception 'Route evidence status can be modified without the owner-reviewed migration';
 end if;
 if exists (
   select 1 from public.flock_camera_locations c
   join public.trusted_flock_gis_sources s on s.gis_layer_url=c.source_url
     and s.jurisdiction_label=c.jurisdiction_label
   where c.verification_status='verified' and s.source_status='verified'
     and s.source_key='live_oak_tx'
     and c.source_flock_label_status<>'generic_lpr'
 ) then
   raise exception 'Live Oak generic LPR source must not qualify for Flock-only routes';
 end if;
 if exists (
   select 1 from public.flock_camera_locations c
   join public.trusted_flock_gis_sources s on s.gis_layer_url=c.source_url
     and s.jurisdiction_label=c.jurisdiction_label
   where c.verification_status='verified' and s.source_status='verified'
     and s.source_key in ('agency_alachua_fl','elpaso_co','lawrenceville_ga',
      'monroe_wa','newport_beach_ca','peoria_az','webster_tx')
     and c.source_flock_label_status<>'source_flock_identified'
 ) then
   raise exception 'Independently reviewed Flock GIS source failed label migration';
 end if;
 select record_key into camera_key from public.flock_camera_locations limit 1;
 if camera_key is not null then
   begin
     update public.flock_camera_locations
       set source_flock_label_status=case when source_flock_label_status='generic_lpr'
         then 'source_flock_identified' else 'generic_lpr' end
       where record_key=camera_key;
     raise exception 'Classification mutation was unexpectedly permitted';
   exception when others then
     if sqlerrm not like 'Source Flock route classification immutable:%' then
       raise;
     end if;
   end;
 end if;
end;
$check$;
