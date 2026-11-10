-- Platform Phase 2 (favourites and read later in My CPD). Run once in Supabase → SQL
-- Editor. Safe to run again: every statement checks before it creates.
--
-- One row per member, course and kind of mark. The app reads and writes this table with
-- the service key and only ever for the signed-in member (member_id comes from the
-- session, never from the form). Until this file is run the app carries on without
-- marks: the buttons are simply not shown and nothing errors.

create table if not exists public.member_marks (
  id          uuid primary key default gen_random_uuid(),
  member_id   uuid not null references public.members(id) on delete cascade,
  course_id   text not null,
  kind        text not null check (kind in ('favourite', 'read_later')),
  created_at  timestamptz not null default now(),
  unique (member_id, course_id, kind)
);

create index if not exists idx_member_marks_member on public.member_marks (member_id);

-- The table holds per-member data: no access for the anon or authenticated roles (the app
-- uses the service key, which bypasses row level security).
alter table public.member_marks enable row level security;
