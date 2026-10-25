-- 107: live source-policy suspension must instantly hide lower-confidence map pins.
-- Pub may read ONLY approved source policies, never write them or see held
-- policies. Withdrawal must remain possible even after evidence revocation.
grant select on public.flock_attributed_source_policies to anon,authenticated;
create policy source_attribution_public_approved_status_only
 on public.flock_attributed_source_policies for select
 to anon,authenticated using(policy_status='approved');
drop policy public_current_attributed_map_only
 on public.flock_source_attributed_map_points;
create policy public_current_attributed_map_only
 on public.flock_source_attributed_map_points for select
 to anon,authenticated
 using(publication_status='active'
       and source_checked_at>=now()-interval '14 days'
       and exists(select 1 from public.flock_attributed_source_policies s
                  where s.source_key=flock_source_attributed_map_points.source_key
                    and s.policy_status='approved'));
create or replace function public.guard_source_attributed_map_point()
returns trigger language plpgsql security invoker
set search_path=public,pg_temp as $$
begin
 if TG_OP='UPDATE' and new.publication_status='withdrawn'
    and old.publication_status='active'
    and new.case_key=old.case_key
    and new.source_key=old.source_key
    and new.latitude=old.latitude and new.longitude=old.longitude
    and new.source_url=old.source_url
    and new.evidence_sha256=old.evidence_sha256
 then
    return new;
 end if;
 if not exists(
   select 1 from public.flock_attributed_source_policies s
   join public.flock_point_evidence_cases c on c.case_key=new.case_key
   join public.flock_point_evidence_attestations e on e.case_key=c.case_key
   where s.source_key=new.source_key and s.policy_status='approved'
     and s.gis_layer_url=new.source_url
     and s.jurisdiction_label=new.jurisdiction_label
     and c.source_url=new.source_url and c.classification='candidate'
     and c.latitude=new.latitude and c.longitude=new.longitude
     and e.source_family=s.source_family
     and e.source_kind='government_arcgis_organization'
     and e.source_url=new.source_url
     and e.authority_url=s.original_government_url
     and e.latitude=new.latitude and e.longitude=new.longitude
     and e.evidence_sha256=new.evidence_sha256
     and e.evidence_status in ('staged','reviewed')
 ) then raise exception 'Original source attribution proof missing or changed';
 end if;
 if exists(select 1 from public.flock_camera_locations o
     where o.verification_status='verified' and o.location_accuracy='exact'
       and o.jurisdiction_label=new.jurisdiction_label
       and abs(o.latitude-new.latitude)<0.0003
       and abs(o.longitude-new.longitude)<0.0003)
 then raise exception 'Location already published through verified government tier';end if;
 return new;
end;$$;
