-- 102: Private independently attributed original-government ArcGIS map applications.
-- A city link to an ArcGIS app is a DISCOVERY LEAD only, not a government
-- verification of the app's underlying FeatureServers or exact camera points.
create table if not exists public.flock_government_camera_map_app_leads (
 government_page_url text not null check(government_page_url ~ '^https://[A-Za-z0-9.-]+/'),
 app_url text not null check(app_url ~ '^https://[A-Za-z0-9-]+[.]maps[.]arcgis[.]com/apps/'),
 arcgis_app_id text not null check(arcgis_app_id ~ '^[a-f0-9]{32}$'),
 agency_page_sha256 text not null check(agency_page_sha256 ~ '^[a-f0-9]{64}$'),
 arcgis_item_type text not null check(arcgis_item_type in ('Web Map','Web Mapping Application','Web Experience','Dashboard','StoryMap')),
 evidence_status text not null default 'unreviewed'
    check(evidence_status in ('unreviewed','held','reviewed','rejected')),
 first_seen_at timestamptz not null default now(),
 last_checked_at timestamptz not null default now(),
 primary key(government_page_url,app_url)
);
alter table public.flock_government_camera_map_app_leads enable row level security;
revoke all on public.flock_government_camera_map_app_leads
 from public,anon,authenticated,service_role;
grant select on public.flock_government_camera_map_app_leads to service_role;
grant insert(government_page_url,app_url,arcgis_app_id,agency_page_sha256,arcgis_item_type)
 on public.flock_government_camera_map_app_leads to service_role;
grant update(last_checked_at,evidence_status,agency_page_sha256)
 on public.flock_government_camera_map_app_leads to service_role;
comment on table public.flock_government_camera_map_app_leads is
'PRIVATE original city Flock disclosure map application leads. App provenance does not authorize its location layer or individual camera manufacturer.';

create table if not exists public.flock_government_camera_map_app_receipts (
 government_page_url text not null,
 app_url text not null,
 agency_page_sha256 text not null check(agency_page_sha256 ~ '^[a-f0-9]{64}$'),
 observed_at timestamptz not null default now(),
 primary key(government_page_url,app_url,agency_page_sha256),
 foreign key (government_page_url,app_url)
   references public.flock_government_camera_map_app_leads(government_page_url,app_url)
);
alter table public.flock_government_camera_map_app_receipts enable row level security;
revoke all on public.flock_government_camera_map_app_receipts
 from public,anon,authenticated,service_role;
grant select,insert on public.flock_government_camera_map_app_receipts to service_role;
comment on table public.flock_government_camera_map_app_receipts is
'Private immutable exact original government Flock page evidence digests by linked map app.';
