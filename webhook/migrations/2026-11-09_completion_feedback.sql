-- The optional step after completion (feedback for Meridian and the learner's reflection).
-- Run once in Supabase → SQL Editor (choose "Run and enable RLS"). Safe to run again.
-- Until it has run the app does not show the step at all, so merging first is harmless;
-- the step appears within five minutes of this running.

-- 1. Feedback for Meridian: one row per member per course. Read for the Friday review
--    (course_feedback?select=course_id,clear,useful,comment,created_at); never shown on
--    a page. clear and useful are yes | partly | no, or null if not answered.
create table if not exists public.course_feedback (
  id uuid primary key default gen_random_uuid(),
  course_id text not null,
  member_id uuid not null references public.members(id),
  completion_id uuid references public.completions(id),
  clear text check (clear in ('yes', 'partly', 'no')),
  useful text check (useful in ('yes', 'partly', 'no')),
  comment text,
  created_at timestamptz not null default now(),
  unique (member_id, course_id)
);
create index if not exists idx_course_feedback_created_at on public.course_feedback (created_at);

-- The app uses the service role key; no policies, so nothing else can read it.
alter table public.course_feedback enable row level security;

-- 2. The learner's reflection, kept on their completion record and shown to them in
--    My CPD (the course page and My certificates). One per member per course.
alter table public.completions add column if not exists reflection_learned text;
alter table public.completions add column if not exists reflection_change text;
alter table public.completions add column if not exists reflected_at timestamptz;
