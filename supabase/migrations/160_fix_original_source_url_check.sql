-- Replace invalid PostgreSQL POSIX regex {8,1400} repetition (max 255)
-- with explicit bounded character length and well-formed HTTPS token.
alter table public.flock_original_page_versions
 drop constraint if exists flock_original_page_versions_source_url_check;
alter table public.flock_original_page_versions
 add constraint flock_original_page_versions_source_url_check
 check (
   length(source_url) between 16 and 1400
   and source_url ~ '^https://[^[:space:]]+$'
 );
