-- 106: separate low-confidence, source-attributed PUBLIC map layer.
-- Only city-affiliated GIS source observations, never claims of active or
-- manufacturer-confirmed Flock devices. Explicit owner-reviewed source policy.
create table if not exists public.flock_attributed_source_policies(
 source_key text primary key,
 gis_layer_url text not null unique,
 original_government_url text not null,
 source_family text not null,
 jurisdiction_label text not null,
 attribution_class text not null check(attribution_class='city_publisher_associated'),
 approved_at timestamptz not null default now(),
 policy_status text not null check(policy_status in ('approved','suspended'))
);
alter table public.flock_attributed_source_policies enable row level security;
revoke all on public.flock_attributed_source_policies from public,anon,authenticated,service_role;
grant select on public.flock_attributed_source_policies to service_role;
-- Narrow audited source scope. Municipality page independently links a Web
-- Map sharing the exact Esri org with the explicitly titled Flock point layer.
-- This does NOT say the police approved each installed/current camera.
insert into public.flock_attributed_source_policies
(source_key,gis_layer_url,original_government_url,source_family,
 jurisdiction_label,attribution_class,policy_status)
values
('shelbyville_arcgis_affiliation',
 'https://services3.arcgis.com/0Uo0Kvp9YTHRegvR/arcgis/rest/services/Flock_Cameras_-_Public/FeatureServer/0',
 'https://test.shelbyvilletn.org/planning-community-development/',
 'shelbyville.municipal.arcgis','Shelbyville, TN',
 'city_publisher_associated','approved')
on conflict(source_key) do nothing;

create table if not exists public.flock_source_attributed_map_points(
 case_key text primary key references public.flock_point_evidence_cases(case_key),
 source_key text not null references public.flock_attributed_source_policies(source_key),
 label text not null,
 jurisdiction_label text not null,
 latitude double precision not null check(latitude between 17 and 72),
 longitude double precision not null check(longitude between -180 and -64),
 source_url text not null,
 evidence_sha256 text not null check(evidence_sha256~'^[0-9a-f]{64}$'),
 source_checked_at timestamptz not null,
 publication_status text not null check(publication_status in ('active','withdrawn')),
 caveat text not null check(length(caveat) between 80 and 900),
 first_published_at timestamptz not null default now(),
 constraint attributed_source_no_future check(source_checked_at<=now()+interval '1 hour')
);
create index if not exists attributed_map_visible_idx on
 public.flock_source_attributed_map_points(source_checked_at desc)
 where publication_status='active';
alter table public.flock_source_attributed_map_points enable row level security;
revoke all on public.flock_source_attributed_map_points from public,anon,authenticated;
grant select on public.flock_source_attributed_map_points to anon,authenticated,service_role;
grant insert,update on public.flock_source_attributed_map_points to service_role;
create policy public_current_attributed_map_only
 on public.flock_source_attributed_map_points for select to anon,authenticated
 using (publication_status='active'
        and source_checked_at>=now()-interval '14 days'
        and exists(select 1 from public.flock_attributed_source_policies p
          where p.source_key=source_key and p.policy_status='approved'));
-- To read the owner-only policy through RLS, replace it with a stable
-- public-status denormalized trusted fixed snapshot in the guarded writer.
drop policy public_current_attributed_map_only on public.flock_source_attributed_map_points;
create policy public_current_attributed_map_only
 on public.flock_source_attributed_map_points for select to anon,authenticated
 using(publication_status='active' and source_checked_at>=now()-interval '14 days');
create or replace function public.guard_source_attributed_map_point()
returns trigger language plpgsql security invoker
set search_path=public,pg_temp as $$
begin
 if not exists(
   select 1 from public.flock_attributed_source_policies s
   join public.flock_point_evidence_cases c on c.case_key=new.case_key
   join public.flock_point_evidence_attestations e on e.case_key=c.case_key
   where s.source_key=new.source_key and s.policy_status='approved'
     and s.gis_layer_url=new.source_url
     and s.jurisdiction_label=new.jurisdiction_label
     and c.source_url=new.source_url
     and c.classification='candidate'
     and c.latitude=new.latitude and c.longitude=new.longitude
     and e.source_family=s.source_family
     and e.source_kind='government_arcgis_organization'
     and e.source_url=new.source_url
     and e.authority_url=s.original_government_url
     and e.latitude=new.latitude and e.longitude=new.longitude
     and e.evidence_sha256=new.evidence_sha256
     and e.evidence_status in ('staged','reviewed')
 ) then
   raise exception 'Original source attribution proof missing or changed';
 end if;
 if exists (select 1 from public.flock_camera_locations o
    where o.verification_status='verified' and o.location_accuracy='exact'
     and o.jurisdiction_label=new.jurisdiction_label
     and abs(o.latitude-new.latitude)<0.0003
     and abs(o.longitude-new.longitude)<0.0003)
 then raise exception 'Location already published through verified government tier';end if;
 return new;
end;$$;
revoke all on function public.guard_source_attributed_map_point()
 from public,anon,authenticated;
create trigger guarded_attributed_source_publication
 before insert or update on public.flock_source_attributed_map_points
 for each row execute function public.guard_source_attributed_map_point();

-- Invoker view: each source family retains its own explicit confidence tier;
-- the existing independently reviewed evidence view remains unmodified in spirit.
create or replace view public.flock_public_tiered_camera_points
 with(security_invoker=true) as
select c.case_key,c.label,c.jurisdiction_label,c.latitude,c.longitude,
 c.classification as evidence_tier,c.evidence_summary,c.source_url,
 c.reviewed_at as published_at
from public.flock_point_evidence_cases c
where c.classification in ('government_verified','independently_corroborated')
union all
select p.case_key,p.label,p.jurisdiction_label,p.latitude,p.longitude,
 'source_attributed_unconfirmed'::text as evidence_tier,
 p.caveat as evidence_summary,p.source_url,p.source_checked_at as published_at
from public.flock_source_attributed_map_points p
where p.publication_status='active' and p.source_checked_at>=now()-interval '14 days';
revoke all on public.flock_public_tiered_camera_points
 from public,anon,authenticated;
grant select on public.flock_public_tiered_camera_points to anon,authenticated;
comment on table public.flock_source_attributed_map_points is
'Public city-publisher-associated Flock-labeled source positions. NOT independently government-endorsed exact camera inventory, active device, or manufacturer certification.';
