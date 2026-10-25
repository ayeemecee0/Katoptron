-- M2 evidence-driven discovery reactivation; no trust grant or camera publication.
-- Existing lifecycle hash previously omitted government attribution, schema,
-- and status metadata; a newly discovered source link could sit untouched for
-- 30 days. Hash changes now re-open immediately. Following an actual due
-- research pass, the next scheduled reconciliation restores its cooldown.
-- A one-time review is expected because stored historical hashes change.
create or replace function public.reconcile_flock_gis_candidate_lifecycle()
returns jsonb language plpgsql security invoker
set search_path = public,pg_temp as $$
declare updated_count integer;
begin
 with scored as (
  select c.gis_layer_url, md5(concat_ws('|',c.gis_layer_url,c.layer_name,
       coalesce(c.geometry_type,''),coalesce(c.object_id_field,''),
       coalesce(c.trust_status,''),coalesce(c.public_gov_context_url,''))) hash,
    case
      when c.trust_status='rejected' then 'rejected_source'
      when exists(select 1 from public.trusted_flock_gis_sources t
                  where t.gis_layer_url=c.gis_layer_url and t.source_status='verified')
           then 'resolved_existing_trusted'
      when c.gis_layer_url like '%/PeregrineWebLayers/FeatureServer/20'
        or c.gis_layer_url like '%/Flock_Cameras_-_Public/FeatureServer/0'
           then 'parked_specific_agency_evidence'
      when exists(select 1 from public.trusted_flock_gis_sources t
           where t.source_status='verified'
           and split_part(t.gis_layer_url,'/',3)=split_part(c.gis_layer_url,'/',3)
           and split_part(c.gis_layer_url,'/',3) not like 'services%.arcgis.com')
           then 'parked_same_government_jurisdiction'
      else 'investigate_original_agency'
    end as disposition
  from public.flock_gis_source_candidates c
 ), described as (
  select *, case disposition
    when 'rejected_source' then 'source_rejected_by_review'
    when 'resolved_existing_trusted' then 'exact_source_already_approved'
    when 'parked_specific_agency_evidence' then 'source_layer_endorsement_not_yet_established'
    when 'parked_same_government_jurisdiction' then 'existing_host_requires_distinct_coverage_proof'
    else 'original_government_agency_link_required' end as reason_code
  from scored
 ), merged as (
  insert into public.flock_gis_candidate_lifecycle
    (gis_layer_url,disposition,source_hash,reason_code,next_review_after)
  select gis_layer_url,disposition,hash,reason_code,
    case when disposition in ('resolved_existing_trusted','rejected_source') then null
      when disposition in ('parked_specific_agency_evidence',
                           'parked_same_government_jurisdiction') then now()+interval '90 days'
      else now() end
  from described
  on conflict(gis_layer_url) do update set
    disposition=excluded.disposition,
    source_hash=excluded.source_hash,
    reason_code=excluded.reason_code,
    last_classified_at=now(),
    next_review_after=case
      when excluded.disposition in ('resolved_existing_trusted','rejected_source')
        then null
      when public.flock_gis_candidate_lifecycle.source_hash<>excluded.source_hash
        or public.flock_gis_candidate_lifecycle.disposition<>excluded.disposition
        then now()
      when public.flock_gis_candidate_lifecycle.next_review_after is null
        or public.flock_gis_candidate_lifecycle.next_review_after<=now()
        then case when excluded.disposition in
           ('parked_specific_agency_evidence','parked_same_government_jurisdiction')
             then now()+interval '90 days'
             else now()+interval '30 days' end
      else public.flock_gis_candidate_lifecycle.next_review_after end
  returning gis_layer_url
 )
 select count(*) into updated_count from merged;
 return jsonb_build_object('classified',updated_count,
  'unclassified',(select count(*) from public.flock_gis_source_candidates c
                  where not exists(select 1 from public.flock_gis_candidate_lifecycle x
                                   where x.gis_layer_url=c.gis_layer_url)));
end;$$;

