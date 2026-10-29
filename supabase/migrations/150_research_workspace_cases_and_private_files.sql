-- 150: Private, consent-based research workspaces. No public plate, route or
-- law-enforcement search data; source records remain publicly cited separately.
create table if not exists public.research_workspaces (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null references auth.users(id) on delete cascade,
 title text not null check (char_length(title) between 3 and 120),
 created_at timestamptz not null default now()
);
create table if not exists public.research_workspace_members (
 workspace_id uuid not null references public.research_workspaces(id) on delete cascade,
 user_id uuid not null references auth.users(id) on delete cascade,
 role text not null check (role in ('editor','viewer')),
 joined_at timestamptz not null default now(),
 primary key(workspace_id,user_id)
);
create index if not exists research_workspace_members_user_idx
 on public.research_workspace_members(user_id,workspace_id);
create table if not exists public.research_cases (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references public.research_workspaces(id) on delete cascade,
 created_by uuid not null references auth.users(id) on delete cascade,
 agency_key text not null check(char_length(agency_key) between 3 and 160),
 title text not null check(char_length(title) between 4 and 180),
 description text not null default '' check(char_length(description)<=5000),
 status text not null default 'open' check(status in ('open','investigating','waiting_for_records','resolved','archived')),
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 unique(id,workspace_id)
);
create index if not exists research_cases_workspace_idx
 on public.research_cases(workspace_id,updated_at desc);
create table if not exists public.research_case_requests (
 id uuid primary key default gen_random_uuid(),
 case_id uuid not null references public.research_cases(id) on delete cascade,
 created_by uuid not null references auth.users(id) on delete cascade,
 subject text not null default 'Public records request' check(char_length(subject) between 3 and 200),
 recipient text not null default '' check(char_length(recipient)<=250),
 body text not null default '' check(char_length(body)<=18000),
 status text not null default 'draft' check(status in ('draft','sent','awaiting_response','received','closed')),
 sent_on date, response_due_on date, response_received_on date,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create index if not exists research_requests_case_idx on public.research_case_requests(case_id);
create table if not exists public.research_case_notes(
 id uuid primary key default gen_random_uuid(),
 case_id uuid not null references public.research_cases(id) on delete cascade,
 author_id uuid not null references auth.users(id) on delete cascade,
 note text not null check(char_length(note) between 1 and 5000),
 source_url text check(source_url is null or (source_url ~ '^https://[^[:space:]]{5,1400}$')),
 created_at timestamptz not null default now()
);
create index if not exists research_case_notes_case_idx on public.research_case_notes(case_id,created_at desc);
create table if not exists public.research_case_files (
 id uuid primary key default gen_random_uuid(),
 case_id uuid not null references public.research_cases(id) on delete cascade,
 uploaded_by uuid not null references auth.users(id) on delete cascade,
 storage_path text not null unique check(char_length(storage_path) between 15 and 500),
 filename text not null check(char_length(filename) between 1 and 180),
 file_size integer not null check(file_size between 1 and 10485760),
 created_at timestamptz not null default now()
);
create index if not exists research_files_case_idx on public.research_case_files(case_id);

