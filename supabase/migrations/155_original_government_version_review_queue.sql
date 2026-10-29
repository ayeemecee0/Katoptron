-- Source change intelligence is PRIVATE until an original-page editorial recheck.
-- HTML or CSS changes are never assumed to be new laws, spending or equipment.
create table if not exists public.flock_original_page_versions(
 source_id text not null check(length(source_id) between 5 and 180),
 source_url text not null check(source_url ~ '^https://[^[:space:]]{8,1400}$'),
 locality_key text not null check(length(locality_key) between 4 and 160),
 source_date text not null check(length(source_date) between 7 and 10),
 text_sha256 text not null check(text_sha256 ~ '^[0-9a-f]{64}$'),
 anchor_context_sha256 text not null check(anchor_context_sha256 ~ '^[0-9a-f]{64}$'),
 first_seen_at timestamptz not null default now(),
 last_seen_at timestamptz not null default now(),
 primary key(source_id,text_sha256)
);
create index if not exists flock_original_page_version_recent_idx on public.flock_original_page_versions(source_id,last_seen_at desc);
create table if not exists public.flock_original_page_review_queue(
 source_id text not null,
 previous_sha256 text not null check(previous_sha256 ~ '^[0-9a-f]{64}$'),
 current_sha256 text not null check(current_sha256 ~ '^[0-9a-f]{64}$'),
 locality_key text not null,
 source_url text not null,
 change_scope text not null check(change_scope in ('anchor_context_changed','publisher_page_text_changed')),
 status text not null default 'needs_original_editorial_review'
   check(status in ('needs_original_editorial_review','dismissed_non_substantive','independently_verified')),
 reviewed_by uuid references auth.users(id),
 reviewed_at timestamptz,
 created_at timestamptz not null default now(),
 primary key(source_id,current_sha256),
 check(previous_sha256<>current_sha256),
 check((status='independently_verified' and reviewed_by is not null and reviewed_at is not null)
       or status<>'independently_verified')
);
alter table public.flock_original_page_versions enable row level security;
alter table public.flock_original_page_review_queue enable row level security;
revoke all on public.flock_original_page_versions,public.flock_original_page_review_queue from public,anon,authenticated;
grant select,insert,update on public.flock_original_page_versions to service_role;
grant select,insert on public.flock_original_page_review_queue to service_role;
comment on table public.flock_original_page_review_queue is
 'Fingerprint change alert for qualified government publication; NOT a verified substantive policy, operational or financial change; cannot generate Watch mail.';
