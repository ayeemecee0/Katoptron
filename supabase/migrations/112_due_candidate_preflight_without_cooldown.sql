-- M2: source-change preflight separate from post-investigation cooldown.
-- The former workflow called the full lifecycle reconciler *before* triage,
-- which advanced overdue next_review_after and skipped the very sources due
-- for investigation. This function only adds new sources or reopens a genuine
-- source fingerprint/disposition change, leaving unchanged due records due.
-- No camera/source registration, GIS geometry reads or source approvals.
create or replace function public.reactivate_changed_gis_source_evidence()
returns jsonb language plpgsql security invoker
set search_path=public,pg_temp as $$
declare affected integer;
begin
 with scored as (
   select c.gis_layer_url,
     md5(concat_ws('|',c.gis_layer_url,c.layer_name,
       coalesce(c.geometry_type,''),coalesce(c.object_id_field,''),
       coalesce(c.trust_status,''),coalesce(c.public_gov_context_url,''))) hash,
     case
       when c.trust_status='rejected' then 'rejected_source'
       when exists (
         select 1 from public.trusted_flock_gis_sources t
         where t.gis_layer_url=c.gis_layer_url and t.source_status='verified'
       ) then 'resolved_existing_trusted'
       when c.gis_layer_url like '%/PeregrineWebLayers/FeatureServer/20'
          or c.gis_layer_url like '%/Flock_Cameras_-_Public/FeatureServer/0'
         then 'parked_specific_agency_evidence'
       when exists (
         select 1 from public.trusted_flock_gis_sources t
         where t.source_status='verified'
           and split_part(t.gis_layer_url,'/',3)=split_part(c.gis_layer_url,'/',3)
           and split_part(c.gis_layer_url,'/',3) not like 'services%.arcgis.com'
       ) then 'parked_same_government_jurisdiction'
       else 'investigate_original_agency'
     end disposition
   from public.flock_gis_source_candidates c
 ), described as (
   select *, case disposition
     when 'rejected_source' then 'source_rejected_by_review'
     when 'resolved_existing_trusted' then 'exact_source_already_approved'
     when 'parked_specific_agency_evidence' then 'source_layer_endorsement_not_yet_established'
     when 'parked_same_government_jurisdiction' then 'existing_host_requires_distinct_coverage_proof'
     else 'original_government_agency_link_required' end reason_code
   from scored
 ), updated as (
   insert into public.flock_gis_candidate_lifecycle
    (gis_layer_url,disposition,source_hash,reason_code,next_review_after)
   select gis_layer_url,disposition,hash,reason_code,
     case when disposition in ('resolved_existing_trusted','rejected_source') then null
       when disposition in ('parked_specific_agency_evidence',
                            'parked_same_government_jurisdiction') then now()+interval '90 days'
       else now() end
   from described
   on conflict(gis_layer_url) do update set
     source_hash=excluded.source_hash,
     disposition=excluded.disposition,
     reason_code=excluded.reason_code,
     last_classified_at=now(),
     next_review_after=case
       when excluded.disposition in ('resolved_existing_trusted','rejected_source')
         then null
       else now() end
   where public.flock_gis_candidate_lifecycle.source_hash
           is distinct from excluded.source_hash
      or public.flock_gis_candidate_lifecycle.disposition
           is distinct from excluded.disposition
   returning gis_layer_url
 )
 select count(*) into affected from updated;
 return jsonb_build_object('reactivated_or_created',affected,
   'unclassified',(select count(*) from public.flock_gis_source_candidates c
       where not exists(select 1 from public.flock_gis_candidate_lifecycle l
                        where l.gis_layer_url=c.gis_layer_url)));
end;$$;
revoke all on function public.reactivate_changed_gis_source_evidence()
 from public,anon,authenticated;
grant execute on function public.reactivate_changed_gis_source_evidence()
 to service_role;
