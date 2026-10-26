-- Disposable PostgreSQL CI shim ONLY, never apply to Supabase production.
-- Production has Supabase Storage's real objects catalog. This isolated CI
-- database intentionally lacks Storage and must still test M5's SQL
-- erasure precondition without weakening its production implementation.
create schema if not exists storage;
create table if not exists storage.buckets(
 id text primary key,
 public boolean not null default false
);
insert into storage.buckets(id,public)
 values('katoptron-community-evidence',false)
 on conflict(id) do nothing;
create table if not exists storage.objects(
  id uuid primary key default gen_random_uuid(),
  bucket_id text not null,
  name text not null,
  owner uuid,
  owner_id text,
  metadata jsonb not null default '{}'::jsonb,
  unique(bucket_id,name)
);
