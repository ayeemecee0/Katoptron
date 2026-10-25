-- 097: Durable ODbL source ID proximity candidates; these are NOT adjudicated duplicates.
-- Snapshot rows are staged unpublished. Each candidate becomes publicly
-- visible ONLY after a complete upload is checked and published_at is set.
create table if not exists public.flock_osm_nearby_snapshots (
 snapshot_id text primary key check (snapshot_id ~ '^[0-9a-f]{64}$'),
 source_snapshot_date date not null,
 algorithm text not null default 'osm-nearby-distinct-coordinates-15m-v1'
   check (algorithm='osm-nearby-distinct-coordinates-15m-v1'),
 source_observations integer not null check(source_observations between 90000 and 200000),
 pair_count integer not null check(pair_count between 0 and 250000),
 source_records_in_pairs integer not null check(source_records_in_pairs between 0 and source_observations),
 pairs_within_5m integer not null check(pairs_within_5m between 0 and pair_count),
 pairs_5_to_15m integer not null check(pairs_5_to_15m between 0 and pair_count),
 source_license text not null default 'ODbL 1.0' check(source_license='ODbL 1.0'),
 evidence_tier text not null default 'possible_osm_proximity'
   check(evidence_tier='possible_osm_proximity'),
 published_at timestamptz,
 staged_at timestamptz not null default now(),
 constraint exact_nearby_distance_bands check (pairs_within_5m+pairs_5_to_15m=pair_count)
);
create index if not exists flock_osm_nearby_snapshot_published_idx
 on public.flock_osm_nearby_snapshots(source_snapshot_date desc,published_at desc)
 where published_at is not null;
alter table public.flock_osm_nearby_snapshots enable row level security;
revoke all on public.flock_osm_nearby_snapshots from public,anon,authenticated,service_role;
grant select on public.flock_osm_nearby_snapshots to anon,authenticated,service_role;
grant insert(snapshot_id,source_snapshot_date,source_observations,pair_count,
 source_records_in_pairs,pairs_within_5m,pairs_5_to_15m)
 on public.flock_osm_nearby_snapshots to service_role;
grant update(published_at) on public.flock_osm_nearby_snapshots to service_role;
create policy public_complete_osm_nearby_snapshots
 on public.flock_osm_nearby_snapshots for select to anon,authenticated
 using (published_at is not null and evidence_tier='possible_osm_proximity');

create table if not exists public.flock_osm_nearby_candidates (
 snapshot_id text not null references public.flock_osm_nearby_snapshots(snapshot_id),
 osm_key_a text not null check (osm_key_a ~ '^(node|way)/[1-9][0-9]{0,17}$'),
 osm_key_b text not null check (osm_key_b ~ '^(node|way)/[1-9][0-9]{0,17}$'),
 distance_m numeric(5,2) not null check (distance_m > 0 and distance_m <= 15),
 source_tier text not null default 'possible_osm_proximity'
   check(source_tier='possible_osm_proximity'),
 primary key (snapshot_id,osm_key_a,osm_key_b),
 constraint pair_ordering_check check(osm_key_a < osm_key_b)
);
create index if not exists flock_osm_nearby_b_source_idx
 on public.flock_osm_nearby_candidates (snapshot_id,osm_key_b);
alter table public.flock_osm_nearby_candidates enable row level security;
revoke all on public.flock_osm_nearby_candidates from public,anon,authenticated,service_role;
grant select on public.flock_osm_nearby_candidates to anon,authenticated,service_role;
grant insert(snapshot_id,osm_key_a,osm_key_b,distance_m)
 on public.flock_osm_nearby_candidates to service_role;
create policy public_published_osm_nearby_candidates
 on public.flock_osm_nearby_candidates for select to anon,authenticated
 using (source_tier='possible_osm_proximity' and exists (
   select 1 from public.flock_osm_nearby_snapshots s
   where s.snapshot_id=flock_osm_nearby_candidates.snapshot_id
   and s.published_at is not null
 ));

create or replace view public.flock_public_osm_nearby_latest
 with (security_invoker=true) as
select snapshot_id,source_snapshot_date,source_observations,pair_count,
 source_records_in_pairs,pairs_within_5m,pairs_5_to_15m,
 source_license,algorithm,published_at
from public.flock_osm_nearby_snapshots
where published_at is not null
order by source_snapshot_date desc,published_at desc limit 1;
revoke all on public.flock_public_osm_nearby_latest from public,anon,authenticated,service_role;
grant select on public.flock_public_osm_nearby_latest to anon,authenticated,service_role;

create or replace view public.flock_public_osm_nearby_search
 with (security_invoker=true) as
select c.osm_key_a,c.osm_key_b,c.distance_m,
       c.snapshot_id,s.source_snapshot_date,
       c.source_tier
from public.flock_osm_nearby_candidates c
join public.flock_public_osm_nearby_latest s on s.snapshot_id=c.snapshot_id;
revoke all on public.flock_public_osm_nearby_search from public,anon,authenticated,service_role;
grant select on public.flock_public_osm_nearby_search to anon,authenticated,service_role;

comment on table public.flock_osm_nearby_snapshots is
'Immutable ODbL proximity audit metadata; candidate rows are hidden until full upload is checked and published. Not camera hardware deduplication.';
comment on table public.flock_osm_nearby_candidates is
'Distinct OSM node/way keys within 15m at different coordinates. Proximity does not prove common hardware, deployment, or status. Never delete canonical or community camera source observations based on these candidates.';
