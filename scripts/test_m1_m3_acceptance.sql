-- M1/M3 acceptance: fail closed on schema security and source-identity drift.
-- Zero mutations. Safe in disposable CI and directly against production.
do $m1m3$
begin
 if exists(
   select 1 from pg_class c
   where c.relnamespace='public'::regnamespace
     and c.relkind='r' and not c.relrowsecurity
 ) then
   raise exception 'M1: public table without RLS';
 end if;

 if not exists (
   select 1 from pg_indexes where schemaname='public'
    and tablename='flock_gis_point_case_dispositions'
    and indexname='flock_gis_disposition_original_public_fk_idx'
 )
 or not exists (
   select 1 from pg_indexes where schemaname='public'
    and tablename='flock_source_attributed_map_points'
    and indexname='flock_attributed_point_source_fk_idx'
 ) then
   raise exception 'M1: missing evidence-provenance foreign-key index';
 end if;

 if has_table_privilege('anon','public.trusted_flock_gis_sources','UPDATE')
  or has_table_privilege('authenticated','public.trusted_flock_gis_sources','INSERT')
  or has_table_privilege('anon','public.flock_gis_candidate_lifecycle','SELECT')
  or has_table_privilege('authenticated','public.flock_point_evidence_attestations','INSERT')
  or has_table_privilege('anon','public.flock_source_attributed_map_points','UPDATE')
  or has_table_privilege('authenticated','public.flock_attributed_source_policies','UPDATE')
 then
   raise exception 'M1: public source trust or private evidence permission regression';
 end if;

 if not exists(select 1 from pg_class where oid='public.flock_public_tiered_camera_points'::regclass
     and 'security_invoker=true'=any(reloptions)) then
   raise exception 'M3: public evidence view bypasses RLS';
 end if;

 if not exists (select 1 from pg_policies
      where schemaname='public' and tablename='flock_camera_locations'
      and cmd='SELECT' and qual ilike '%gis_camera_authority_current%') then
   raise exception 'M3: original source revocation filter missing';
 end if;

 if not exists (select 1 from pg_policies
      where schemaname='public' and tablename='flock_source_attributed_map_points'
      and cmd='SELECT' and qual ilike '%policy_status%'
      and qual ilike '%source_checked_at%') then
   raise exception 'M3: unconfirmed source revocation/expiry gate missing';
 end if;

 if exists (
    select 1 from public.flock_source_attributed_map_points p
    join public.flock_camera_locations c
    on c.verification_status='verified'
      and c.location_accuracy='exact'
      and c.jurisdiction_label=p.jurisdiction_label
      and abs(c.latitude-p.latitude)<0.0003
      and abs(c.longitude-p.longitude)<0.0003
    where p.publication_status='active'
 ) then
   raise exception 'M3: lower tier duplicates verified government point';
 end if;
end $m1m3$;

-- A new authenticated SECURITY DEFINER API requires explicit release review.
-- The existing reviewer RPCs check auth.uid() and their role/owner allowlists;
-- the two source-status booleans intentionally serve public RLS.
do $privileged_authenticated$
declare fn record;
 total integer;
begin
 select count(*) into total from pg_proc
 where pronamespace='public'::regnamespace and prosecdef
   and has_function_privilege('authenticated',oid,'EXECUTE');
 if total > 13 or total <> (
   select count(distinct proname) from pg_proc
   where pronamespace='public'::regnamespace and prosecdef
     and has_function_privilege('authenticated',oid,'EXECUTE')
 ) then
    raise exception 'M1: unreviewed or overloaded authenticated privileged RPC';
 end if;
 for fn in
   select proname, pg_get_function_identity_arguments(oid) as args, prosrc,
      oid::regprocedure::text as signature
   from pg_proc
   where pronamespace='public'::regnamespace and prosecdef
     and has_function_privilege('authenticated',oid,'EXECUTE')
 loop
   if fn.proname not in (
     'community_report_attachment_paths','editorial_decide',
     'editorial_evidence_ref','editorial_general_decide',
     'editorial_general_list','editorial_history','editorial_list',
     'editorial_session','gis_camera_authority_current',
     'is_current_flock_polygon_camera_gis_source',
     'list_community_review_queue','set_community_review_status',
     'withdraw_own_community_report'
   ) then raise exception 'M1: unreviewed authenticated privileged RPC %',fn.signature;end if;
   if fn.proname = 'set_community_review_status'
     and fn.args <> 'p_id uuid, p_status text, p_note text' then
     raise exception 'M1: legacy unlogged community review RPC re-enabled';
   end if;
   if fn.proname not in ('gis_camera_authority_current',
     'is_current_flock_polygon_camera_gis_source')
     and fn.prosrc not ilike '%auth.uid%' then
     raise exception 'M1: privileged authenticated RPC has no UID gate: %',fn.signature;
   end if;
 end loop;
end $privileged_authenticated$;
