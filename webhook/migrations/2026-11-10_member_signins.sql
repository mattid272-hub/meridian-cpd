-- One row per My CPD sign-in (magic link or the order page's sign-in button), counted by
-- the daily funnel report. Written by main._record_signin; nothing reads it but the report.
-- Run once in Supabase > SQL Editor. Safe to run again.
create table if not exists public.member_signins (
  id           uuid primary key default gen_random_uuid(),
  member_id    uuid not null references public.members(id) on delete cascade,
  signed_in_at timestamptz not null default now()
);
create index if not exists idx_member_signins_at on public.member_signins (signed_in_at);
alter table public.member_signins enable row level security;
